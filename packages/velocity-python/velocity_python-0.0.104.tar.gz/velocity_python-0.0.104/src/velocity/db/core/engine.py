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

        except Exception as e:
            raise self.process_error(e)

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
        
        # Enhanced logging with context - more readable format
        sql_preview = sql[:100] + "..." if sql and len(sql) > 100 else sql or "None"
        
        logger.error(
            f"🔴 Database Error Detected\n"
            f"   Exception Type: {type(exception).__name__}\n"
            f"   SQL Statement: {sql_preview}\n"
            f"   Processing error for classification..."
        )
        
        # Safely get error code and message with fallbacks
        try:
            error_code = getattr(exception, 'pgcode', None) or self.get_error(exception)
        except Exception as e:
            logger.warning(f"⚠️  Unable to extract database error code: {e}")
            error_code = None
            
        try:
            error_message = str(exception)
        except Exception as e:
            logger.warning(f"⚠️  Unable to convert exception to string: {e}")
            error_message = f"<Error converting exception: {type(exception).__name__}>"
        
        # Primary error classification by error code
        if error_code and hasattr(self, 'error_codes'):
            for error_class, codes in self.error_codes.items():
                if error_code in codes:
                    logger.info(f"✅ Successfully classified error: {error_code} → {error_class}")
                    try:
                        return self._create_exception_with_chaining(
                            error_class, error_message, exception, sql, parameters
                        )
                    except Exception as creation_error:
                        logger.error(f"❌ Failed to create {error_class} exception: {creation_error}")
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
                        logger.info(f"✅ Classified error by pattern match: '{pattern}' → {error_class}")
                        return self._create_exception_with_chaining(
                            error_class, error_message, exception, sql, parameters
                        )
                except re.error as regex_error:
                    logger.warning(f"⚠️  Regex pattern error for '{pattern}': {regex_error}")
                    continue
                except Exception as pattern_error:
                    logger.error(f"❌ Error applying pattern '{pattern}': {pattern_error}")
                    continue
        
        # Fallback: return generic database error with full context
        available_codes = list(getattr(self, 'error_codes', {}).keys()) if hasattr(self, 'error_codes') else []
        logger.warning(
            f"⚠️  Unable to classify database error automatically\n"
            f"   → Falling back to generic DatabaseError\n"
            f"   → Error Code: {error_code or 'Unknown'}\n"
            f"   → Available Classifications: {available_codes or 'None configured'}"
        )
        
        return self._create_exception_with_chaining(
            'DatabaseError', error_message, exception, sql, parameters
        )
    
    def _format_human_readable_error(self, error_class, message, original_exception, sql=None, parameters=None, format_type='console'):
        """
        Format a human-readable error message with proper context and formatting.
        
        Args:
            error_class: The name of the exception class
            message: The raw error message
            original_exception: The original exception
            sql: The SQL statement (optional)
            parameters: The SQL parameters (optional)
            format_type: 'console' for terminal output, 'email' for HTML email format
            
        Returns:
            A nicely formatted, human-readable error message
        """
        if format_type == 'email':
            return self._format_email_error(error_class, message, original_exception, sql, parameters)
        else:
            return self._format_console_error(error_class, message, original_exception, sql, parameters)
    
    def _format_console_error(self, error_class, message, original_exception, sql=None, parameters=None):
        """
        Format error message for console/terminal output with Unicode box drawing.
        """
        # Map error classes to user-friendly descriptions
        error_descriptions = {
            'DbColumnMissingError': 'Column Not Found',
            'DbTableMissingError': 'Table Not Found', 
            'DbDatabaseMissingError': 'Database Not Found',
            'DbForeignKeyMissingError': 'Foreign Key Constraint Violation',
            'DbDuplicateKeyError': 'Duplicate Key Violation',
            'DbConnectionError': 'Database Connection Failed',
            'DbDataIntegrityError': 'Data Integrity Violation',
            'DbQueryError': 'Query Execution Error',
            'DbTransactionError': 'Transaction Error',
            'DbTruncationError': 'Data Truncation Error',
            'DatabaseError': 'Database Error'
        }
        
        # Get user-friendly error type
        friendly_type = error_descriptions.get(error_class, error_class.replace('Db', '').replace('Error', ' Error'))
        
        # Clean up the original message
        clean_message = str(message).strip()
        
        # Extract specific details from PostgreSQL errors
        details = self._extract_error_details(original_exception, clean_message)
        
        # Build the formatted message
        lines = []
        lines.append(f"╭─ {friendly_type} ─" + "─" * max(0, 60 - len(friendly_type)))
        lines.append("│")
        
        # Add the main error description
        if details.get('description'):
            lines.append(f"│ {details['description']}")
        else:
            lines.append(f"│ {clean_message}")
        lines.append("│")
        
        # Add error code if available
        error_code = getattr(original_exception, 'pgcode', None)
        if error_code:
            lines.append(f"│ Error Code: {error_code}")
        
        # Add specific details if available
        if details.get('column'):
            lines.append(f"│ Column: {details['column']}")
        if details.get('table'):
            lines.append(f"│ Table: {details['table']}")
        if details.get('constraint'):
            lines.append(f"│ Constraint: {details['constraint']}")
        if details.get('hint'):
            lines.append(f"│ Hint: {details['hint']}")
        
        # Add SQL context if available
        if sql:
            lines.append("│")
            lines.append("│ SQL Statement:")
            # Show complete SQL without truncation for debugging
            for line in sql.split('\n'):
                lines.append(f"│   {line.strip()}")
        
        # Add parameters if available
        if parameters is not None:
            lines.append("│")
            lines.append(f"│ Parameters: {parameters}")
        
        # Add debugging section with copy-paste ready format
        if sql or parameters is not None:
            lines.append("│")
            lines.append("│ ┌─ DEBUG COPY-PASTE SECTION ─────────────────────────────")
            
            if sql and parameters is not None:
                # Format for direct copy-paste into database console
                lines.append("│ │")
                lines.append("│ │ Complete SQL with Parameters:")
                lines.append("│ │ " + "─" * 45)
                
                # Show the raw SQL
                lines.append("│ │ Raw SQL:")
                for line in sql.split('\n'):
                    lines.append(f"│ │   {line}")
                
                lines.append("│ │")
                lines.append(f"│ │ Raw Parameters: {parameters}")
                
                # Try to create an executable version
                lines.append("│ │")
                lines.append("│ │ Executable Format (for PostgreSQL):")
                lines.append("│ │ " + "─" * 35)
                
                try:
                    # Create a version with parameters substituted for testing
                    executable_sql = self._format_executable_sql(sql, parameters)
                    for line in executable_sql.split('\n'):
                        lines.append(f"│ │   {line}")
                except Exception:
                    lines.append("│ │   [Unable to format executable SQL]")
                    for line in sql.split('\n'):
                        lines.append(f"│ │   {line}")
                    lines.append(f"│ │   -- Parameters: {parameters}")
                
            elif sql:
                lines.append("│ │")
                lines.append("│ │ SQL Statement (no parameters):")
                lines.append("│ │ " + "─" * 30)
                for line in sql.split('\n'):
                    lines.append(f"│ │   {line}")
            
            lines.append("│ │")
            lines.append("│ └─────────────────────────────────────────────────────────")
        
        # Add detailed call stack information for debugging
        stack_info = self._extract_call_stack_info()
        if stack_info:
            lines.append("│")
            lines.append("│ ┌─ CALL STACK ANALYSIS ──────────────────────────────────")
            lines.append("│ │")
            
            if stack_info.get('top_level_call'):
                lines.append("│ │ Top-Level Function (most helpful for debugging):")
                lines.append("│ │ " + "─" * 48)
                call = stack_info['top_level_call']
                lines.append(f"│ │   Function: {call['function']}")
                lines.append(f"│ │   File: {call['file']}")
                lines.append(f"│ │   Line: {call['line']}")
                if call.get('code'):
                    lines.append(f"│ │   Code: {call['code'].strip()}")
            
            if stack_info.get('relevant_calls'):
                lines.append("│ │")
                lines.append("│ │ Relevant Call Chain (excluding middleware):")
                lines.append("│ │ " + "─" * 44)
                for i, call in enumerate(stack_info['relevant_calls'][:5], 1):  # Show top 5
                    lines.append(f"│ │   {i}. {call['function']} in {call['file']}:{call['line']}")
                    if call.get('code'):
                        lines.append(f"│ │      → {call['code'].strip()}")
            
            if stack_info.get('lambda_context'):
                lines.append("│ │")
                lines.append("│ │ AWS Lambda Context:")
                lines.append("│ │ " + "─" * 19)
                for key, value in stack_info['lambda_context'].items():
                    lines.append(f"│ │   {key}: {value}")
            
            lines.append("│ │")
            lines.append("│ └─────────────────────────────────────────────────────────")
        
        lines.append("│")
        lines.append("╰" + "─" * 70)
        
        return '\n'.join(lines)

    def _format_email_error(self, error_class, message, original_exception, sql=None, parameters=None):
        """
        Format error message for email delivery with HTML formatting.
        """
        # Map error classes to user-friendly descriptions
        error_descriptions = {
            'DbColumnMissingError': 'Column Not Found',
            'DbTableMissingError': 'Table Not Found', 
            'DbDatabaseMissingError': 'Database Not Found',
            'DbForeignKeyMissingError': 'Foreign Key Constraint Violation',
            'DbDuplicateKeyError': 'Duplicate Key Violation',
            'DbConnectionError': 'Database Connection Failed',
            'DbDataIntegrityError': 'Data Integrity Violation',
            'DbQueryError': 'Query Execution Error',
            'DbTransactionError': 'Transaction Error',
            'DbTruncationError': 'Data Truncation Error',
            'DatabaseError': 'Database Error'
        }
        
        # Get user-friendly error type
        friendly_type = error_descriptions.get(error_class, error_class.replace('Db', '').replace('Error', ' Error'))
        
        # Clean up the original message
        clean_message = str(message).strip()
        
        # Extract specific details from PostgreSQL errors
        details = self._extract_error_details(original_exception, clean_message)
        
        # Get error code
        error_code = getattr(original_exception, 'pgcode', None)
        
        # Get stack info
        stack_info = self._extract_call_stack_info()
        
        # Build HTML email format
        html_parts = []
        
        # Email header
        html_parts.append("""
<html>
<head>
    <style>
        body { font-family: 'Courier New', monospace; margin: 20px; }
        .error-container { border: 2px solid #dc3545; border-radius: 8px; padding: 20px; background-color: #f8f9fa; }
        .error-header { background-color: #dc3545; color: white; padding: 10px; border-radius: 5px; font-weight: bold; font-size: 16px; margin-bottom: 15px; }
        .error-section { margin: 15px 0; padding: 10px; background-color: #ffffff; border-left: 4px solid #007bff; }
        .section-title { font-weight: bold; color: #007bff; margin-bottom: 8px; }
        .code-block { background-color: #f1f3f4; padding: 10px; border-radius: 4px; font-family: 'Courier New', monospace; margin: 5px 0; white-space: pre-wrap; }
        .highlight { background-color: #fff3cd; padding: 2px 4px; border-radius: 3px; }
        .stack-call { margin: 5px 0; padding: 5px; background-color: #e9ecef; border-radius: 3px; }
        .copy-section { background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="error-container">
""")
        
        # Error header
        html_parts.append(f'        <div class="error-header">🚨 {friendly_type}</div>')
        
        # Main error description
        description = details.get('description', clean_message)
        html_parts.append(f'        <div class="error-section"><strong>{description}</strong></div>')
        
        # Error details section
        if error_code or details.get('column') or details.get('table') or details.get('constraint'):
            html_parts.append('        <div class="error-section">')
            html_parts.append('            <div class="section-title">Error Details:</div>')
            if error_code:
                html_parts.append(f'            <div><strong>Error Code:</strong> <span class="highlight">{error_code}</span></div>')
            if details.get('column'):
                html_parts.append(f'            <div><strong>Column:</strong> <span class="highlight">{details["column"]}</span></div>')
            if details.get('table'):
                html_parts.append(f'            <div><strong>Table:</strong> <span class="highlight">{details["table"]}</span></div>')
            if details.get('constraint'):
                html_parts.append(f'            <div><strong>Constraint:</strong> <span class="highlight">{details["constraint"]}</span></div>')
            if details.get('hint'):
                html_parts.append(f'            <div><strong>Hint:</strong> {details["hint"]}</div>')
            html_parts.append('        </div>')
        
        # SQL and Parameters section
        if sql or parameters is not None:
            html_parts.append('        <div class="copy-section">')
            html_parts.append('            <div class="section-title">📋 Debug Information (Copy-Paste Ready)</div>')
            
            if sql:
                html_parts.append('            <div><strong>SQL Statement:</strong></div>')
                html_parts.append(f'            <div class="code-block">{self._html_escape(sql)}</div>')
            
            if parameters is not None:
                html_parts.append(f'            <div><strong>Parameters:</strong> <code>{self._html_escape(str(parameters))}</code></div>')
            
            # Executable SQL
            if sql and parameters is not None:
                try:
                    executable_sql = self._format_executable_sql(sql, parameters)
                    html_parts.append('            <div><strong>Executable SQL (for testing):</strong></div>')
                    html_parts.append(f'            <div class="code-block">{self._html_escape(executable_sql)}</div>')
                except Exception:
                    pass
            
            html_parts.append('        </div>')
        
        # Call stack section  
        if stack_info and stack_info.get('top_level_call'):
            html_parts.append('        <div class="error-section">')
            html_parts.append('            <div class="section-title">🔍 Source Code Location</div>')
            
            call = stack_info['top_level_call']
            html_parts.append('            <div class="stack-call">')
            html_parts.append(f'                <strong>Function:</strong> {call["function"]}<br>')
            html_parts.append(f'                <strong>File:</strong> {call["file"]}<br>')
            html_parts.append(f'                <strong>Line:</strong> {call["line"]}')
            if call.get('code'):
                html_parts.append(f'<br>                <strong>Code:</strong> <code>{self._html_escape(call["code"].strip())}</code>')
            html_parts.append('            </div>')
            
            # Show relevant call chain
            if stack_info.get('relevant_calls') and len(stack_info['relevant_calls']) > 1:
                html_parts.append('            <div><strong>Call Chain:</strong></div>')
                for i, call in enumerate(stack_info['relevant_calls'][:4], 1):
                    html_parts.append('            <div class="stack-call">')
                    html_parts.append(f'                {i}. <strong>{call["function"]}</strong> in {call["file"]}:{call["line"]}')
                    html_parts.append('            </div>')
            
            html_parts.append('        </div>')
        
        # Lambda context
        if stack_info and stack_info.get('lambda_context'):
            html_parts.append('        <div class="error-section">')
            html_parts.append('            <div class="section-title">⚡ AWS Lambda Context</div>')
            for key, value in stack_info['lambda_context'].items():
                html_parts.append(f'            <div><strong>{key.title()}:</strong> {value}</div>')
            html_parts.append('        </div>')
        
        # Email footer
        html_parts.append("""
    </div>
</body>
</html>
""")
        
        return ''.join(html_parts)

    def _html_escape(self, text):
        """Escape HTML special characters."""
        if not text:
            return ""
        return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))

    def _format_executable_sql(self, sql, parameters):
        """
        Format SQL with parameters substituted for easy copy-paste debugging.
        
        Args:
            sql: The SQL statement with placeholders
            parameters: The parameters to substitute
            
        Returns:
            SQL statement with parameters properly formatted for execution
        """
        if not parameters:
            return sql
            
        try:
            # Handle different parameter formats
            if isinstance(parameters, (list, tuple)):
                # For positional parameters (%s style)
                formatted_sql = sql
                
                # Replace %s placeholders with properly formatted values
                for param in parameters:
                    if isinstance(param, str):
                        # Escape single quotes and wrap in quotes
                        formatted_param = f"'{param.replace(chr(39), chr(39)+chr(39))}'"
                    elif isinstance(param, (int, float)):
                        formatted_param = str(param)
                    elif param is None:
                        formatted_param = 'NULL'
                    elif isinstance(param, bool):
                        formatted_param = 'TRUE' if param else 'FALSE'
                    else:
                        # For other types, try to convert to string and quote
                        formatted_param = f"'{str(param).replace(chr(39), chr(39)+chr(39))}'"
                    
                    # Replace first occurrence of %s
                    formatted_sql = formatted_sql.replace('%s', formatted_param, 1)
                
                return formatted_sql
                
            elif isinstance(parameters, dict):
                # For named parameters (%(name)s style)
                formatted_sql = sql
                for key, value in parameters.items():
                    placeholder = f'%({key})s'
                    if isinstance(value, str):
                        formatted_value = f"'{value.replace(chr(39), chr(39)+chr(39))}'"
                    elif isinstance(value, (int, float)):
                        formatted_value = str(value)
                    elif value is None:
                        formatted_value = 'NULL'
                    elif isinstance(value, bool):
                        formatted_value = 'TRUE' if value else 'FALSE'
                    else:
                        formatted_value = f"'{str(value).replace(chr(39), chr(39)+chr(39))}'"
                    
                    formatted_sql = formatted_sql.replace(placeholder, formatted_value)
                
                return formatted_sql
            
            else:
                # Fallback: just append parameters as comment
                return f"{sql}\n-- Parameters: {parameters}"
                
        except Exception:
            # If formatting fails, return original with parameters as comment
            return f"{sql}\n-- Parameters: {parameters}"

    def _extract_call_stack_info(self):
        """
        Extract relevant call stack information for debugging, filtering out 
        middleware and focusing on the most useful frames.
        
        Returns:
            Dictionary with call stack analysis
        """
        import traceback
        import os
        
        try:
            # Get the current stack
            stack = traceback.extract_stack()
            
            # Common middleware/decorator patterns to filter out
            middleware_patterns = [
                'decorator',
                'wrapper',
                'new_function',
                'exec_function',
                '_execute',
                'process_error',
                '_create_exception',
                '_format_human_readable',
                '__enter__',
                '__exit__',
                'contextlib',
                'functools'
            ]
            
            # Lambda/AWS specific patterns
            lambda_patterns = [
                'lambda_handler',
                'handler',
                'bootstrap',
                'runtime'
            ]
            
            relevant_calls = []
            top_level_call = None
            lambda_context = {}
            
            # Analyze stack frames from top to bottom (most recent first)
            for frame in reversed(stack[:-4]):  # Skip the last few frames (this method, etc.)
                file_path = frame.filename
                function_name = frame.name
                line_number = frame.lineno
                code_line = frame.line or ""
                
                # Extract just the filename
                filename = os.path.basename(file_path)
                
                # Skip internal Python and library frames
                if any(skip in file_path.lower() for skip in [
                    'python3', 'site-packages', '/usr/', '/opt/python',
                    'psycopg2', 'boto3', 'botocore'
                ]):
                    continue
                
                # Capture Lambda context if found
                if any(pattern in function_name.lower() for pattern in lambda_patterns):
                    lambda_context.update({
                        'handler': function_name,
                        'file': filename,
                        'line': line_number
                    })
                
                # Skip middleware/decorator frames but keep track of meaningful ones
                is_middleware = any(pattern in function_name.lower() for pattern in middleware_patterns)
                
                if not is_middleware:
                    call_info = {
                        'function': function_name,
                        'file': filename,
                        'line': line_number,
                        'code': code_line,
                        'full_path': file_path
                    }
                    
                    relevant_calls.append(call_info)
                    
                    # The first non-middleware call is likely the most important
                    if not top_level_call:
                        # Look for application-level calls (not in velocity internals)
                        if not any(internal in file_path for internal in [
                            'velocity/db/', 'velocity/aws/', 'velocity/misc/'
                        ]):
                            top_level_call = call_info
            
            # If no clear top-level call found, use the first relevant call
            if not top_level_call and relevant_calls:
                top_level_call = relevant_calls[0]
            
            # Look for handler functions in the stack
            handler_calls = [call for call in relevant_calls 
                           if any(pattern in call['function'].lower() 
                                for pattern in ['handler', 'main', 'process', 'action'])]
            
            if handler_calls and not top_level_call:
                top_level_call = handler_calls[0]
            
            return {
                'top_level_call': top_level_call,
                'relevant_calls': relevant_calls,
                'lambda_context': lambda_context if lambda_context else None
            }
            
        except Exception:
            # If stack analysis fails, return minimal info
            return None

    def _extract_error_details(self, exception, message):
        """
        Extract specific details from database errors for better formatting.
        
        Args:
            exception: The original database exception
            message: The error message string
            
        Returns:
            Dictionary with extracted details
        """
        import re
        
        details = {}
        
        # PostgreSQL specific error parsing
        if hasattr(exception, 'pgcode'):
            # Column does not exist
            if 'column' in message.lower() and 'does not exist' in message.lower():
                match = re.search(r'column "([^"]+)" does not exist', message, re.IGNORECASE)
                if match:
                    details['column'] = match.group(1)
                    details['description'] = f'The column "{match.group(1)}" was not found in the table.'
            
            # Table does not exist  
            elif 'relation' in message.lower() and 'does not exist' in message.lower():
                match = re.search(r'relation "([^"]+)" does not exist', message, re.IGNORECASE)
                if match:
                    details['table'] = match.group(1)
                    details['description'] = f'The table "{match.group(1)}" was not found in the database.'
            
            # Foreign key violation
            elif 'foreign key constraint' in message.lower():
                match = re.search(r'violates foreign key constraint "([^"]+)"', message, re.IGNORECASE)
                if match:
                    details['constraint'] = match.group(1)
                    details['description'] = 'A foreign key constraint was violated.'
                    details['hint'] = 'Make sure the referenced record exists.'
            
            # Unique constraint violation
            elif 'unique constraint' in message.lower() or 'duplicate key' in message.lower():
                match = re.search(r'violates unique constraint "([^"]+)"', message, re.IGNORECASE)
                if match:
                    details['constraint'] = match.group(1)
                    details['description'] = 'A unique constraint was violated (duplicate key).'
                    details['hint'] = 'The value you are trying to insert already exists.'
            
            # Connection errors
            elif any(term in message.lower() for term in ['connection', 'connect', 'server']):
                details['description'] = 'Failed to connect to the database server.'
                details['hint'] = 'Check your database connection settings and network connectivity.'
            
            # Data type errors
            elif 'invalid input syntax' in message.lower():
                details['description'] = 'Invalid data format provided.'
                details['hint'] = 'Check that your data matches the expected format for the column type.'
        
        return details

    def _create_exception_with_chaining(self, error_class, message, original_exception, sql=None, parameters=None, format_type=None):
        """
        Create a velocity exception with proper exception chaining and human-readable formatting.
        
        Args:
            error_class: The name of the exception class to create
            message: The error message
            original_exception: The original exception to chain
            sql: The SQL statement (optional)
            parameters: The SQL parameters (optional)
            format_type: 'console', 'email', or None (auto-detect)
            
        Returns:
            The created exception with proper chaining and formatting
        """
        logger = logging.getLogger(__name__)
        
        try:
            # Import the exception class dynamically
            exception_module = __import__('velocity.db.exceptions', fromlist=[error_class])
            ExceptionClass = getattr(exception_module, error_class)
            
            # Auto-detect format if not specified
            if format_type is None:
                format_type = self._detect_output_format()
            
            # Create human-readable, formatted message
            formatted_message = self._format_human_readable_error(
                error_class, message, original_exception, sql, parameters, format_type
            )
            
            # For email format, also create a console version for logging
            if format_type == 'email':
                console_message = self._format_human_readable_error(
                    error_class, message, original_exception, sql, parameters, 'console'
                )
                # Log the console version for server logs
                logger.error(f"Database Error (Console Format):\n{console_message}")
                
                # Create custom exception with both formats
                new_exception = ExceptionClass(formatted_message)
                new_exception.console_format = console_message
                new_exception.email_format = formatted_message
            else:
                new_exception = ExceptionClass(formatted_message)
                
            # Only set __cause__ if original_exception is actually a BaseException
            if isinstance(original_exception, BaseException):
                new_exception.__cause__ = original_exception  # Preserve exception chain
            
            return new_exception
            
        except (ImportError, AttributeError) as e:
            logger.error(f"Could not import exception class {error_class}: {e}")
            # Fallback to generic database error
            try:
                exception_module = __import__('velocity.db.exceptions', fromlist=['DatabaseError'])
                DatabaseError = getattr(exception_module, 'DatabaseError')
                
                # Auto-detect format if not specified for fallback too
                if format_type is None:
                    format_type = self._detect_output_format()
                
                # Still format the fallback nicely
                formatted_message = self._format_human_readable_error(
                    'DatabaseError', message, original_exception, sql, parameters, format_type
                )
                
                fallback_exception = DatabaseError(formatted_message)
                # Only set __cause__ if original_exception is actually a BaseException
                if isinstance(original_exception, BaseException):
                    fallback_exception.__cause__ = original_exception
                return fallback_exception
            except Exception as fallback_error:
                logger.critical(f"Failed to create fallback exception: {fallback_error}")
                # Last resort: return the original exception
                return original_exception

    def _detect_output_format(self):
        """
        Detect whether we should use console or email formatting based on context.
        
        Returns:
            'email' if in email/notification context, 'console' otherwise
        """
        import inspect
        
        # Look at the call stack for email-related functions
        stack = inspect.stack()
        
        email_indicators = [
            'email', 'mail', 'notification', 'alert', 'send', 'notify',
            'smtp', 'message', 'recipient', 'subject', 'body'
        ]
        
        for frame_info in stack:
            function_name = frame_info.function.lower()
            filename = frame_info.filename.lower()
            
            # Check if we're in an email-related context
            if any(indicator in function_name or indicator in filename 
                   for indicator in email_indicators):
                return 'email'
        
        # Default to console format
        return 'console'
