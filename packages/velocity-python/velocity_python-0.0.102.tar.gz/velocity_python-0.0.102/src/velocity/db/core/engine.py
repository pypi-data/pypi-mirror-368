import inspect
import sys
import re
import traceback
from functools import wraps
from velocity.db import exceptions
from velocity.db.core.transaction import Transaction

import logging

logger = logging.getLogger("velocity.db.engine")
logger.setLevel(logging.INFO)  # Or DEBUG for more verbosity


class Engine:
    """
    Encapsulates driver config, connection logic, error handling, and transaction decoration.
    """

    MAX_RETRIES = 100

    def __init__(self, driver, config, sql, connect_timeout=5):
        self.__config = config
        self.__sql = sql
        self.__driver = driver
        self.__connect_timeout = connect_timeout

    def __str__(self):
        return f"[{self.sql.server}] engine({self.config})"

    def connect(self):
        """
        Connects to the database and returns the connection object.
        If the database is missing, tries to create it, then reconnect.
        """
        try:
            conn = self.__connect()
        except exceptions.DbDatabaseMissingError:
            self.create_database()
            conn = self.__connect()
        if self.sql.server == "SQLite3":
            conn.isolation_level = None
        return conn

    def __connect(self):
        """
        Internal connection logic, raising suitable exceptions on error.
        Enforces a connect timeout and handles different config types.
        """
        server = self.sql.server.lower()
        timeout_key = "timeout" if "sqlite" in server else "connect_timeout"
        timeout_val = self.__connect_timeout

        try:
            if isinstance(self.config, dict):
                config = self.config.copy()
                if timeout_key not in config:
                    config[timeout_key] = timeout_val
                return self.driver.connect(**config)

            elif isinstance(self.config, str):
                conn_str = self.config
                if timeout_key not in conn_str:
                    conn_str += f" {timeout_key}={timeout_val}"
                return self.driver.connect(conn_str)

            elif isinstance(self.config, (tuple, list)):
                config_args = list(self.config)
                if config_args and isinstance(config_args[-1], dict):
                    if timeout_key not in config_args[-1]:
                        config_args[-1][timeout_key] = timeout_val
                else:
                    config_args.append({timeout_key: timeout_val})
                return self.driver.connect(*config_args)

            else:
                raise TypeError(
                    f"Unhandled configuration parameter type: {type(self.config)}"
                )

        except Exception:
            self.process_error()

    def transaction(self, func_or_cls=None):
        """
        Decorator that provides a Transaction. If `tx` is passed in, uses it; otherwise, creates a new one.
        May also be used to decorate a class, in which case all methods are wrapped in a transaction if they accept `tx`.
        With no arguments, returns a new Transaction directly.
        """
        # print("Transaction", func_or_cls.__name__, type(func_or_cls))

        if func_or_cls is None:
            return Transaction(self)

        if isinstance(func_or_cls, classmethod):
            return classmethod(self.transaction(func_or_cls.__func__))

        if inspect.isfunction(func_or_cls) or inspect.ismethod(func_or_cls):
            names = list(inspect.signature(func_or_cls).parameters.keys())
            # print(func_or_cls.__name__, names)
            if "_tx" in names:
                raise NameError(
                    f"In function {func_or_cls.__name__}, '_tx' is not allowed as a parameter."
                )

            @wraps(func_or_cls)
            def new_function(*args, **kwds):
                tx = None
                names = list(inspect.signature(func_or_cls).parameters.keys())

                # print("inside", func_or_cls.__name__)
                # print(names)
                # print(args, kwds)

                if "tx" not in names:
                    # The function doesn't even declare a `tx` parameter, so run normally.
                    return func_or_cls(*args, **kwds)

                if "tx" in kwds:
                    if isinstance(kwds["tx"], Transaction):
                        tx = kwds["tx"]
                    else:
                        raise TypeError(
                            f"In function {func_or_cls.__name__}, keyword argument `tx` must be a Transaction object."
                        )
                else:
                    # Might be in positional args
                    pos = names.index("tx")
                    if len(args) > pos:
                        if isinstance(args[pos], Transaction):
                            tx = args[pos]

                if tx:
                    return self.exec_function(func_or_cls, tx, *args, **kwds)

                with Transaction(self) as local_tx:
                    pos = names.index("tx")
                    new_args = args[:pos] + (local_tx,) + args[pos:]
                    return self.exec_function(func_or_cls, local_tx, *new_args, **kwds)

            return new_function

        if inspect.isclass(func_or_cls):

            NewCls = type(func_or_cls.__name__, (func_or_cls,), {})

            for attr_name in dir(func_or_cls):
                # Optionally skip special methods
                if attr_name.startswith("__") and attr_name.endswith("__"):
                    continue

                attr = getattr(func_or_cls, attr_name)

                if callable(attr):
                    setattr(NewCls, attr_name, self.transaction(attr))

            return NewCls

        return Transaction(self)

    def exec_function(self, function, _tx, *args, **kwds):
        """
        Executes the given function inside the transaction `_tx`.
        Retries if it raises DbRetryTransaction or DbLockTimeoutError, up to MAX_RETRIES times.
        """
        depth = getattr(_tx, "_exec_function_depth", 0)
        setattr(_tx, "_exec_function_depth", depth + 1)

        try:
            if depth > 0:
                # Not top-level. Just call the function.
                return function(*args, **kwds)
            else:
                retry_count = 0
                lock_timeout_count = 0
                while True:
                    try:
                        return function(*args, **kwds)
                    except exceptions.DbRetryTransaction as e:
                        retry_count += 1
                        if retry_count > self.MAX_RETRIES:
                            raise
                        _tx.rollback()
                    except exceptions.DbLockTimeoutError as e:
                        lock_timeout_count += 1
                        if lock_timeout_count > self.MAX_RETRIES:
                            raise
                        _tx.rollback()
                        continue
                    except:
                        raise
        finally:
            setattr(_tx, "_exec_function_depth", depth)
            # or if depth was 0, you might delete the attribute:
            # if depth == 0:
            #     delattr(_tx, "_exec_function_depth")

    @property
    def driver(self):
        return self.__driver

    @property
    def config(self):
        return self.__config

    @property
    def sql(self):
        return self.__sql

    @property
    def version(self):
        """
        Returns the DB server version.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.version()
            return tx.execute(sql, vals).scalar()

    @property
    def timestamp(self):
        """
        Returns the current timestamp from the DB server.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.timestamp()
            return tx.execute(sql, vals).scalar()

    @property
    def user(self):
        """
        Returns the current user as known by the DB server.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.user()
            return tx.execute(sql, vals).scalar()

    @property
    def databases(self):
        """
        Returns a list of available databases.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.databases()
            result = tx.execute(sql, vals)
            return [x[0] for x in result.as_tuple()]

    @property
    def current_database(self):
        """
        Returns the name of the current database.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.current_database()
            return tx.execute(sql, vals).scalar()

    def create_database(self, name=None):
        """
        Creates a database if it doesn't exist, or does nothing if it does.
        """
        old = None
        if name is None:
            old = self.config["database"]
            self.set_config({"database": "postgres"})
            name = old
        with Transaction(self) as tx:
            sql, vals = self.sql.create_database(name)
            tx.execute(sql, vals, single=True)
        if old:
            self.set_config({"database": old})
        return self

    def switch_to_database(self, database):
        """
        Switch the config to use a different database name, closing any existing connection.
        """
        conf = self.config
        if "database" in conf:
            conf["database"] = database
        if "dbname" in conf:
            conf["dbname"] = database
        return self

    def set_config(self, config):
        """
        Updates the internal config dictionary.
        """
        self.config.update(config)

    @property
    def schemas(self):
        """
        Returns a list of schemas in the current database.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.schemas()
            result = tx.execute(sql, vals)
            return [x[0] for x in result.as_tuple()]

    @property
    def current_schema(self):
        """
        Returns the current schema in use.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.current_schema()
            return tx.execute(sql, vals).scalar()

    @property
    def tables(self):
        """
        Returns a list of 'schema.table' for all tables in the current DB.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.tables()
            result = tx.execute(sql, vals)
            return [f"{x[0]}.{x[1]}" for x in result.as_tuple()]

    @property
    def views(self):
        """
        Returns a list of 'schema.view' for all views in the current DB.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.views()
            result = tx.execute(sql, vals)
            return [f"{x[0]}.{x[1]}" for x in result.as_tuple()]

    def process_error(self, exception, sql=None, parameters=None):
        """
        Process database errors and raise appropriate velocity exceptions.
        Enhanced for robustness with exception chaining and comprehensive error handling.
        
        Args:
            exception: The original exception from the database driver
            sql: The SQL statement that caused the error (optional)
            parameters: The parameters passed to the SQL statement (optional)
            
        Returns:
            The appropriate velocity exception to raise
        """
        logger = logging.getLogger(__name__)
        
        # Enhanced logging with context
        extra_data = {
            'exception_type': type(exception).__name__,
            'sql': sql,
            'parameters': parameters
        }
        
        logger.error(
            f"Database error caught. Attempting to transform: "
            f"type={type(exception).__name__}, sql={sql[:100] if sql else 'None'}...",
            extra=extra_data
        )
        
        # Safely get error code and message with fallbacks
        try:
            error_code = getattr(exception, 'pgcode', None) or self.get_error(exception)
        except Exception as e:
            logger.warning(f"Failed to extract error code: {e}")
            error_code = None
            
        try:
            error_message = str(exception)
        except Exception as e:
            logger.warning(f"Failed to convert exception to string: {e}")
            error_message = f"<Error converting exception: {type(exception).__name__}>"
        
        # Primary error classification by error code
        if error_code and hasattr(self, 'error_codes'):
            for error_class, codes in self.error_codes.items():
                if error_code in codes:
                    logger.info(f"Classified error by code: {error_code} -> {error_class}")
                    try:
                        return self._create_exception_with_chaining(
                            error_class, error_message, exception, sql, parameters
                        )
                    except Exception as creation_error:
                        logger.error(f"Failed to create {error_class} exception: {creation_error}")
                        # Fall through to regex classification
                        break
        
        # Secondary error classification by message patterns (regex fallback)
        error_message_lower = error_message.lower()
        
        # Enhanced connection error patterns
        connection_patterns = [
            r'connection.*refused|could not connect',
            r'network.*unreachable|network.*down',
            r'broken pipe|connection.*broken',
            r'timeout.*connection|connection.*timeout',
            r'server.*closed.*connection|connection.*lost',
            r'no route to host|host.*unreachable',
            r'connection.*reset|reset.*connection'
        ]
        
        # Enhanced duplicate key patterns  
        duplicate_patterns = [
            r'duplicate.*key.*value|unique.*constraint.*violated',
            r'duplicate.*entry|key.*already.*exists',
            r'violates.*unique.*constraint',
            r'unique.*violation|constraint.*unique'
        ]
        
        # Enhanced permission/authorization patterns
        permission_patterns = [
            r'permission.*denied|access.*denied|authorization.*failed',
            r'insufficient.*privileges|privilege.*denied',
            r'not.*authorized|unauthorized.*access',
            r'authentication.*failed|login.*failed'
        ]
        
        # Enhanced database/table not found patterns
        not_found_patterns = [
            r'database.*does.*not.*exist|unknown.*database',
            r'table.*does.*not.*exist|relation.*does.*not.*exist',
            r'no.*such.*database|database.*not.*found',
            r'schema.*does.*not.*exist|unknown.*table'
        ]
        
        # Enhanced syntax error patterns
        syntax_patterns = [
            r'syntax.*error|invalid.*syntax',
            r'malformed.*query|bad.*sql.*grammar',
            r'unexpected.*token|parse.*error'
        ]
        
        # Enhanced deadlock/timeout patterns
        deadlock_patterns = [
            r'deadlock.*detected|lock.*timeout',
            r'timeout.*waiting.*for.*lock|query.*timeout',
            r'lock.*wait.*timeout|deadlock.*found'
        ]
        
        # Comprehensive pattern matching with error class mapping
        pattern_mappings = [
            (connection_patterns, 'ConnectionError'),
            (duplicate_patterns, 'DuplicateError'), 
            (permission_patterns, 'PermissionError'),
            (not_found_patterns, 'NotFoundError'),
            (syntax_patterns, 'SyntaxError'),
            (deadlock_patterns, 'DeadlockError')
        ]
        
        # Apply pattern matching
        for patterns, error_class in pattern_mappings:
            for pattern in patterns:
                try:
                    if re.search(pattern, error_message_lower):
                        logger.info(f"Classified error by pattern: '{pattern}' -> {error_class}")
                        return self._create_exception_with_chaining(
                            error_class, error_message, exception, sql, parameters
                        )
                except re.error as regex_error:
                    logger.warning(f"Regex pattern error '{pattern}': {regex_error}")
                    continue
                except Exception as pattern_error:
                    logger.error(f"Error applying pattern '{pattern}': {pattern_error}")
                    continue
        
        # Fallback: return generic database error with full context
        logger.warning(
            f"Could not classify error. Returning generic DatabaseError. "
            f"Error code: {error_code}, Available error codes: {list(getattr(self, 'error_codes', {}).keys()) if hasattr(self, 'error_codes') else 'None'}"
        )
        
        return self._create_exception_with_chaining(
            'DatabaseError', error_message, exception, sql, parameters
        )
    
    def _create_exception_with_chaining(self, error_class, message, original_exception, sql=None, parameters=None):
        """
        Create a velocity exception with proper exception chaining.
        
        Args:
            error_class: The name of the exception class to create
            message: The error message
            original_exception: The original exception to chain
            sql: The SQL statement (optional)
            parameters: The SQL parameters (optional)
            
        Returns:
            The created exception with proper chaining
        """
        logger = logging.getLogger(__name__)
        
        try:
            # Import the exception class dynamically
            exception_module = __import__('velocity.db.exceptions', fromlist=[error_class])
            ExceptionClass = getattr(exception_module, error_class)
            
            # Create enhanced message with context
            if sql:
                enhanced_message = f"{message} (SQL: {sql[:200]}{'...' if len(sql) > 200 else ''})"
            else:
                enhanced_message = message
                
            # Create the exception with chaining
            new_exception = ExceptionClass(enhanced_message)
            new_exception.__cause__ = original_exception  # Preserve exception chain
            
            return new_exception
            
        except (ImportError, AttributeError) as e:
            logger.error(f"Could not import exception class {error_class}: {e}")
            # Fallback to generic database error
            try:
                exception_module = __import__('velocity.db.exceptions', fromlist=['DatabaseError'])
                DatabaseError = getattr(exception_module, 'DatabaseError')
                fallback_exception = DatabaseError(f"Database error: {message}")
                fallback_exception.__cause__ = original_exception
                return fallback_exception
            except Exception as fallback_error:
                logger.critical(f"Failed to create fallback exception: {fallback_error}")
                # Last resort: return the original exception
                return original_exception
