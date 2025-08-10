import json
import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union, Type, cast, TypeVar, Generic
from .exceptions import MultipleObjectsReturned, DoesNotExist
from .types import IdType, DatabaseValue, QueryCondition, QueryConditions
from surrealdb import RecordID
from .pagination import PaginationResult

# Type variable for generic QuerySet
T = TypeVar('T')  # For generic document types

# Set up logging
logger = logging.getLogger(__name__)

# Import these at runtime to avoid circular imports
def _get_connection_classes():
    from .connection import SurrealEngineAsyncConnection, SurrealEngineSyncConnection
    return SurrealEngineAsyncConnection, SurrealEngineSyncConnection

class BaseQuerySet:
    """Base query builder for SurrealDB.

    This class provides the foundation for building queries in SurrealDB.
    It includes methods for filtering, limiting, ordering, and retrieving results.
    Subclasses must implement specific methods like _build_query, all, and count.

    Attributes:
        connection: The database connection to use for queries
        query_parts: List of query conditions (field, operator, value)
        limit_value: Maximum number of results to return
        start_value: Number of results to skip (for pagination)
        order_by_value: Field and direction to order results by
        group_by_fields: Fields to group results by
        split_fields: Fields to split results by
        fetch_fields: Fields to fetch related records for
        with_index: Index to use for the query
    """

    def __init__(self, connection: Any) -> None:
        """Initialize a new BaseQuerySet.

        Args:
            connection: The database connection to use for queries
        """
        self.connection = connection
        self.query_parts: QueryConditions = []
        self.limit_value: Optional[int] = None
        self.start_value: Optional[int] = None
        self.order_by_value: Optional[Tuple[str, str]] = None
        self.group_by_fields: List[str] = []
        self.split_fields: List[str] = []
        self.fetch_fields: List[str] = []
        self.with_index: Optional[str] = None
        # Performance optimization attributes
        self._bulk_id_selection: Optional[List[IdType]] = None
        self._id_range_selection: Optional[Tuple[IdType, IdType, bool]] = None
        self._prefer_direct_access: bool = False
        # Retry configuration
        self._retry_attempts: int = 3
        self._retry_delay: float = 1.0
        self._retry_backoff_multiplier: float = 2.0
        self._retry_max_delay: float = 30.0

    def is_async_connection(self) -> bool:
        """Check if the connection is asynchronous.

        Returns:
            True if the connection is asynchronous, False otherwise
        """
        SurrealEngineAsyncConnection, SurrealEngineSyncConnection = _get_connection_classes()
        return isinstance(self.connection, SurrealEngineAsyncConnection)

    def filter(self, *expressions, query=None, **kwargs) -> 'BaseQuerySet':
        """Add filter conditions to the query with automatic ID optimization.

        This method supports multiple query syntaxes:
        1. Pythonic expressions: filter(User.age > 18, User.active == True)
        2. Django-style kwargs: filter(age__gt=18, active=True)
        3. Q objects: filter(Q(age__gt=18) & Q(active=True))
        4. Mixed: filter(User.age > 18, active=True)

        Django-style field lookups with double-underscore operators:
        - field__gt: Greater than
        - field__lt: Less than
        - field__gte: Greater than or equal
        - field__lte: Less than or equal
        - field__ne: Not equal
        - field__in: Inside (for arrays) - optimized for ID fields
        - field__nin: Not inside (for arrays)
        - field__contains: Contains (for strings or arrays)
        - field__startswith: Starts with (for strings)
        - field__endswith: Ends with (for strings)
        - field__regex: Matches regex pattern (for strings)

        PERFORMANCE OPTIMIZATIONS:
        - id__in automatically uses direct record access syntax
        - ID range queries (id__gte + id__lte) use range syntax

        Args:
            query: Q object or QueryExpression for complex queries
            **kwargs: Field names and values to filter by

        Returns:
            The query set instance for method chaining

        Raises:
            ValueError: If an unknown operator is provided
        """
        # Process Pythonic expressions and Q objects first
        for expr in expressions:
            # Import here to avoid circular imports
            try:
                from .query_expressions import Q, QueryExpression
                from .query_expressions_pythonic import FieldExpression, CompoundExpression, is_pythonic_expression
                
                # Check for Q objects in expressions (for backward compatibility)
                if isinstance(expr, Q):
                    where_clause = expr.to_where_clause()
                    if where_clause:
                        self.query_parts.append(('__raw__', '=', where_clause))
                
                elif isinstance(expr, FieldExpression):
                    # Convert to internal query condition
                    condition = expr.to_query_condition()
                    self.query_parts.append(condition)
                    
                elif isinstance(expr, CompoundExpression):
                    # Convert compound expression to Q object and use its WHERE clause
                    q_obj = expr.to_q_object()
                    where_clause = q_obj.to_where_clause()
                    if where_clause:
                        self.query_parts.append(('__raw__', '=', where_clause))
                            
                elif is_pythonic_expression(expr):
                    # Generic check for any pythonic expression
                    if hasattr(expr, 'to_query_condition'):
                        condition = expr.to_query_condition()
                        self.query_parts.append(condition)
                    elif hasattr(expr, 'to_q_object'):
                        q_obj = expr.to_q_object()
                        where_clause = q_obj.to_where_clause()
                        if where_clause:
                            self.query_parts.append(('__raw__', '=', where_clause))
                                
            except ImportError:
                # If expressions not available, skip
                pass
        
        # Handle Q objects and QueryExpressions
        if query is not None:
            # Import here to avoid circular imports
            try:
                from .query_expressions import Q, QueryExpression
                
                if isinstance(query, Q):
                    # Use Q object's WHERE clause directly to preserve OR/AND logic
                    where_clause = query.to_where_clause()
                    if where_clause:
                        self.query_parts.append(('__raw__', '=', where_clause))
                    return self
                
                elif isinstance(query, QueryExpression):
                    # Apply QueryExpression to this queryset
                    return query.apply_to_queryset(self)
                
                else:
                    raise ValueError(f"Unsupported query type: {type(query)}")
                    
            except ImportError:
                raise ValueError("Query expressions not available")
        
        # Continue with existing kwargs processing if no query object
        # PERFORMANCE OPTIMIZATION: Check for bulk ID operations
        if len(kwargs) == 1 and 'id__in' in kwargs:
            clone = self._clone()
            clone._bulk_id_selection = kwargs['id__in']
            return clone
        
        # PERFORMANCE OPTIMIZATION: Check for ID range operations  
        id_range_keys = {k for k in kwargs.keys() if k.startswith('id__') and k.endswith(('gte', 'lte', 'gt', 'lt'))}
        if len(kwargs) == 2 and len(id_range_keys) == 2:
            clone = self._clone()
            if 'id__gte' in kwargs and 'id__lte' in kwargs:
                clone._id_range_selection = (kwargs['id__gte'], kwargs['id__lte'], True)  # inclusive
                return clone
            elif 'id__gt' in kwargs and 'id__lt' in kwargs:
                clone._id_range_selection = (kwargs['id__gt'], kwargs['id__lt'], False)  # exclusive
                return clone
        
        # Fall back to regular filtering for non-optimizable queries
        for k, v in kwargs.items():
            if k == 'id':
                if isinstance(v, RecordID):
                    self.query_parts.append((k, '=', str(v)))
                elif isinstance(v, str) and ':' in v:
                    # Handle full record ID format (collection:id)
                    self.query_parts.append((k, '=', v))
                else:
                    # Handle short ID format - check backend type
                    backend = getattr(self, 'backend', None)
                    if backend and hasattr(backend, '__class__') and ('Redis' in backend.__class__.__name__ or 'ClickHouse' in backend.__class__.__name__):
                        # For Redis and ClickHouse backends, use ID as-is (no collection prefix)
                        self.query_parts.append((k, '=', v))
                    else:
                        # For SurrealDB and other backends, prefix with collection name
                        collection = getattr(self, 'document_class', None)
                        if collection:
                            full_id = f"{collection._get_collection_name()}:{v}"
                            self.query_parts.append((k, '=', full_id))
                        else:
                            self.query_parts.append((k, '=', v))
                continue

            parts = k.split('__')
            field = parts[0]

            # Handle operators
            if len(parts) > 1:
                op = parts[1]
                if op == 'gt':
                    self.query_parts.append((field, '>', v))
                elif op == 'lt':
                    self.query_parts.append((field, '<', v))
                elif op == 'gte':
                    self.query_parts.append((field, '>=', v))
                elif op == 'lte':
                    self.query_parts.append((field, '<=', v))
                elif op == 'ne':
                    self.query_parts.append((field, '!=', v))
                elif op == 'in':
                    # Note: id__in is handled by optimization above
                    self.query_parts.append((field, 'INSIDE', v))
                elif op == 'nin':
                    self.query_parts.append((field, 'NOT INSIDE', v))
                elif op == 'contains':
                    # Delegate to backend-specific condition building
                    self.query_parts.append((field, 'CONTAINS', v))
                elif op == 'startswith':
                    # Delegate to backend-specific condition building
                    self.query_parts.append((field, 'STARTSWITH', v))
                elif op == 'endswith':
                    # Delegate to backend-specific condition building
                    self.query_parts.append((field, 'ENDSWITH', v))
                elif op == 'regex':
                    # Delegate to backend-specific condition building
                    self.query_parts.append((field, 'REGEX', v))
                else:
                    # Handle nested field access for DictFields
                    document_class = getattr(self, 'document_class', None)
                    if document_class and hasattr(document_class, '_fields'):
                        if field in document_class._fields:
                            from .fields import DictField
                            if isinstance(document_class._fields[field], DictField):
                                nested_field = f"{field}.{op}"
                                self.query_parts.append((nested_field, '=', v))
                                continue

                    # If we get here, it's an unknown operator
                    raise ValueError(f"Unknown operator: {op}")
            else:
                # Simple equality
                self.query_parts.append((field, '=', v))

        return self

    def limit(self, value: int) -> 'BaseQuerySet':
        """Set the maximum number of results to return.

        Args:
            value: Maximum number of results

        Returns:
            The query set instance for method chaining
        """
        self.limit_value = value
        return self

    def start(self, value: int) -> 'BaseQuerySet':
        """Set the number of results to skip (for pagination).

        Args:
            value: Number of results to skip

        Returns:
            The query set instance for method chaining
        """
        self.start_value = value
        return self

    def order_by(self, field: str, direction: str = 'ASC') -> 'BaseQuerySet':
        """Set the field and direction to order results by.

        Args:
            field: Field name to order by
            direction: Direction to order by ('ASC' or 'DESC')

        Returns:
            The query set instance for method chaining
        """
        self.order_by_value = (field, direction)
        return self

    def group_by(self, *fields: str) -> 'BaseQuerySet':
        """Group the results by the specified fields.

        This method sets the fields to group the results by using the GROUP BY clause.

        Args:
            *fields: Field names to group by

        Returns:
            The query set instance for method chaining
        """
        self.group_by_fields.extend(fields)
        return self

    def split(self, *fields: str) -> 'BaseQuerySet':
        """Split the results by the specified fields.

        This method sets the fields to split the results by using the SPLIT clause.

        Args:
            *fields: Field names to split by

        Returns:
            The query set instance for method chaining
        """
        self.split_fields.extend(fields)
        return self

    def fetch(self, *fields: str) -> 'BaseQuerySet':
        """Fetch related records for the specified fields.

        This method sets the fields to fetch related records for using the FETCH clause.

        Args:
            *fields: Field names to fetch related records for

        Returns:
            The query set instance for method chaining
        """
        self.fetch_fields.extend(fields)
        return self

    def get_many(self, ids: List[IdType]) -> 'BaseQuerySet':
        """Get multiple records by IDs using optimized direct record access.
        
        This method uses SurrealDB's direct record selection syntax for better
        performance compared to WHERE clause filtering.
        
        Args:
            ids: List of record IDs (can be strings or other ID types)
            
        Returns:
            The query set instance configured for direct record access
            
        Example:
            # Efficient: SELECT * FROM users:1, users:2, users:3
            users = await User.objects.get_many([1, 2, 3]).all()
            users = await User.objects.get_many(['users:1', 'users:2']).all()
        """
        clone = self._clone()
        clone._bulk_id_selection = ids
        return clone
    
    def get_range(self, start_id: IdType, end_id: IdType, 
                  inclusive: bool = True) -> 'BaseQuerySet':
        """Get a range of records by ID using optimized range syntax.
        
        This method uses SurrealDB's range selection syntax for better
        performance compared to WHERE clause filtering.
        
        Args:
            start_id: Starting ID of the range
            end_id: Ending ID of the range  
            inclusive: Whether the range is inclusive (default: True)
            
        Returns:
            The query set instance configured for range access
            
        Example:
            # Efficient: SELECT * FROM users:100..=200
            users = await User.objects.get_range(100, 200).all()
            users = await User.objects.get_range('users:100', 'users:200', inclusive=False).all()
        """
        clone = self._clone()
        clone._id_range_selection = (start_id, end_id, inclusive)
        return clone


    def with_index(self, index: str) -> 'BaseQuerySet':
        """Use the specified index for the query.

        This method sets the index to use for the query using the WITH clause.

        Args:
            index: Name of the index to use

        Returns:
            The query set instance for method chaining
        """
        self.with_index = index
        return self
    
    def use_direct_access(self) -> 'BaseQuerySet':
        """Mark this queryset to prefer direct record access when possible.
        
        This method sets a preference for using direct record access patterns
        over WHERE clause filtering for better performance.
        
        Returns:
            The query set instance for method chaining
        """
        clone = self._clone()
        clone._prefer_direct_access = True
        return clone

    def _build_query(self) -> str:
        """Build the base query string.

        This method must be implemented by subclasses to generate the appropriate
        query string for the specific database operation.

        Returns:
            The query string

        Raises:
            NotImplementedError: If not implemented by a subclass
        """
        raise NotImplementedError("Subclasses must implement _build_query")

    def _build_conditions(self) -> List[str]:
        """Build query conditions from query_parts.

        This method converts the query_parts list into a list of condition strings
        that can be used in a WHERE clause. It now delegates to backend-specific
        condition building when available.

        Returns:
            List of condition strings
        """
        conditions = []
        
        # Try to get backend for condition building
        backend = None
        if hasattr(self, '_get_backend'):
            try:
                backend = self._get_backend()
            except Exception:
                pass  # Fall back to legacy approach
        
        for field, op, value in self.query_parts:
            # Handle raw query conditions
            if field == '__raw__':
                conditions.append(value)
                continue
            # Handle special cases
            elif op == '=' and isinstance(field, str) and '::' in field:
                conditions.append(f"{field}")
            # Use backend-specific condition building if available
            elif backend and hasattr(backend, 'build_condition'):
                try:
                    condition = backend.build_condition(field, op, value)
                    conditions.append(condition)
                    continue
                except Exception:
                    pass  # Fall back to legacy approach
            
            # Legacy condition building for backward compatibility
            # Special handling for RecordIDs - don't quote them
            if field == 'id' and isinstance(value, str) and ':' in value:
                conditions.append(f"{field} {op} {value}")
            # Special handling for INSIDE and NOT INSIDE operators
            elif isinstance(value, RecordID) or (isinstance(value, str) and ':' in field):
                conditions.append(f"{field} {op} {value}")
            elif op in ('INSIDE', 'NOT INSIDE'):
                value_str = json.dumps(value)
                conditions.append(f"{field} {op} {value_str}")
            # For compatibility with old operator names - these should be converted to lowercase
            elif op == 'STARTSWITH':
                conditions.append(f"string::starts_with({field}, '{value}')")
            elif op == 'ENDSWITH':
                conditions.append(f"string::ends_with({field}, '{value}')")
            elif op == 'CONTAINS':
                if isinstance(value, str):
                    conditions.append(f"string::contains({field}, '{value}')")
                else:
                    conditions.append(f"{field} CONTAINS {json.dumps(value)}")
            else:
                # Convert value to database format if we have field information
                db_value = self._convert_value_for_query(field, value)
                conditions.append(f"{field} {op} {json.dumps(db_value)}")
        return conditions

    def _convert_value_for_query(self, field_name: str, value: Any) -> Any:
        """Convert a value to its database representation for query conditions.
        
        This method checks if the document class has a field definition for the given
        field name and uses its to_db() method to convert the value properly.
        
        Args:
            field_name: The name of the field
            value: The value to convert
            
        Returns:
            The converted value ready for JSON serialization
        """
        # Check if we have a document class with field definitions
        document_class = getattr(self, 'document_class', None)
        if document_class and hasattr(document_class, '_fields'):
            # Get the field definition
            field_obj = document_class._fields.get(field_name)
            if field_obj and hasattr(field_obj, 'to_db'):
                # Use the field's to_db method to convert the value
                try:
                    return field_obj.to_db(value)
                except Exception:
                    # If conversion fails, return the original value
                    pass
        
        # If no field definition or conversion failed, return original value
        return value

    def _format_record_id(self, id_value: IdType) -> str:
        """Format an ID value into a proper SurrealDB record ID.
        
        Args:
            id_value: The ID value to format
            
        Returns:
            Properly formatted record ID string
        """
        # If it's already a full record ID (contains colon), use as-is
        if isinstance(id_value, str) and ':' in id_value:
            return id_value
            
        # If it's a RecordID object, convert to string
        if isinstance(id_value, RecordID):
            return str(id_value)
            
        # Otherwise, add collection name prefix
        collection_name = getattr(self, 'document_class', None)
        if collection_name:
            collection_name = collection_name._get_collection_name()
            return f"{collection_name}:{id_value}"
        else:
            return str(id_value)
    
    def _build_direct_record_query(self) -> Optional[str]:
        """Build optimized direct record access query if applicable.
        
        Returns:
            Optimized query string or None if not applicable
        """
        # Handle bulk ID selection optimization
        if self._bulk_id_selection:
            if not self._bulk_id_selection:  # Empty list
                return None
            
            record_ids = [self._format_record_id(id_val) for id_val in self._bulk_id_selection]
            query = f"SELECT * FROM {', '.join(record_ids)}"
            
            # Add other clauses (but skip WHERE since we're using direct access)
            clauses = self._build_clauses()
            for clause_name, clause_sql in clauses.items():
                if clause_name != 'WHERE':  # Skip WHERE for direct access
                    query += f" {clause_sql}"
            
            return query
            
        # Handle ID range selection optimization  
        if self._id_range_selection:
            start_id, end_id, inclusive = self._id_range_selection
            
            start_record_id = self._format_record_id(start_id)
            end_record_id = self._format_record_id(end_id)
            
            # Extract just the numeric part for range syntax
            collection_name = getattr(self, 'document_class', None)
            if collection_name:
                collection_name = collection_name._get_collection_name()
                
                # Extract numeric IDs from record IDs
                start_num = str(start_id).split(':')[-1] if ':' in str(start_id) else str(start_id)
                end_num = str(end_id).split(':')[-1] if ':' in str(end_id) else str(end_id)
                
                range_op = "..=" if inclusive else ".."
                query = f"SELECT * FROM {collection_name}:{start_num}{range_op}{end_num}"
            else:
                # Fall back to WHERE clause if we can't determine collection
                return None
            
            # Add other clauses (but skip WHERE since we're using direct access)
            clauses = self._build_clauses()
            for clause_name, clause_sql in clauses.items():
                if clause_name != 'WHERE':  # Skip WHERE for direct access
                    query += f" {clause_sql}"
            
            return query
            
        return None

    def _build_clauses(self) -> Dict[str, str]:
        """Build query clauses from the query parameters.

        This method builds the various clauses for the query string, including
        WHERE, GROUP BY, SPLIT, FETCH, WITH, ORDER BY, LIMIT, and START.

        Returns:
            Dictionary of clause names and their string representations
        """
        clauses = {}

        # Build WHERE clause
        if self.query_parts:
            conditions = self._build_conditions()
            clauses['WHERE'] = f"WHERE {' AND '.join(conditions)}"

        # Build GROUP BY clause
        if self.group_by_fields:
            clauses['GROUP BY'] = f"GROUP BY {', '.join(self.group_by_fields)}"

        # Build SPLIT clause
        if self.split_fields:
            clauses['SPLIT'] = f"SPLIT {', '.join(self.split_fields)}"

        # Build FETCH clause
        if self.fetch_fields:
            clauses['FETCH'] = f"FETCH {', '.join(self.fetch_fields)}"

        # Build WITH clause
        if self.with_index:
            clauses['WITH'] = f"WITH INDEX {self.with_index}"

        # Build ORDER BY clause
        if self.order_by_value:
            field, direction = self.order_by_value
            clauses['ORDER BY'] = f"ORDER BY {field} {direction}"

        # Build LIMIT clause
        if self.limit_value is not None:
            clauses['LIMIT'] = f"LIMIT {self.limit_value}"

        # Build START clause
        if self.start_value is not None:
            clauses['START'] = f"START {self.start_value}"

        return clauses
    
    def _get_collection_name(self) -> Optional[str]:
        """Get the collection name for this queryset.
        
        Returns:
            Collection name or None if not available
        """
        document_class = getattr(self, 'document_class', None)
        if document_class and hasattr(document_class, '_get_collection_name'):
            return document_class._get_collection_name()
        return getattr(self, 'table_name', None)

    def configure_retry(self, attempts: int = 3, delay: float = 1.0, 
                       backoff_multiplier: float = 2.0, max_delay: float = 30.0) -> 'BaseQuerySet':
        """Configure retry parameters for this queryset.
        
        Args:
            attempts: Maximum number of retry attempts (default: 3)
            delay: Initial delay between retries in seconds (default: 1.0)
            backoff_multiplier: Multiplier for exponential backoff (default: 2.0)
            max_delay: Maximum delay between retries in seconds (default: 30.0)
            
        Returns:
            The queryset instance for method chaining
            
        Example:
            # Retry up to 5 times with exponential backoff
            users = await User.objects.configure_retry(attempts=5, delay=0.5).all()
        """
        self._retry_attempts = max(1, attempts)
        self._retry_delay = max(0.1, delay)
        self._retry_backoff_multiplier = max(1.0, backoff_multiplier)
        self._retry_max_delay = max(delay, max_delay)
        return self

    def _is_transient_error(self, error: Exception) -> bool:
        """Check if an error is transient and worth retrying.
        
        Args:
            error: The exception to check
            
        Returns:
            True if the error appears to be transient
        """
        error_msg = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Common transient error indicators
        transient_indicators = [
            'connection', 'timeout', 'unavailable', 'temporary', 
            'retry', 'deadlock', 'lock', 'busy', 'overloaded',
            'rate limit', 'throttl', 'too many', 'service unavailable',
            'network', 'socket', 'broken pipe', 'reset by peer',
            'read timeout', 'write timeout', 'connect timeout'
        ]
        
        # Common transient exception types
        transient_types = [
            'connectionerror', 'timeouterror', 'networkerror',
            'temporaryerror', 'retryableerror', 'deadlockdetected'
        ]
        
        # Check error message
        for indicator in transient_indicators:
            if indicator in error_msg:
                return True
                
        # Check error type
        for error_type_indicator in transient_types:
            if error_type_indicator in error_type:
                return True
                
        # SurrealDB specific transient errors
        if 'surrealdb' in error_msg and any(word in error_msg for word in 
                                           ['connection', 'network', 'timeout']):
            return True
            
        # ClickHouse specific transient errors
        if any(indicator in error_msg for indicator in [
            'clickhouse', 'too many simultaneous queries',
            'database is readonly', 'memory limit', 'query quota exceeded',
            'table is read-only', 'node is readonly'
        ]):
            return True
            
        # Check for specific exception types that are often transient
        if any(exc_type in error_type for exc_type in [
            'operationalerror', 'interfaceerror', 'databaseerror'
        ]):
            return True
            
        return False

    async def _execute_with_retry(self, operation_name: str, operation_func, *args, **kwargs):
        """Execute an operation with automatic retry on transient failures.
        
        Args:
            operation_name: Name of the operation for logging
            operation_func: The async function to execute
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            The result of the operation
            
        Raises:
            The last exception if all retry attempts fail
        """
        last_exception = None
        current_delay = self._retry_delay
        
        for attempt in range(self._retry_attempts):
            try:
                if attempt > 0:
                    logger.info(f"Retrying {operation_name} (attempt {attempt + 1}/{self._retry_attempts})")
                
                # Execute the operation
                return await operation_func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                # Check if this is the last attempt
                if attempt + 1 >= self._retry_attempts:
                    logger.error(f"All retry attempts failed for {operation_name}. Final error: {e}")
                    break
                
                # Check if error is worth retrying
                if not self._is_transient_error(e):
                    logger.warning(f"Non-transient error in {operation_name}, not retrying: {e}")
                    break
                
                # Log the retry
                logger.warning(f"Transient error in {operation_name} (attempt {attempt + 1}), "
                             f"retrying in {current_delay:.1f}s: {e}")
                
                # Wait before retrying
                await asyncio.sleep(current_delay)
                
                # Calculate next delay with exponential backoff
                current_delay = min(
                    current_delay * self._retry_backoff_multiplier,
                    self._retry_max_delay
                )
        
        # If we get here, all retries failed
        raise last_exception

    def _execute_with_retry_sync(self, operation_name: str, operation_func, *args, **kwargs):
        """Execute an operation with automatic retry on transient failures (synchronous version).
        
        Args:
            operation_name: Name of the operation for logging
            operation_func: The sync function to execute
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            The result of the operation
            
        Raises:
            The last exception if all retry attempts fail
        """
        last_exception = None
        current_delay = self._retry_delay
        
        for attempt in range(self._retry_attempts):
            try:
                if attempt > 0:
                    logger.info(f"Retrying {operation_name} (attempt {attempt + 1}/{self._retry_attempts})")
                
                # Execute the operation (synchronous)
                return operation_func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                # Check if this is the last attempt
                if attempt + 1 >= self._retry_attempts:
                    logger.error(f"All retry attempts failed for {operation_name}. Final error: {e}")
                    break
                
                # Check if error is worth retrying
                if not self._is_transient_error(e):
                    logger.warning(f"Non-transient error in {operation_name}, not retrying: {e}")
                    break
                
                # Log the retry
                logger.warning(f"Transient error in {operation_name} (attempt {attempt + 1}), "
                             f"retrying in {current_delay:.1f}s: {e}")
                
                # Wait before retrying (synchronous sleep)
                time.sleep(current_delay)
                
                # Calculate next delay with exponential backoff
                current_delay = min(
                    current_delay * self._retry_backoff_multiplier,
                    self._retry_max_delay
                )
        
        # If we get here, all retries failed
        raise last_exception

    async def all(self) -> List[Any]:
        """Execute the query and return all results asynchronously.

        This method must be implemented by subclasses to execute the query
        and return the results.

        Returns:
            List of results

        Raises:
            NotImplementedError: If not implemented by a subclass
        """
        raise NotImplementedError("Subclasses must implement all")

    def all_sync(self) -> List[Any]:
        """Execute the query and return all results synchronously.

        This method must be implemented by subclasses to execute the query
        and return the results.

        Returns:
            List of results

        Raises:
            NotImplementedError: If not implemented by a subclass
        """
        raise NotImplementedError("Subclasses must implement all_sync")

    async def first(self) -> Optional[Any]:
        """Execute the query and return the first result asynchronously.

        This method limits the query to one result and returns the first item
        or None if no results are found.

        Returns:
            The first result or None if no results
        """
        self.limit_value = 1
        results = await self.all()
        return results[0] if results else None

    def first_sync(self) -> Optional[Any]:
        """Execute the query and return the first result synchronously.

        This method limits the query to one result and returns the first item
        or None if no results are found.

        Returns:
            The first result or None if no results
        """
        self.limit_value = 1
        results = self.all_sync()
        return results[0] if results else None

    async def get(self, **kwargs) -> Any:
        """Get a single document matching the query asynchronously.

        This method applies filters and ensures that exactly one document is returned.
        For ID-based lookups, it uses direct record syntax instead of WHERE clause.

        Args:
            **kwargs: Field names and values to filter by

        Returns:
            The matching document

        Raises:
            DoesNotExist: If no matching document is found
            MultipleObjectsReturned: If multiple matching documents are found
        """
        # Special handling for ID-based lookup
        if len(kwargs) == 1 and 'id' in kwargs:
            id_value = kwargs['id']
            # If it's already a full record ID (table:id format)
            if isinstance(id_value, str) and ':' in id_value:
                query = f"SELECT * FROM {id_value}"
            else:
                # Get table name from document class if available
                table_name = getattr(self, 'document_class', None)
                if table_name:
                    table_name = table_name._get_collection_name()
                else:
                    table_name = getattr(self, 'table_name', None)

                if table_name:
                    query = f"SELECT * FROM {table_name}:{id_value}"
                else:
                    # Fall back to regular filtering if we can't determine the table
                    return await self._get_with_filters(**kwargs)

            result = await self.connection.client.query(query)
            if not result or not result[0]:
                raise DoesNotExist(f"Object with ID '{id_value}' does not exist.")
            return result[0][0]

        # For non-ID lookups, use regular filtering
        return await self._get_with_filters(**kwargs)

    def get_sync(self, **kwargs) -> Any:
        """Get a single document matching the query synchronously.

        This method applies filters and ensures that exactly one document is returned.
        For ID-based lookups, it uses direct record syntax instead of WHERE clause.

        Args:
            **kwargs: Field names and values to filter by

        Returns:
            The matching document

        Raises:
            DoesNotExist: If no matching document is found
            MultipleObjectsReturned: If multiple matching documents are found
        """
        # Special handling for ID-based lookup
        if len(kwargs) == 1 and 'id' in kwargs:
            id_value = kwargs['id']
            # If it's already a full record ID (table:id format)
            if isinstance(id_value, str) and ':' in id_value:
                query = f"SELECT * FROM {id_value}"
            else:
                # Get table name from document class if available
                table_name = getattr(self, 'document_class', None)
                if table_name:
                    table_name = table_name._get_collection_name()
                else:
                    table_name = getattr(self, 'table_name', None)

                if table_name:
                    query = f"SELECT * FROM {table_name}:{id_value}"
                else:
                    # Fall back to regular filtering if we can't determine the table
                    return self._get_with_filters_sync(**kwargs)

            result = self.connection.client.query(query)
            if not result or not result[0]:
                raise DoesNotExist(f"Object with ID '{id_value}' does not exist.")
            return result[0][0]

        # For non-ID lookups, use regular filtering
        return self._get_with_filters_sync(**kwargs)

    async def _get_with_filters(self, **kwargs) -> Any:
        """Internal method to get a single document using filters asynchronously.

        Args:
            **kwargs: Field names and values to filter by

        Returns:
            The matching document

        Raises:
            DoesNotExist: If no matching document is found
            MultipleObjectsReturned: If multiple matching documents are found
        """
        self.filter(**kwargs)
        self.limit_value = 2  # Get 2 to check for multiple
        results = await self.all()

        if not results:
            raise DoesNotExist(f"Object matching query does not exist.")
        if len(results) > 1:
            raise MultipleObjectsReturned(f"Multiple objects returned instead of one")

        return results[0]

    def _get_with_filters_sync(self, **kwargs) -> Any:
        """Internal method to get a single document using filters synchronously.

        Args:
            **kwargs: Field names and values to filter by

        Returns:
            The matching document

        Raises:
            DoesNotExist: If no matching document is found
            MultipleObjectsReturned: If multiple matching documents are found
        """
        self.filter(**kwargs)
        self.limit_value = 2  # Get 2 to check for multiple
        results = self.all_sync()

        if not results:
            raise DoesNotExist(f"Object matching query does not exist.")
        if len(results) > 1:
            raise MultipleObjectsReturned(f"Multiple objects returned instead of one")

        return results[0]

    async def count(self) -> int:
        """Count documents matching the query asynchronously.

        This method must be implemented by subclasses to count the number
        of documents matching the query.

        Returns:
            Number of matching documents

        Raises:
            NotImplementedError: If not implemented by a subclass
        """
        raise NotImplementedError("Subclasses must implement count")

    def count_sync(self) -> int:
        """Count documents matching the query synchronously.

        This method must be implemented by subclasses to count the number
        of documents matching the query.

        Returns:
            Number of matching documents

        Raises:
            NotImplementedError: If not implemented by a subclass
        """
        raise NotImplementedError("Subclasses must implement count_sync")

    def __await__(self):
        """Make the queryset awaitable.

        This method allows the queryset to be used with the await keyword,
        which will execute the query and return all results.

        Returns:
            Awaitable that resolves to the query results
        """
        return self.all().__await__()

    def page(self, number: int, size: int) -> 'BaseQuerySet':
        """Set pagination parameters using page number and size.

        This method calculates the appropriate LIMIT and START values
        based on the page number and size, providing a more convenient
        way to paginate results.

        Args:
            number: Page number (1-based, first page is 1)
            size: Number of items per page

        Returns:
            The query set instance for method chaining
        """
        if number < 1:
            raise ValueError("Page number must be 1 or greater")
        if size < 1:
            raise ValueError("Page size must be 1 or greater")

        self.limit_value = size
        self.start_value = (number - 1) * size
        return self

    async def paginate(self, page: int, per_page: int) -> PaginationResult:
        """Get a page of results with pagination metadata asynchronously.

        This method gets a page of results along with metadata about the
        pagination, such as the total number of items, the number of pages,
        and whether there are next or previous pages.

        Args:
            page: The page number (1-based)
            per_page: The number of items per page

        Returns:
            A PaginationResult containing the items and pagination metadata
        """
        # Get the total count
        total = await self.count()

        # Get the items for the current page
        items = await self.page(page, per_page).all()

        # Return a PaginationResult
        return PaginationResult(items, page, per_page, total)

    def paginate_sync(self, page: int, per_page: int) -> PaginationResult:
        """Get a page of results with pagination metadata synchronously.

        This method gets a page of results along with metadata about the
        pagination, such as the total number of items, the number of pages,
        and whether there are next or previous pages.

        Args:
            page: The page number (1-based)
            per_page: The number of items per page

        Returns:
            A PaginationResult containing the items and pagination metadata
        """
        # Get the total count
        total = self.count_sync()

        # Get the items for the current page
        items = self.page(page, per_page).all_sync()

        # Return a PaginationResult
        return PaginationResult(items, page, per_page, total)

    def get_raw_query(self) -> str:
        """Get the raw query string without executing it.

        This method builds and returns the query string without executing it.
        It can be used to get the raw query for manual execution or debugging.

        Returns:
            The raw query string
        """
        return self._build_query()

    def aggregate(self):
        """Create an aggregation pipeline from this query.

        This method returns an AggregationPipeline instance that can be used
        to build and execute complex aggregation queries with multiple stages.

        Returns:
            An AggregationPipeline instance for building and executing
            aggregation queries.
        """
        from .aggregation import AggregationPipeline
        return AggregationPipeline(self)

    def _clone(self) -> 'BaseQuerySet':
        """Create a new instance of the queryset with the same parameters.

        This method creates a new instance of the same class as the current
        instance and copies all the relevant attributes.

        Returns:
            A new queryset instance with the same parameters
        """
        # Create a new instance of the same class
        if hasattr(self, 'document_class'):
            # For QuerySet subclass
            clone = self.__class__(self.document_class, self.connection)
        elif hasattr(self, 'table_name'):
            # For SchemalessQuerySet subclass
            clone = self.__class__(self.table_name, self.connection)
        else:
            # For BaseQuerySet or other subclasses
            clone = self.__class__(self.connection)

        # Copy all the query parameters
        clone.query_parts = self.query_parts.copy()
        clone.limit_value = self.limit_value
        clone.start_value = self.start_value
        clone.order_by_value = self.order_by_value
        clone.group_by_fields = self.group_by_fields.copy()
        clone.split_fields = self.split_fields.copy()
        clone.fetch_fields = self.fetch_fields.copy()
        clone.with_index = self.with_index
        # Copy performance optimization attributes
        clone._bulk_id_selection = self._bulk_id_selection
        clone._id_range_selection = self._id_range_selection
        clone._prefer_direct_access = self._prefer_direct_access
        
        # Copy retry configuration
        clone._retry_attempts = self._retry_attempts
        clone._retry_delay = self._retry_delay
        clone._retry_backoff_multiplier = self._retry_backoff_multiplier
        clone._retry_max_delay = self._retry_max_delay

        return clone
