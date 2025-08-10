import surrealdb
import time
import logging
import re
import urllib.parse
from typing import Dict, Optional, Any, Type, Union, Protocol, runtime_checkable, List, Tuple, Callable
from abc import ABC, abstractmethod
from queue import Queue, Empty
from threading import Lock, Event
import asyncio
from .schemaless import SurrealEngine

# Set up logging
logger = logging.getLogger(__name__)

class ConnectionPoolBase(ABC):
    """Base class for connection pools.

    This abstract class defines the common interface and functionality for
    both synchronous and asynchronous connection pools.

    Attributes:
        url: The URL of the SurrealDB server
        namespace: The namespace to use
        database: The database to use
        username: The username for authentication
        password: The password for authentication
        pool_size: Maximum number of connections in the pool
        max_idle_time: Maximum time in seconds a connection can be idle before being closed
        connect_timeout: Timeout in seconds for establishing a connection
        operation_timeout: Timeout in seconds for operations
        retry_limit: Maximum number of retries for failed operations
        retry_delay: Initial delay in seconds between retries
        retry_backoff: Backoff multiplier for retry delay
        validate_on_borrow: Whether to validate connections when borrowing from the pool
    """

    def __init__(self, 
                 url: str, 
                 namespace: Optional[str] = None, 
                 database: Optional[str] = None, 
                 username: Optional[str] = None, 
                 password: Optional[str] = None, 
                 pool_size: int = 10, 
                 max_idle_time: int = 60, 
                 connect_timeout: int = 30, 
                 operation_timeout: int = 30, 
                 retry_limit: int = 3, 
                 retry_delay: float = 1.0, 
                 retry_backoff: float = 2.0, 
                 validate_on_borrow: bool = True) -> None:
        """Initialize a new ConnectionPoolBase.

        Args:
            url: The URL of the SurrealDB server
            namespace: The namespace to use
            database: The database to use
            username: The username for authentication
            password: The password for authentication
            pool_size: Maximum number of connections in the pool
            max_idle_time: Maximum time in seconds a connection can be idle before being closed
            connect_timeout: Timeout in seconds for establishing a connection
            operation_timeout: Timeout in seconds for operations
            retry_limit: Maximum number of retries for failed operations
            retry_delay: Initial delay in seconds between retries
            retry_backoff: Backoff multiplier for retry delay
            validate_on_borrow: Whether to validate connections when borrowing from the pool
        """
        self.url = url
        self.namespace = namespace
        self.database = database
        self.username = username
        self.password = password
        self.pool_size = max(1, pool_size)
        self.max_idle_time = max(0, max_idle_time)
        self.connect_timeout = max(1, connect_timeout)
        self.operation_timeout = max(1, operation_timeout)
        self.retry_limit = max(0, retry_limit)
        self.retry_delay = max(0.1, retry_delay)
        self.retry_backoff = max(1.0, retry_backoff)
        self.validate_on_borrow = validate_on_borrow

        # Initialize pool statistics
        self.created_connections = 0
        self.borrowed_connections = 0
        self.returned_connections = 0
        self.discarded_connections = 0

    @abstractmethod
    def create_connection(self) -> Any:
        """Create a new connection.

        Returns:
            A new connection
        """
        pass

    @abstractmethod
    def validate_connection(self, connection: Any) -> bool:
        """Validate a connection.

        Args:
            connection: The connection to validate

        Returns:
            True if the connection is valid, False otherwise
        """
        pass

    @abstractmethod
    def close_connection(self, connection: Any) -> None:
        """Close a connection.

        Args:
            connection: The connection to close
        """
        pass

    @abstractmethod
    def get_connection(self) -> Any:
        """Get a connection from the pool.

        Returns:
            A connection from the pool
        """
        pass

    @abstractmethod
    def return_connection(self, connection: Any) -> None:
        """Return a connection to the pool.

        Args:
            connection: The connection to return
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the pool and all connections."""
        pass


class SyncConnectionPool(ConnectionPoolBase):
    """Synchronous connection pool for SurrealDB.

    This class manages a pool of synchronous connections to a SurrealDB database.
    It handles connection creation, validation, and reuse, and provides methods
    for acquiring and releasing connections.

    The connections returned by this pool are wrapped in SurrealEngineSyncConnection
    objects, which can be used with the Document class and other SurrealEngine
    functionality that expects a SurrealEngineSyncConnection.

    Attributes:
        pool: Queue of available connections
        in_use: Set of connections currently in use
        lock: Lock for thread-safe operations
        closed: Whether the pool is closed
    """

    def __init__(self, 
                 url: str, 
                 namespace: Optional[str] = None, 
                 database: Optional[str] = None, 
                 username: Optional[str] = None, 
                 password: Optional[str] = None, 
                 pool_size: int = 10, 
                 max_idle_time: int = 60, 
                 connect_timeout: int = 30, 
                 operation_timeout: int = 30, 
                 retry_limit: int = 3, 
                 retry_delay: float = 1.0, 
                 retry_backoff: float = 2.0, 
                 validate_on_borrow: bool = True) -> None:
        """Initialize a new SyncConnectionPool.

        Args:
            url: The URL of the SurrealDB server
            namespace: The namespace to use
            database: The database to use
            username: The username for authentication
            password: The password for authentication
            pool_size: Maximum number of connections in the pool
            max_idle_time: Maximum time in seconds a connection can be idle before being closed
            connect_timeout: Timeout in seconds for establishing a connection
            operation_timeout: Timeout in seconds for operations
            retry_limit: Maximum number of retries for failed operations
            retry_delay: Initial delay in seconds between retries
            retry_backoff: Backoff multiplier for retry delay
            validate_on_borrow: Whether to validate connections when borrowing from the pool
        """
        super().__init__(
            url, namespace, database, username, password, 
            pool_size, max_idle_time, connect_timeout, operation_timeout, 
            retry_limit, retry_delay, retry_backoff, validate_on_borrow
        )

        # Initialize the pool
        self.pool: Queue = Queue(maxsize=self.pool_size)
        self.in_use: Dict['SurrealEngineSyncConnection', float] = {}  # Connection -> timestamp when borrowed
        self.lock = Lock()
        self.closed = False

    def create_connection(self) -> 'SurrealEngineSyncConnection':
        """Create a new connection.

        Returns:
            A new connection wrapped in SurrealEngineSyncConnection

        Raises:
            Exception: If the connection cannot be created
        """
        try:
            # Create a SurrealEngineSyncConnection
            connection = SurrealEngineSyncConnection(
                url=self.url,
                namespace=self.namespace,
                database=self.database,
                username=self.username,
                password=self.password
            )

            # Connect to the database
            connection.connect()

            self.created_connections += 1
            logger.debug(f"Created new connection (total created: {self.created_connections})")

            return connection
        except Exception as e:
            logger.error(f"Failed to create connection: {str(e)}")
            raise

    def validate_connection(self, connection: 'SurrealEngineSyncConnection') -> bool:
        """Validate a connection.

        Args:
            connection: The connection to validate (SurrealEngineSyncConnection)

        Returns:
            True if the connection is valid, False otherwise
        """
        try:
            # Execute a simple query to check if the connection is valid
            if connection.client:
                connection.client.query("SELECT 1 FROM information_schema.tables LIMIT 1")
                return True
            return False
        except Exception as e:
            logger.warning(f"Connection validation failed: {str(e)}")
            return False

    def close_connection(self, connection: 'SurrealEngineSyncConnection') -> None:
        """Close a connection.

        Args:
            connection: The connection to close (SurrealEngineSyncConnection)
        """
        try:
            connection.disconnect()
            self.discarded_connections += 1
            logger.debug(f"Closed connection (total discarded: {self.discarded_connections})")
        except Exception as e:
            logger.warning(f"Failed to close connection: {str(e)}")

    def get_connection(self) -> 'SurrealEngineSyncConnection':
        """Get a connection from the pool.

        Returns:
            A SurrealEngineSyncConnection from the pool

        Raises:
            RuntimeError: If the pool is closed
            Exception: If a connection cannot be obtained
        """
        if self.closed:
            raise RuntimeError("Connection pool is closed")

        # Try to get a connection from the pool
        try:
            connection = self.pool.get(block=False)

            # Validate the connection if needed
            if self.validate_on_borrow and not self.validate_connection(connection):
                # Connection is invalid, close it and create a new one
                self.close_connection(connection)
                connection = self.create_connection()
        except Empty:
            # Pool is empty, create a new connection if we haven't reached the limit
            with self.lock:
                if len(self.in_use) < self.pool_size:
                    connection = self.create_connection()
                else:
                    # Wait for a connection to become available
                    try:
                        connection = self.pool.get(timeout=self.connect_timeout)

                        # Validate the connection if needed
                        if self.validate_on_borrow and not self.validate_connection(connection):
                            # Connection is invalid, close it and create a new one
                            self.close_connection(connection)
                            connection = self.create_connection()
                    except Empty:
                        raise RuntimeError("Timeout waiting for a connection")

        # Mark the connection as in use
        with self.lock:
            self.in_use[connection] = time.time()
            self.borrowed_connections += 1
            logger.debug(f"Borrowed connection (total borrowed: {self.borrowed_connections})")

        return connection

    def return_connection(self, connection: 'SurrealEngineSyncConnection') -> None:
        """Return a connection to the pool.

        Args:
            connection: The connection to return (SurrealEngineSyncConnection)
        """
        if self.closed:
            # Pool is closed, just close the connection
            self.close_connection(connection)
            return

        # Remove the connection from the in-use set
        with self.lock:
            if connection in self.in_use:
                del self.in_use[connection]
                self.returned_connections += 1
                logger.debug(f"Returned connection (total returned: {self.returned_connections})")
            else:
                # Connection wasn't borrowed from this pool
                logger.warning("Attempted to return a connection that wasn't borrowed from this pool")
                return

        # Check if the connection is still valid
        if self.validate_on_borrow and not self.validate_connection(connection):
            # Connection is invalid, close it
            self.close_connection(connection)
            return

        # Return the connection to the pool
        try:
            self.pool.put(connection, block=False)
        except Exception:
            # Pool is full, close the connection
            self.close_connection(connection)

    def close(self) -> None:
        """Close the pool and all connections."""
        if self.closed:
            return

        self.closed = True

        # Close all connections in the pool
        while not self.pool.empty():
            try:
                connection = self.pool.get(block=False)
                self.close_connection(connection)
            except Empty:
                break

        # Close all in-use connections
        with self.lock:
            for connection in list(self.in_use.keys()):
                self.close_connection(connection)
            self.in_use.clear()

        logger.info(f"Connection pool closed. Stats: created={self.created_connections}, "
                   f"borrowed={self.borrowed_connections}, returned={self.returned_connections}, "
                   f"discarded={self.discarded_connections}")


class AsyncConnectionPool(ConnectionPoolBase):
    """Asynchronous connection pool for SurrealDB.

    This class manages a pool of asynchronous connections to a SurrealDB database.
    It handles connection creation, validation, and reuse, and provides methods
    for acquiring and releasing connections.

    The connections returned by this pool are wrapped in SurrealEngineAsyncConnection
    objects, which can be used with the Document class and other SurrealEngine
    functionality that expects a SurrealEngineAsyncConnection.

    Attributes:
        pool: List of available connections
        in_use: Dictionary of connections currently in use and their timestamps
        lock: Asyncio lock for thread-safe operations
        closed: Whether the pool is closed
    """

    def __init__(self, 
                 url: str, 
                 namespace: Optional[str] = None, 
                 database: Optional[str] = None, 
                 username: Optional[str] = None, 
                 password: Optional[str] = None, 
                 pool_size: int = 10, 
                 max_idle_time: int = 60, 
                 connect_timeout: int = 30, 
                 operation_timeout: int = 30, 
                 retry_limit: int = 3, 
                 retry_delay: float = 1.0, 
                 retry_backoff: float = 2.0, 
                 validate_on_borrow: bool = True) -> None:
        """Initialize a new AsyncConnectionPool.

        Args:
            url: The URL of the SurrealDB server
            namespace: The namespace to use
            database: The database to use
            username: The username for authentication
            password: The password for authentication
            pool_size: Maximum number of connections in the pool
            max_idle_time: Maximum time in seconds a connection can be idle before being closed
            connect_timeout: Timeout in seconds for establishing a connection
            operation_timeout: Timeout in seconds for operations
            retry_limit: Maximum number of retries for failed operations
            retry_delay: Initial delay in seconds between retries
            retry_backoff: Backoff multiplier for retry delay
            validate_on_borrow: Whether to validate connections when borrowing from the pool
        """
        super().__init__(
            url, namespace, database, username, password, 
            pool_size, max_idle_time, connect_timeout, operation_timeout, 
            retry_limit, retry_delay, retry_backoff, validate_on_borrow
        )

        # Initialize the pool
        self.pool: List['SurrealEngineAsyncConnection'] = []
        self.in_use: Dict['SurrealEngineAsyncConnection', float] = {}  # Connection -> timestamp when borrowed
        self.lock = asyncio.Lock()
        self.closed = False
        self.connection_waiters: List[asyncio.Future] = []

    async def create_connection(self) -> 'SurrealEngineAsyncConnection':
        """Create a new connection.

        Returns:
            A new connection wrapped in SurrealEngineAsyncConnection

        Raises:
            Exception: If the connection cannot be created
        """
        try:
            # Create a SurrealEngineAsyncConnection
            connection = SurrealEngineAsyncConnection(
                url=self.url,
                namespace=self.namespace,
                database=self.database,
                username=self.username,
                password=self.password
            )

            # Connect to the database
            await connection.connect()

            self.created_connections += 1
            logger.debug(f"Created new async connection (total created: {self.created_connections})")

            return connection
        except Exception as e:
            logger.error(f"Failed to create async connection: {str(e)}")
            raise

    async def validate_connection(self, connection: 'SurrealEngineAsyncConnection') -> bool:
        """Validate a connection.

        Args:
            connection: The connection to validate (SurrealEngineAsyncConnection)

        Returns:
            True if the connection is valid, False otherwise
        """
        try:
            # Execute a simple query to check if the connection is valid
            if connection.client:
                await connection.client.query("SELECT 1 FROM information_schema.tables LIMIT 1")
                return True
            return False
        except Exception as e:
            logger.warning(f"Async connection validation failed: {str(e)}")
            return False

    async def close_connection(self, connection: 'SurrealEngineAsyncConnection') -> None:
        """Close a connection.

        Args:
            connection: The connection to close (SurrealEngineAsyncConnection)
        """
        try:
            await connection.disconnect()
            self.discarded_connections += 1
            logger.debug(f"Closed async connection (total discarded: {self.discarded_connections})")
        except Exception as e:
            logger.warning(f"Failed to close async connection: {str(e)}")

    async def get_connection(self) -> 'SurrealEngineAsyncConnection':
        """Get a connection from the pool.

        Returns:
            A SurrealEngineAsyncConnection from the pool

        Raises:
            RuntimeError: If the pool is closed
            Exception: If a connection cannot be obtained
        """
        if self.closed:
            raise RuntimeError("Async connection pool is closed")

        async with self.lock:
            # Try to get a connection from the pool
            if self.pool:
                connection = self.pool.pop()

                # Validate the connection if needed
                if self.validate_on_borrow:
                    is_valid = await self.validate_connection(connection)
                    if not is_valid:
                        # Connection is invalid, close it and create a new one
                        await self.close_connection(connection)
                        connection = await self.create_connection()
            elif len(self.in_use) < self.pool_size:
                # Pool is empty but we haven't reached the limit, create a new connection
                connection = await self.create_connection()
            else:
                # We've reached the pool size limit, wait for a connection to be returned
                waiter = asyncio.get_event_loop().create_future()
                self.connection_waiters.append(waiter)

                # Release the lock while waiting
                self.lock.release()
                try:
                    # Wait for a connection with timeout
                    connection = await asyncio.wait_for(waiter, timeout=self.connect_timeout)

                    # Validate the connection if needed
                    if self.validate_on_borrow:
                        is_valid = await self.validate_connection(connection)
                        if not is_valid:
                            # Connection is invalid, close it and create a new one
                            await self.close_connection(connection)
                            async with self.lock:
                                connection = await self.create_connection()
                except asyncio.TimeoutError:
                    # Remove the waiter from the list
                    async with self.lock:
                        if waiter in self.connection_waiters:
                            self.connection_waiters.remove(waiter)
                    raise RuntimeError("Timeout waiting for an async connection")
                except Exception:
                    # Remove the waiter from the list
                    async with self.lock:
                        if waiter in self.connection_waiters:
                            self.connection_waiters.remove(waiter)
                    raise
                finally:
                    # Re-acquire the lock
                    await self.lock.acquire()

            # Mark the connection as in use
            self.in_use[connection] = time.time()
            self.borrowed_connections += 1
            logger.debug(f"Borrowed async connection (total borrowed: {self.borrowed_connections})")

            return connection

    async def return_connection(self, connection: 'SurrealEngineAsyncConnection') -> None:
        """Return a connection to the pool.

        Args:
            connection: The connection to return (SurrealEngineAsyncConnection)
        """
        if self.closed:
            # Pool is closed, just close the connection
            await self.close_connection(connection)
            return

        async with self.lock:
            # Remove the connection from the in-use set
            if connection in self.in_use:
                del self.in_use[connection]
                self.returned_connections += 1
                logger.debug(f"Returned async connection (total returned: {self.returned_connections})")
            else:
                # Connection wasn't borrowed from this pool
                logger.warning("Attempted to return an async connection that wasn't borrowed from this pool")
                return

            # Check if there are waiters
            if self.connection_waiters:
                # Give the connection to the first waiter
                waiter = self.connection_waiters.pop(0)
                if not waiter.done():
                    waiter.set_result(connection)
                    return

            # Check if the connection is still valid
            if self.validate_on_borrow:
                is_valid = await self.validate_connection(connection)
                if not is_valid:
                    # Connection is invalid, close it
                    await self.close_connection(connection)
                    return

            # Return the connection to the pool
            if len(self.pool) < self.pool_size:
                self.pool.append(connection)
            else:
                # Pool is full, close the connection
                await self.close_connection(connection)

    async def close(self) -> None:
        """Close the pool and all connections."""
        if self.closed:
            return

        async with self.lock:
            self.closed = True

            # Cancel all waiters
            for waiter in self.connection_waiters:
                if not waiter.done():
                    waiter.set_exception(RuntimeError("Async connection pool is closed"))
            self.connection_waiters.clear()

            # Close all connections in the pool
            for connection in self.pool:
                await self.close_connection(connection)
            self.pool.clear()

            # Close all in-use connections
            for connection in list(self.in_use.keys()):
                await self.close_connection(connection)
            self.in_use.clear()

            logger.info(f"Async connection pool closed. Stats: created={self.created_connections}, "
                       f"borrowed={self.borrowed_connections}, returned={self.returned_connections}, "
                       f"discarded={self.discarded_connections}")


class ConnectionEvent:
    """Event types for connection events.

    This class defines the event types that can be emitted by connections.
    """
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    RECONNECTED = "reconnected"
    CONNECTION_FAILED = "connection_failed"
    RECONNECTION_FAILED = "reconnection_failed"
    CONNECTION_CLOSED = "connection_closed"


class ConnectionEventListener:
    """Listener for connection events.

    This class defines the interface for connection event listeners.
    """

    def on_event(self, event_type: str, connection: Any, **kwargs) -> None:
        """Handle a connection event.

        Args:
            event_type: The type of event
            connection: The connection that emitted the event
            **kwargs: Additional event data
        """
        pass


class ConnectionEventEmitter:
    """Emitter for connection events.

    This class provides methods for registering listeners and emitting events.

    Attributes:
        listeners: List of registered event listeners
    """

    def __init__(self) -> None:
        """Initialize a new ConnectionEventEmitter."""
        self.listeners: List[ConnectionEventListener] = []

    def add_listener(self, listener: ConnectionEventListener) -> None:
        """Add a listener for connection events.

        Args:
            listener: The listener to add
        """
        if listener not in self.listeners:
            self.listeners.append(listener)

    def remove_listener(self, listener: ConnectionEventListener) -> None:
        """Remove a listener for connection events.

        Args:
            listener: The listener to remove
        """
        if listener in self.listeners:
            self.listeners.remove(listener)

    def emit_event(self, event_type: str, connection: Any, **kwargs) -> None:
        """Emit a connection event.

        Args:
            event_type: The type of event
            connection: The connection that emitted the event
            **kwargs: Additional event data
        """
        for listener in self.listeners:
            try:
                listener.on_event(event_type, connection, **kwargs)
            except Exception as e:
                logger.warning(f"Error in connection event listener: {str(e)}")


class OperationQueue:
    """Queue for operations during reconnection.

    This class manages a queue of operations that are waiting for a connection
    to be reestablished. Once the connection is restored, the operations are
    executed in the order they were queued.

    Attributes:
        sync_operations: Queue of synchronous operations
        async_operations: Queue of asynchronous operations
        is_reconnecting: Whether the connection is currently reconnecting
        reconnection_event: Event that is set when reconnection is complete
        async_reconnection_event: Asyncio event that is set when reconnection is complete
    """

    def __init__(self) -> None:
        """Initialize a new OperationQueue."""
        self.sync_operations: List[Tuple[Callable, List, Dict]] = []
        self.async_operations: List[Tuple[Callable, List, Dict]] = []
        self.is_reconnecting = False
        self.reconnection_event = Event()
        self.async_reconnection_event = asyncio.Event()

    def start_reconnection(self) -> None:
        """Start the reconnection process.

        This method marks the connection as reconnecting and clears the
        reconnection events.
        """
        self.is_reconnecting = True
        self.reconnection_event.clear()
        self.async_reconnection_event.clear()

    def end_reconnection(self) -> None:
        """End the reconnection process.

        This method marks the connection as no longer reconnecting and sets
        the reconnection events.
        """
        self.is_reconnecting = False
        self.reconnection_event.set()
        self.async_reconnection_event.set()

    def queue_operation(self, operation: Callable, args: List = None, kwargs: Dict = None) -> None:
        """Queue a synchronous operation.

        Args:
            operation: The operation to queue
            args: The positional arguments for the operation
            kwargs: The keyword arguments for the operation
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        self.sync_operations.append((operation, args, kwargs))

    def queue_async_operation(self, operation: Callable, args: List = None, kwargs: Dict = None) -> None:
        """Queue an asynchronous operation.

        Args:
            operation: The operation to queue
            args: The positional arguments for the operation
            kwargs: The keyword arguments for the operation
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        self.async_operations.append((operation, args, kwargs))

    def execute_queued_operations(self) -> None:
        """Execute all queued synchronous operations."""
        operations = self.sync_operations
        self.sync_operations = []

        for operation, args, kwargs in operations:
            try:
                operation(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing queued operation: {str(e)}")

    async def execute_queued_async_operations(self) -> None:
        """Execute all queued asynchronous operations."""
        operations = self.async_operations
        self.async_operations = []

        for operation, args, kwargs in operations:
            try:
                await operation(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing queued async operation: {str(e)}")

    def wait_for_reconnection(self, timeout: Optional[float] = None) -> bool:
        """Wait for reconnection to complete.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if reconnection completed, False if timed out
        """
        if not self.is_reconnecting:
            return True

        return self.reconnection_event.wait(timeout)

    async def wait_for_async_reconnection(self, timeout: Optional[float] = None) -> bool:
        """Wait for reconnection to complete asynchronously.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if reconnection completed, False if timed out
        """
        if not self.is_reconnecting:
            return True

        try:
            if timeout is not None:
                await asyncio.wait_for(self.async_reconnection_event.wait(), timeout)
            else:
                await self.async_reconnection_event.wait()
            return True
        except asyncio.TimeoutError:
            return False


class ReconnectionStrategy:
    """Strategy for reconnecting to the database.

    This class provides methods for reconnecting to the database with
    configurable retry limits and backoff strategies.

    Attributes:
        max_attempts: Maximum number of reconnection attempts
        initial_delay: Initial delay in seconds between reconnection attempts
        max_delay: Maximum delay in seconds between reconnection attempts
        backoff_factor: Backoff multiplier for reconnection delay
    """

    def __init__(self, max_attempts: int = 10, initial_delay: float = 1.0, 
                 max_delay: float = 60.0, backoff_factor: float = 2.0) -> None:
        """Initialize a new ReconnectionStrategy.

        Args:
            max_attempts: Maximum number of reconnection attempts
            initial_delay: Initial delay in seconds between reconnection attempts
            max_delay: Maximum delay in seconds between reconnection attempts
            backoff_factor: Backoff multiplier for reconnection delay
        """
        self.max_attempts = max(1, max_attempts)
        self.initial_delay = max(0.1, initial_delay)
        self.max_delay = max(self.initial_delay, max_delay)
        self.backoff_factor = max(1.0, backoff_factor)

    def get_delay(self, attempt: int) -> float:
        """Get the delay for a reconnection attempt.

        Args:
            attempt: The reconnection attempt number (0-based)

        Returns:
            The delay in seconds for the reconnection attempt
        """
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        return min(delay, self.max_delay)


class RetryStrategy:
    """Strategy for retrying operations with exponential backoff.

    This class provides methods for retrying operations with configurable
    retry limits and backoff strategies.

    Attributes:
        retry_limit: Maximum number of retries
        retry_delay: Initial delay in seconds between retries
        retry_backoff: Backoff multiplier for retry delay
    """

    def __init__(self, retry_limit: int = 3, retry_delay: float = 1.0, retry_backoff: float = 2.0) -> None:
        """Initialize a new RetryStrategy.

        Args:
            retry_limit: Maximum number of retries
            retry_delay: Initial delay in seconds between retries
            retry_backoff: Backoff multiplier for retry delay
        """
        self.retry_limit = max(0, retry_limit)
        self.retry_delay = max(0.1, retry_delay)
        self.retry_backoff = max(1.0, retry_backoff)

    def get_retry_delay(self, attempt: int) -> float:
        """Get the delay for a retry attempt.

        Args:
            attempt: The retry attempt number (0-based)

        Returns:
            The delay in seconds for the retry attempt
        """
        return self.retry_delay * (self.retry_backoff ** attempt)

    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """Determine whether to retry an operation.

        Args:
            attempt: The retry attempt number (0-based)
            exception: The exception that caused the operation to fail

        Returns:
            True if the operation should be retried, False otherwise
        """
        # Don't retry if we've reached the retry limit
        if attempt >= self.retry_limit:
            return False

        # Determine whether the exception is retryable
        # For now, we'll retry on all exceptions, but in a real implementation
        # you might want to be more selective
        return True

    def execute_with_retry(self, operation: Callable[[], Any]) -> Any:
        """Execute an operation with retry.

        Args:
            operation: The operation to execute

        Returns:
            The result of the operation

        Raises:
            Exception: If the operation fails after all retries
        """
        last_exception = None

        for attempt in range(self.retry_limit + 1):
            try:
                return operation()
            except Exception as e:
                last_exception = e

                if not self.should_retry(attempt, e):
                    break

                # Calculate the delay for this retry attempt
                delay = self.get_retry_delay(attempt)

                logger.warning(f"Operation failed: {str(e)}. Retrying in {delay:.2f} seconds (attempt {attempt + 1}/{self.retry_limit + 1})...")

                # Wait before retrying
                time.sleep(delay)

        # If we get here, all retries failed
        if last_exception:
            logger.error(f"Operation failed after {self.retry_limit + 1} attempts: {str(last_exception)}")
            raise last_exception

        # This should never happen, but just in case
        raise RuntimeError("Operation failed for unknown reason")

    async def execute_with_retry_async(self, operation: Callable[[], Any]) -> Any:
        """Execute an asynchronous operation with retry.

        Args:
            operation: The asynchronous operation to execute

        Returns:
            The result of the operation

        Raises:
            Exception: If the operation fails after all retries
        """
        last_exception = None

        for attempt in range(self.retry_limit + 1):
            try:
                return await operation()
            except Exception as e:
                last_exception = e

                if not self.should_retry(attempt, e):
                    break

                # Calculate the delay for this retry attempt
                delay = self.get_retry_delay(attempt)

                logger.warning(f"Async operation failed: {str(e)}. Retrying in {delay:.2f} seconds (attempt {attempt + 1}/{self.retry_limit + 1})...")

                # Wait before retrying
                await asyncio.sleep(delay)

        # If we get here, all retries failed
        if last_exception:
            logger.error(f"Async operation failed after {self.retry_limit + 1} attempts: {str(last_exception)}")
            raise last_exception

        # This should never happen, but just in case
        raise RuntimeError("Async operation failed for unknown reason")


def parse_connection_string(connection_string: str) -> Dict[str, Any]:
    """Parse a connection string into a dictionary of connection parameters.

    Supports the following formats:
    - surrealdb://user:pass@host:port/namespace/database?param1=value1&param2=value2 (maps to ws://)
    - wss://user:pass@host:port/namespace/database?param1=value1&param2=value2
    - ws://user:pass@host:port/namespace/database?param1=value1&param2=value2
    - http://user:pass@host:port/namespace/database?param1=value1&param2=value2
    - https://user:pass@host:port/namespace/database?param1=value1&param2=value2

    Connection string parameters:
    - pool_size: Maximum number of connections in the pool (default: 10)
    - max_idle_time: Maximum time in seconds a connection can be idle before being closed (default: 60)
    - connect_timeout: Timeout in seconds for establishing a connection (default: 30)
    - operation_timeout: Timeout in seconds for operations (default: 30)
    - retry_limit: Maximum number of retries for failed operations (default: 3)
    - retry_delay: Initial delay in seconds between retries (default: 1)
    - retry_backoff: Backoff multiplier for retry delay (default: 2)
    - validate_on_borrow: Whether to validate connections when borrowing from the pool (default: true)

    Args:
        connection_string: The connection string to parse

    Returns:
        A dictionary containing the parsed connection parameters

    Raises:
        ValueError: If the connection string is invalid
    """
    # Validate the connection string
    if not connection_string:
        raise ValueError("Connection string cannot be empty")

    # Check if the connection string starts with a supported protocol
    supported_protocols = ["surrealdb://", "wss://", "ws://", "http://", "https://"]
    protocol_match = False
    for protocol in supported_protocols:
        if connection_string.startswith(protocol):
            protocol_match = True
            break

    if not protocol_match:
        raise ValueError(f"Connection string must start with one of: {', '.join(supported_protocols)}")

    # Parse the connection string using urllib.parse
    try:
        parsed_url = urllib.parse.urlparse(connection_string)

        # Extract the components
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc
        path = parsed_url.path.strip('/')
        query = parsed_url.query

        # Parse the netloc to get username, password, host, and port
        username = None
        password = None
        if '@' in netloc:
            auth, netloc = netloc.split('@', 1)
            if ':' in auth:
                username, password = auth.split(':', 1)
                username = urllib.parse.unquote(username)
                password = urllib.parse.unquote(password)
            else:
                username = urllib.parse.unquote(auth)

        # Parse host and port
        host = netloc
        port = None
        if ':' in netloc:
            host, port_str = netloc.split(':', 1)
            try:
                port = int(port_str)
            except ValueError:
                raise ValueError(f"Invalid port number: {port_str}")

        # Parse namespace and database from path
        namespace = None
        database = None
        path_parts = path.split('/')
        if len(path_parts) >= 1 and path_parts[0]:
            namespace = path_parts[0]
        if len(path_parts) >= 2 and path_parts[1]:
            database = path_parts[1]

        # Parse query parameters
        params = {}
        if query:
            query_params = urllib.parse.parse_qs(query)
            for key, values in query_params.items():
                if len(values) == 1:
                    # Try to convert to appropriate types
                    value = values[0]
                    if value.lower() == 'true':
                        params[key] = True
                    elif value.lower() == 'false':
                        params[key] = False
                    elif value.isdigit():
                        params[key] = int(value)
                    elif re.match(r'^-?\d+(\.\d+)?$', value):
                        params[key] = float(value)
                    else:
                        params[key] = value
                else:
                    params[key] = values

        # Construct the URL
        # Map the surrealdb scheme to ws scheme
        if scheme == "surrealdb":
            scheme = "ws"
        url = f"{scheme}://{host}"
        if port:
            url += f":{port}"

        # Build the result dictionary
        result = {
            "url": url,
            "namespace": namespace,
            "database": database,
            "username": username,
            "password": password,
            **params
        }

        return result

    except Exception as e:
        raise ValueError(f"Failed to parse connection string: {str(e)}")

@runtime_checkable
class BaseSurrealEngineConnection(Protocol):
    """Protocol defining the interface for SurrealDB connections.

    This protocol defines the common interface that both synchronous and
    asynchronous connections must implement.
    """
    url: Optional[str]
    namespace: Optional[str]
    database: Optional[str]
    username: Optional[str]
    password: Optional[str]
    client: Any

    @property
    def db(self) -> SurrealEngine:
        """Get dynamic table accessor."""
        ...

class ConnectionPoolClient:
    """Client that proxies requests to connections from a connection pool.

    This class provides the same interface as the SurrealDB client but gets a connection
    from the pool for each operation and returns it when done.

    Attributes:
        pool: The connection pool to get connections from
    """

    def __init__(self, pool: 'AsyncConnectionPool') -> None:
        """Initialize a new ConnectionPoolClient.

        Args:
            pool: The connection pool to get connections from
        """
        self.pool = pool

    async def create(self, collection: str, data: Dict[str, Any]) -> Any:
        """Create a new record in the database.

        Args:
            collection: The collection to create the record in
            data: The data to create the record with

        Returns:
            The created record
        """
        connection = await self.pool.get_connection()
        try:
            return await connection.client.create(collection, data)
        finally:
            await self.pool.return_connection(connection)

    async def update(self, id: str, data: Dict[str, Any]) -> Any:
        """Update an existing record in the database.

        Args:
            id: The ID of the record to update
            data: The data to update the record with

        Returns:
            The updated record
        """
        connection = await self.pool.get_connection()
        try:
            return await connection.client.update(id, data)
        finally:
            await self.pool.return_connection(connection)

    async def delete(self, id: str) -> Any:
        """Delete a record from the database.

        Args:
            id: The ID of the record to delete

        Returns:
            The result of the delete operation
        """
        connection = await self.pool.get_connection()
        try:
            return await connection.client.delete(id)
        finally:
            await self.pool.return_connection(connection)

    async def select(self, id: str) -> Any:
        """Select a record from the database.

        Args:
            id: The ID of the record to select

        Returns:
            The selected record
        """
        connection = await self.pool.get_connection()
        try:
            return await connection.client.select(id)
        finally:
            await self.pool.return_connection(connection)

    async def query(self, query: str) -> Any:
        """Execute a query against the database.

        Args:
            query: The query to execute

        Returns:
            The result of the query
        """
        connection = await self.pool.get_connection()
        try:
            return await connection.client.query(query)
        finally:
            await self.pool.return_connection(connection)

    async def insert(self, collection: str, data: List[Dict[str, Any]]) -> Any:
        """Insert multiple records into the database.

        Args:
            collection: The collection to insert the records into
            data: The data to insert

        Returns:
            The inserted records
        """
        connection = await self.pool.get_connection()
        try:
            return await connection.client.insert(collection, data)
        finally:
            await self.pool.return_connection(connection)

    async def signin(self, credentials: Dict[str, str]) -> Any:
        """Sign in to the database.

        Args:
            credentials: The credentials to sign in with

        Returns:
            The result of the sign-in operation
        """
        connection = await self.pool.get_connection()
        try:
            return await connection.client.signin(credentials)
        finally:
            await self.pool.return_connection(connection)

    async def use(self, namespace: str, database: str) -> Any:
        """Use a specific namespace and database.

        Args:
            namespace: The namespace to use
            database: The database to use

        Returns:
            The result of the use operation
        """
        connection = await self.pool.get_connection()
        try:
            return await connection.client.use(namespace, database)
        finally:
            await self.pool.return_connection(connection)

    async def close(self) -> None:
        """Close the connection pool."""
        await self.pool.close()


class ConnectionRegistry:
    """Global connection registry for multi-backend support.

    This class provides a centralized registry for managing database connections
    for multiple backends (SurrealDB, ClickHouse, etc.). It allows setting default
    connections per backend and registering named connections that can be retrieved
    throughout the application.

    Attributes:
        _default_async_connection: The default async connection to use when none is specified (legacy)
        _default_sync_connection: The default sync connection to use when none is specified (legacy)
        _async_connections: Dictionary of named async connections (legacy)
        _sync_connections: Dictionary of named sync connections (legacy)
        _backend_connections: Dictionary of backend -> {connection_name -> connection}
        _default_backend_connections: Dictionary of backend -> default_connection
    """

    # Legacy attributes for backward compatibility
    _default_async_connection: Optional['SurrealEngineAsyncConnection'] = None
    _default_sync_connection: Optional['SurrealEngineSyncConnection'] = None
    _async_connections: Dict[str, 'SurrealEngineAsyncConnection'] = {}
    _sync_connections: Dict[str, 'SurrealEngineSyncConnection'] = {}
    
    # New multi-backend attributes
    _backend_connections: Dict[str, Dict[str, Any]] = {}
    _default_backend_connections: Dict[str, Any] = {}

    @classmethod
    def set_default_async_connection(cls, connection: 'SurrealEngineAsyncConnection') -> None:
        """Set the default async connection.

        Args:
            connection: The async connection to set as default
        """
        cls._default_async_connection = connection

    @classmethod
    def set_default_sync_connection(cls, connection: 'SurrealEngineSyncConnection') -> None:
        """Set the default sync connection.

        Args:
            connection: The sync connection to set as default
        """
        cls._default_sync_connection = connection

    @classmethod
    def set_default_connection(cls, connection: Union['SurrealEngineAsyncConnection', 'SurrealEngineSyncConnection']) -> None:
        """Set the default connection based on its type.

        Args:
            connection: The connection to set as default
        """
        if isinstance(connection, SurrealEngineAsyncConnection):
            cls.set_default_async_connection(connection)
        elif isinstance(connection, SurrealEngineSyncConnection):
            cls.set_default_sync_connection(connection)
        else:
            raise TypeError(f"Unsupported connection type: {type(connection)}")

    @classmethod
    def get_default_async_connection(cls) -> 'SurrealEngineAsyncConnection':
        """Get the default async connection.

        Returns:
            The default async connection

        Raises:
            RuntimeError: If no default async connection has been set
        """
        if cls._default_async_connection is None:
            raise RuntimeError("No default async connection has been set. Call set_default_async_connection() first.")
        return cls._default_async_connection

    @classmethod
    def get_default_sync_connection(cls) -> 'SurrealEngineSyncConnection':
        """Get the default sync connection.

        Returns:
            The default sync connection

        Raises:
            RuntimeError: If no default sync connection has been set
        """
        if cls._default_sync_connection is None:
            raise RuntimeError("No default sync connection has been set. Call set_default_sync_connection() first.")
        return cls._default_sync_connection

    @classmethod
    def get_default_connection(cls, async_mode: bool = True) -> Union['SurrealEngineAsyncConnection', 'SurrealEngineSyncConnection']:
        """Get the default connection based on the mode.

        Args:
            async_mode: Whether to get the async or sync connection

        Returns:
            The default connection of the requested type

        Raises:
            RuntimeError: If no default connection of the requested type has been set
        """
        if async_mode:
            return cls.get_default_async_connection()
        else:
            return cls.get_default_sync_connection()

    @classmethod
    def add_async_connection(cls, name: str, connection: 'SurrealEngineAsyncConnection') -> None:
        """Add a named async connection to the registry.

        Args:
            name: The name to register the connection under
            connection: The async connection to register
        """
        cls._async_connections[name] = connection

    @classmethod
    def add_sync_connection(cls, name: str, connection: 'SurrealEngineSyncConnection') -> None:
        """Add a named sync connection to the registry.

        Args:
            name: The name to register the connection under
            connection: The sync connection to register
        """
        cls._sync_connections[name] = connection

    @classmethod
    def add_connection(cls, name: str, connection: Union['SurrealEngineAsyncConnection', 'SurrealEngineSyncConnection']) -> None:
        """Add a named connection to the registry based on its type.

        Args:
            name: The name to register the connection under
            connection: The connection to register
        """
        if isinstance(connection, SurrealEngineAsyncConnection):
            cls.add_async_connection(name, connection)
        elif isinstance(connection, SurrealEngineSyncConnection):
            cls.add_sync_connection(name, connection)
        else:
            raise TypeError(f"Unsupported connection type: {type(connection)}")

    @classmethod
    def get_async_connection(cls, name: str) -> 'SurrealEngineAsyncConnection':
        """Get a named async connection from the registry.

        Args:
            name: The name of the async connection to retrieve

        Returns:
            The requested async connection

        Raises:
            KeyError: If no async connection with the given name exists
        """
        if name not in cls._async_connections:
            raise KeyError(f"No async connection named '{name}' exists.")
        return cls._async_connections[name]

    @classmethod
    def get_sync_connection(cls, name: str) -> 'SurrealEngineSyncConnection':
        """Get a named sync connection from the registry.

        Args:
            name: The name of the sync connection to retrieve

        Returns:
            The requested sync connection

        Raises:
            KeyError: If no sync connection with the given name exists
        """
        if name not in cls._sync_connections:
            raise KeyError(f"No sync connection named '{name}' exists.")
        return cls._sync_connections[name]

    @classmethod
    def get_connection(cls, name: str, async_mode: bool = True) -> Union['SurrealEngineAsyncConnection', 'SurrealEngineSyncConnection']:
        """Get a named connection from the registry based on the mode.

        Args:
            name: The name of the connection to retrieve
            async_mode: Whether to get an async or sync connection

        Returns:
            The requested connection of the requested type

        Raises:
            KeyError: If no connection of the requested type with the given name exists
        """
        if async_mode:
            return cls.get_async_connection(name)
        else:
            return cls.get_sync_connection(name)

    # Multi-backend connection management methods

    @classmethod
    def register(cls, name: str, connection: Any, backend: str = 'surrealdb') -> None:
        """Register a connection for a specific backend.
        
        Args:
            name: The name to register the connection under
            connection: The connection object
            backend: The backend type ('surrealdb', 'clickhouse', etc.)
        """
        if backend not in cls._backend_connections:
            cls._backend_connections[backend] = {}
        cls._backend_connections[backend][name] = connection

    @classmethod
    def set_default(cls, backend: str, connection_name: str) -> None:
        """Set the default connection for a backend.
        
        Args:
            backend: The backend type
            connection_name: The name of the connection to set as default
        """
        if backend not in cls._backend_connections or connection_name not in cls._backend_connections[backend]:
            raise ValueError(f"Connection '{connection_name}' not found for backend '{backend}'")
        cls._default_backend_connections[backend] = connection_name

    @classmethod
    def get_default_connection(cls, backend: str = 'surrealdb') -> Any:
        """Get the default connection for a backend.
        
        Args:
            backend: The backend type
            
        Returns:
            The default connection for the backend
            
        Raises:
            ValueError: If no default connection is set for the backend
        """
        if backend not in cls._default_backend_connections:
            raise ValueError(f"No default connection set for backend '{backend}'")
        
        connection_name = cls._default_backend_connections[backend]
        if backend not in cls._backend_connections or connection_name not in cls._backend_connections[backend]:
            raise ValueError(f"Default connection '{connection_name}' not found for backend '{backend}'")
        
        return cls._backend_connections[backend][connection_name]

    @classmethod
    def get_connection_by_backend(cls, name: str, backend: str = 'surrealdb') -> Any:
        """Get a named connection for a specific backend.
        
        Args:
            name: The name of the connection
            backend: The backend type
            
        Returns:
            The requested connection
            
        Raises:
            ValueError: If the connection is not found
        """
        if backend not in cls._backend_connections or name not in cls._backend_connections[backend]:
            raise ValueError(f"Connection '{name}' not found for backend '{backend}'")
        
        return cls._backend_connections[backend][name]

    @classmethod
    def list_backends(cls) -> List[str]:
        """List all registered backends.
        
        Returns:
            List of backend names
        """
        return list(cls._backend_connections.keys())

    @classmethod
    def list_connections(cls, backend: str) -> List[str]:
        """List all connections for a backend.
        
        Args:
            backend: The backend type
            
        Returns:
            List of connection names for the backend
        """
        if backend not in cls._backend_connections:
            return []
        return list(cls._backend_connections[backend].keys())


class SurrealEngineAsyncConnection:
    """Asynchronous connection manager for SurrealDB.

    This class manages the asynchronous connection to a SurrealDB database, providing methods
    for connecting, disconnecting, and executing transactions. It also provides
    access to the database through the db property.

    Attributes:
        url: The URL of the SurrealDB server
        namespace: The namespace to use
        database: The database to use
        username: The username for authentication
        password: The password for authentication
        client: The SurrealDB async client instance or ConnectionPoolClient
        use_pool: Whether to use a connection pool
        pool: The connection pool if use_pool is True
        pool_size: The size of the connection pool
        max_idle_time: Maximum time in seconds a connection can be idle before being closed
    """

    def __init__(self, url: Optional[str] = None, namespace: Optional[str] = None, 
                 database: Optional[str] = None, username: Optional[str] = None, 
                 password: Optional[str] = None, name: Optional[str] = None,
                 make_default: bool = False, use_pool: bool = False,
                 pool_size: int = 10, max_idle_time: int = 60,
                 connect_timeout: int = 30, operation_timeout: int = 30,
                 retry_limit: int = 3, retry_delay: float = 1.0,
                 retry_backoff: float = 2.0, validate_on_borrow: bool = True) -> None:
        """Initialize a new SurrealEngineAsyncConnection.

        Args:
            url: The URL of the SurrealDB server
            namespace: The namespace to use
            database: The database to use
            username: The username for authentication
            password: The password for authentication
            name: The name to register this connection under in the registry
            make_default: Whether to set this connection as the default
            use_pool: Whether to use a connection pool
            pool_size: The size of the connection pool
            max_idle_time: Maximum time in seconds a connection can be idle before being closed
            connect_timeout: Timeout in seconds for establishing a connection
            operation_timeout: Timeout in seconds for operations
            retry_limit: Maximum number of retries for failed operations
            retry_delay: Initial delay in seconds between retries
            retry_backoff: Backoff multiplier for retry delay
            validate_on_borrow: Whether to validate connections when borrowing from the pool
        """
        self.url = url
        self.namespace = namespace
        self.database = database
        self.username = username
        self.password = password
        self.client = None
        self.use_pool = use_pool
        self.pool = None
        self.pool_size = pool_size
        self.max_idle_time = max_idle_time
        self.connect_timeout = connect_timeout
        self.operation_timeout = operation_timeout
        self.retry_limit = retry_limit
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff
        self.validate_on_borrow = validate_on_borrow

        if name:
            ConnectionRegistry.add_async_connection(name, self)
        if make_default or name is None:
            ConnectionRegistry.set_default_async_connection(self)

    async def __aenter__(self) -> 'SurrealEngineAsyncConnection':
        """Enter the async context manager.

        Returns:
            The connection instance
        """
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Optional[Type[BaseException]], 
                        exc_val: Optional[BaseException], 
                        exc_tb: Optional[Any]) -> None:
        """Exit the async context manager.

        Args:
            exc_type: The exception type, if an exception was raised
            exc_val: The exception value, if an exception was raised
            exc_tb: The exception traceback, if an exception was raised
        """
        await self.disconnect()

    @property
    def db(self) -> SurrealEngine:
        """Get dynamic table accessor.

        Returns:
            A SurrealEngine instance for accessing tables dynamically
        """
        return SurrealEngine(self)

    async def _ensure_connected(self) -> None:
        """Ensure connection is established, handling auto-connect task if present."""
        # If there's a pending auto-connect task, await it first
        if hasattr(self, '_auto_connect_task') and self._auto_connect_task:
            await self._auto_connect_task
            self._auto_connect_task = None
        
        # If still not connected, connect now
        if not self.client:
            await self.connect()

    async def connect(self) -> Any:
        """Connect to the database.

        This method creates a new client if one doesn't exist. If use_pool is True,
        it creates a connection pool and a ConnectionPoolClient. Otherwise, it creates
        a direct connection to the database.

        Returns:
            The SurrealDB client instance or ConnectionPoolClient
        """
        if not self.client:
            if self.use_pool:
                # Create a connection pool
                self.pool = AsyncConnectionPool(
                    url=self.url,
                    namespace=self.namespace,
                    database=self.database,
                    username=self.username,
                    password=self.password,
                    pool_size=self.pool_size,
                    max_idle_time=self.max_idle_time,
                    connect_timeout=self.connect_timeout,
                    operation_timeout=self.operation_timeout,
                    retry_limit=self.retry_limit,
                    retry_delay=self.retry_delay,
                    retry_backoff=self.retry_backoff,
                    validate_on_borrow=self.validate_on_borrow
                )

                # Create a client that uses the pool
                self.client = ConnectionPoolClient(self.pool)
            else:
                # Create the client directly
                self.client = surrealdb.AsyncSurreal(self.url)

                # Sign in if credentials are provided
                if self.username and self.password:
                    await self.client.signin({"username": self.username, "password": self.password})

                # Use namespace and database
                if self.namespace and self.database:
                    await self.client.use(self.namespace, self.database)

        return self.client

    async def disconnect(self) -> None:
        """Disconnect from the database.

        This method closes the client connection if one exists. If use_pool is True,
        it closes the connection pool.
        """
        if self.client:
            if self.use_pool and self.pool:
                await self.pool.close()
                self.pool = None
            else:
                await self.client.close()
            self.client = None

    async def transaction(self, coroutines: list) -> list:
        """Execute multiple operations in a transaction.

        This method executes a list of coroutines within a transaction,
        committing the transaction if all operations succeed or canceling
        it if any operation fails.

        Args:
            coroutines: List of coroutines to execute in the transaction

        Returns:
            List of results from the coroutines

        Raises:
            Exception: If any operation in the transaction fails
        """
        await self.client.query("BEGIN TRANSACTION;")
        try:
            results = []
            for coro in coroutines:
                result = await coro
                results.append(result)
            await self.client.query("COMMIT TRANSACTION;")
            return results
        except Exception as e:
            await self.client.query("CANCEL TRANSACTION;")
            raise e


def create_connection(url: Optional[str] = None, namespace: Optional[str] = None, 
                  database: Optional[str] = None, username: Optional[str] = None, 
                  password: Optional[str] = None, name: Optional[str] = None,
                  make_default: bool = False, async_mode: bool = True,
                  use_pool: bool = False, pool_size: int = 10, 
                  max_idle_time: int = 60, connect_timeout: int = 30,
                  operation_timeout: int = 30, retry_limit: int = 3,
                  retry_delay: float = 1.0, retry_backoff: float = 2.0,
                  validate_on_borrow: bool = True, auto_connect: bool = False,
                  backend: str = 'surrealdb', **backend_kwargs) -> Any:
    """Factory function to create a connection for the specified backend.

    Args:
        url: The URL of the database server (for SurrealDB) or host (for ClickHouse)
        namespace: The namespace to use (SurrealDB only)
        database: The database to use
        username: The username for authentication
        password: The password for authentication
        name: The name to register this connection under in the registry
        make_default: Whether to set this connection as the default
        async_mode: Whether to create an async or sync connection (SurrealDB only)
        use_pool: Whether to use a connection pool (SurrealDB async_mode only)
        pool_size: The size of the connection pool
        max_idle_time: Maximum time in seconds a connection can be idle before being closed
        connect_timeout: Timeout in seconds for establishing a connection
        operation_timeout: Timeout in seconds for operations
        retry_limit: Maximum number of retries for failed operations
        retry_delay: Initial delay in seconds between retries
        retry_backoff: Backoff multiplier for retry delay
        validate_on_borrow: Whether to validate connections when borrowing from the pool
        auto_connect: Whether to automatically connect the connection
        backend: The backend type ('surrealdb', 'clickhouse', etc.)
        **backend_kwargs: Additional backend-specific connection parameters

    Returns:
        A connection instance for the specified backend
        
    Examples:
        SurrealDB connection (default)::

            surrealdb_conn = create_connection(
                url="ws://localhost:8000/rpc",
                namespace="test", database="test",
                username="root", password="root"
            )

        ClickHouse connection::

            clickhouse_conn = create_connection(
                url="localhost", database="default",
                username="default", password="",
                backend="clickhouse", port=8123
            )
    """
    if backend == 'surrealdb':
        # Legacy SurrealDB connection creation
        if async_mode:
            connection = SurrealEngineAsyncConnection(
                url=url, 
                namespace=namespace, 
                database=database, 
                username=username, 
                password=password, 
                name=name, 
                make_default=make_default,
                use_pool=use_pool,
                pool_size=pool_size,
                max_idle_time=max_idle_time,
                connect_timeout=connect_timeout,
                operation_timeout=operation_timeout,
                retry_limit=retry_limit,
                retry_delay=retry_delay,
                retry_backoff=retry_backoff,
                validate_on_borrow=validate_on_borrow
            )
        else:
            connection = SurrealEngineSyncConnection(
                url=url, 
                namespace=namespace, 
                database=database, 
                username=username, 
                password=password, 
                name=name, 
                make_default=make_default
            )

        # Register in the unified backend system as well
        if name:
            ConnectionRegistry.register(name, connection, backend)
        if make_default or name is None:
            if name:
                ConnectionRegistry.set_default(backend, name)
            else:
                # Create a default name for unified registry
                default_name = f'{backend}_default'
                ConnectionRegistry.register(default_name, connection, backend)
                ConnectionRegistry.set_default(backend, default_name)

        # Auto-connect if requested - make SurrealDB consistent with other backends
        if auto_connect:
            if async_mode:
                # For async SurrealDB, we need to connect immediately
                import asyncio
                try:
                    # Try to connect immediately in the current async context
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Create a task and wait for it to complete
                        task = asyncio.create_task(connection.connect())
                        # Note: This will be awaited when the connection is first used
                        connection._auto_connect_task = task
                    else:
                        # If no event loop is running, connect will happen on first use
                        pass
                except Exception:
                    # If we can't get the event loop, connect will happen on first use
                    pass
            else:
                connection.connect()

        return connection
        
    elif backend == 'clickhouse':
        # ClickHouse connection creation using modular backend system
        from .backends import BackendRegistry
        
        # Check if ClickHouse backend is available
        if not BackendRegistry.is_backend_available('clickhouse'):
            # This will raise ImportError with helpful message
            BackendRegistry.get_backend('clickhouse')
        
        try:
            import clickhouse_connect
        except ImportError:
            # This should be caught by the BackendRegistry, but just in case
            raise ImportError("ClickHouse backend requires 'clickhouse-connect'. Install with: pip install quantumengine[clickhouse]")
        
        # Build ClickHouse connection parameters
        clickhouse_params = {
            'host': url or 'localhost',
            'database': database or 'default',
            'username': username or 'default',
            'password': password or '',
            **backend_kwargs  # port, secure, etc.
        }
        
        # Create ClickHouse client
        connection = clickhouse_connect.get_client(**clickhouse_params)
        
        # Register in ConnectionRegistry
        if name:
            ConnectionRegistry.register(name, connection, backend)
        if make_default or name is None:
            if name:
                ConnectionRegistry.set_default(backend, name)
            else:
                # Create a default name
                default_name = f'{backend}_default'
                ConnectionRegistry.register(default_name, connection, backend)
                ConnectionRegistry.set_default(backend, default_name)
        
        return connection
        
    else:
        # Generic backend connection creation using BackendRegistry
        from .backends import BackendRegistry
        
        # Check if the backend is available
        try:
            backend_class = BackendRegistry.get_backend(backend)
        except (ImportError, ValueError) as e:
            # Re-raise with additional context
            available = BackendRegistry.list_backends()
            failed = BackendRegistry.list_failed_backends()
            
            error_msg = str(e)
            if failed:
                error_msg += f"\n\nAvailable installation commands:"
                for failed_backend, install_msg in failed.items():
                    error_msg += f"\n  - {install_msg}"
            
            if isinstance(e, ImportError):
                raise ImportError(error_msg)
            else:
                raise ValueError(error_msg)
        
        # Backend-specific connection creation
        if backend == 'redis':
            try:
                import redis
            except ImportError:
                raise ImportError("Redis backend requires 'redis'. Install with: pip install quantumengine[redis]")
            
            # Build Redis connection parameters
            redis_params = {
                'host': url or 'localhost',
                'port': backend_kwargs.get('port', 6379),
                'db': backend_kwargs.get('db', 0),
                'decode_responses': backend_kwargs.get('decode_responses', True),
                **{k: v for k, v in backend_kwargs.items() if k not in ['port', 'db', 'decode_responses']}
            }
            
            # Add auth if provided
            if password:
                redis_params['password'] = password
            if username:
                redis_params['username'] = username
            
            # Create Redis client
            connection = redis.Redis(**redis_params)
            
            # Test connection
            try:
                connection.ping()
            except Exception as e:
                raise ConnectionError(f"Failed to connect to Redis: {e}")
            
            # Register in ConnectionRegistry
            if name:
                ConnectionRegistry.register(name, connection, backend)
            if make_default or name is None:
                if name:
                    ConnectionRegistry.set_default(backend, name)
                else:
                    # Create a default name
                    default_name = f'{backend}_default'
                    ConnectionRegistry.register(default_name, connection, backend)
                    ConnectionRegistry.set_default(backend, default_name)
            
            return connection
            
        else:
            # For future backends, we would create the connection here
            # For now, raise an error for unsupported backends
            raise ValueError(f"Backend '{backend}' found but connection creation not yet implemented")


class SurrealEngineSyncConnection:
    """Synchronous connection manager for SurrealDB.

    This class manages the synchronous connection to a SurrealDB database, providing methods
    for connecting, disconnecting, and executing transactions. It also provides
    access to the database through the db property.

    Attributes:
        url: The URL of the SurrealDB server
        namespace: The namespace to use
        database: The database to use
        username: The username for authentication
        password: The password for authentication
        client: The SurrealDB sync client instance
    """

    def __init__(self, url: Optional[str] = None, namespace: Optional[str] = None, 
                 database: Optional[str] = None, username: Optional[str] = None, 
                 password: Optional[str] = None, name: Optional[str] = None,
                 make_default: bool = False) -> None:
        """Initialize a new SurrealEngineSyncConnection.

        Args:
            url: The URL of the SurrealDB server
            namespace: The namespace to use
            database: The database to use
            username: The username for authentication
            password: The password for authentication
            name: The name to register this connection under in the registry
            make_default: Whether to set this connection as the default
        """
        self.url = url
        self.namespace = namespace
        self.database = database
        self.username = username
        self.password = password
        self.client = None

        if name:
            ConnectionRegistry.add_sync_connection(name, self)
        if make_default or name is None:
            ConnectionRegistry.set_default_sync_connection(self)

    def __enter__(self) -> 'SurrealEngineSyncConnection':
        """Enter the sync context manager.

        Returns:
            The connection instance
        """
        self.connect()
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], 
                exc_val: Optional[BaseException], 
                exc_tb: Optional[Any]) -> None:
        """Exit the sync context manager.

        Args:
            exc_type: The exception type, if an exception was raised
            exc_val: The exception value, if an exception was raised
            exc_tb: The exception traceback, if an exception was raised
        """
        self.disconnect()

    @property
    def db(self) -> SurrealEngine:
        """Get dynamic table accessor.

        Returns:
            A SurrealEngine instance for accessing tables dynamically
        """
        return SurrealEngine(self)

    def connect(self) -> Any:
        """Connect to the database.

        This method creates a new client if one doesn't exist, signs in if
        credentials are provided, and sets the namespace and database.

        Returns:
            The SurrealDB client instance
        """
        if not self.client:
            # Create the client directly
            self.client = surrealdb.Surreal(self.url)

            # Sign in if credentials are provided
            if self.username and self.password:
                self.client.signin({"username": self.username, "password": self.password})

            # Use namespace and database
            if self.namespace and self.database:
                self.client.use(self.namespace, self.database)

        return self.client

    def disconnect(self) -> None:
        """Disconnect from the database.

        This method closes the client connection if one exists.
        """
        if self.client:
            self.client.close()
            self.client = None

    def transaction(self, callables: list) -> list:
        """Execute multiple operations in a transaction.

        This method executes a list of callables within a transaction,
        committing the transaction if all operations succeed or canceling
        it if any operation fails.

        Args:
            callables: List of callables to execute in the transaction

        Returns:
            List of results from the callables

        Raises:
            Exception: If any operation in the transaction fails
        """
        self.client.query("BEGIN TRANSACTION;")
        try:
            results = []
            for func in callables:
                result = func()
                results.append(result)
            self.client.query("COMMIT TRANSACTION;")
            return results
        except Exception as e:
            self.client.query("CANCEL TRANSACTION;")
            raise e
