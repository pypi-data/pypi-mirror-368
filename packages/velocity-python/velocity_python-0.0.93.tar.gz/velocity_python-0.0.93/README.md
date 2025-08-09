# Velocity.DB

A modern Python database abstraction library that simplifies database operations across multiple database engines. Velocity.DB provides a unified interface for PostgreSQL, MySQL, SQLite, and SQL Server, with features like transaction management, automatic connection pooling, and database-agnostic query building.

## Features

- **Multi-database support**: PostgreSQL, MySQL, SQLite, SQL Server
- **Transaction management**: Decorator-based transaction handling with automatic rollback
- **Query builder**: Database-agnostic SQL generation with foreign key expansion
- **Connection pooling**: Automatic connection management and pooling
- **Type safety**: Comprehensive type hints and validation
- **Modern Python**: Built for Python 3.8+ with modern packaging

## Supported Databases

- **PostgreSQL** (via psycopg2)
- **MySQL** (via mysqlclient)
- **SQLite** (built-in sqlite3)
- **SQL Server** (via pytds)

## Installation

Install the base package:

```bash
pip install velocity-python
```

Install with database-specific dependencies:

```bash
# For PostgreSQL
pip install velocity-python[postgres]

# For MySQL  
pip install velocity-python[mysql]

# For SQL Server
pip install velocity-python[sqlserver]

# For all databases
pip install velocity-python[all]
```

## Quick Start

### Database Connection

```python
import velocity.db

# PostgreSQL
engine = velocity.db.postgres(
    host="localhost",
    port=5432,
    database="mydb",
    user="username",
    password="password"
)

# MySQL
engine = velocity.db.mysql(
    host="localhost",
    port=3306,
    database="mydb",
    user="username", 
    password="password"
)

# SQLite
engine = velocity.db.sqlite("path/to/database.db")

# SQL Server
engine = velocity.db.sqlserver(
    host="localhost",
    port=1433,
    database="mydb",
    user="username",
    password="password"
### Transaction Management

Use the `@engine.transaction` decorator for automatic transaction handling:

```python
@engine.transaction
def create_user(tx):
    # All operations within this function are wrapped in a transaction
    user = tx.table('users').new()
    user['name'] = 'John Doe'
    user['email'] = 'john@example.com'
    # Transaction commits automatically on success or rolls back on error
    return user['sys_id']
```

### Table Operations

#### Creating Tables

```python
@engine.transaction
def create_tables(tx):
    # Create a users table
    users = tx.table('users')
    users.create()
    
    # Add columns by setting data
    user = users.new()
    user['name'] = 'Sample User'
    user['email'] = 'user@example.com'
    user['created_at'] = datetime.now()
```

#### Selecting Data

```python
@engine.transaction
def query_users(tx):
    users = tx.table('users')
    
    # Select all users
    all_users = users.select().all()
    
    # Select with conditions
    active_users = users.select(where={'status': 'active'}).all()
    
    # Select specific columns
    names = users.select(columns=['name', 'email']).all()
    
    # Select with ordering and limits
    recent = users.select(
        orderby='created_at DESC',
        qty=10
    ).all()
    
    # Find single record
    user = users.find({'email': 'john@example.com'})
    
    # Get by primary key
    user = users.find(123)
```

#### Updating Data

```python
@engine.transaction
def update_user(tx):
    users = tx.table('users')
    
    # Update single record
    user = users.find(123)
    user['name'] = 'Updated Name'
    user['updated_at'] = datetime.now()
    
    # Bulk update
    users.update(
        {'status': 'inactive'},
        where={'<last_login': '2023-01-01'}
    )
```

#### Inserting Data

```python
@engine.transaction
def create_users(tx):
    users = tx.table('users')
    
    # Create new record
    user = users.new()
    user['name'] = 'New User'
    user['email'] = 'new@example.com'
    
    # Insert with data
    user_id = users.insert({
        'name': 'Another User',
        'email': 'another@example.com'
    })
    
    # Upsert (insert or update)
    users.upsert(
        {'name': 'John Doe', 'status': 'active'},
        {'email': 'john@example.com'}  # matching condition
    )
```

#### Deleting Data

```python
@engine.transaction
def delete_users(tx):
    users = tx.table('users')
    
    # Delete single record
    user = users.find(123)
    user.delete()
    
    # Delete with conditions
    users.delete(where={'status': 'inactive'})
    
    # Truncate table
    users.truncate()
    
    # Drop table
    users.drop()
```

### Advanced Queries

#### Foreign Key Navigation

Velocity.DB supports automatic foreign key expansion using pointer syntax:

```python
@engine.transaction  
def get_user_with_profile(tx):
    users = tx.table('users')
    
    # Automatic join via foreign key
    users_with_profiles = users.select(
        columns=['name', 'email', 'profile_id>bio', 'profile_id>avatar_url'],
        where={'status': 'active'}
    ).all()
```

#### Complex Conditions

Velocity.DB supports various where clause formats:

```python
@engine.transaction
def complex_queries(tx):
    users = tx.table('users')
    
    # Dictionary format with operator prefixes
    results = users.select(where={
        'status': 'active',          # Equals (default)
        '>=created_at': '2023-01-01',  # Greater than or equal
        '><age': [18, 65],           # Between
        '%email': '@company.com',    # Like
        '!status': 'deleted'         # Not equal
    }).all()
    
    # List of tuples format for complex predicates
    results = users.select(where=[
        ('status = %s', 'active'),
        ('priority = %s OR urgency = %s', ('high', 'critical'))
    ]).all()
    
    # Raw string format
    results = users.select(where="status = 'active' AND age >= 18").all()
```

**Available Operators:**
- `=` (default): `{'name': 'John'}`
- `>`, `<`, `>=`, `<=`: `{'>age': 18}`, `{'<=score': 100}`
- `!`, `!=`, `<>`: `{'!status': 'deleted'}`
- `%`, `LIKE`: `{'%email': '@company.com'}`
- `!%`, `NOT LIKE`: `{'!%name': 'test%'}`
- `><`, `BETWEEN`: `{'><age': [18, 65]}`
- `!><`, `NOT BETWEEN`: `{'!><score': [0, 50]}`
```

#### Aggregations and Grouping

```python
@engine.transaction
def analytics(tx):
    orders = tx.table('orders')
    
    # Count records
    total_orders = orders.count()
    recent_orders = orders.count(where={'>=created_at': '2023-01-01'})
    
    # Aggregations
    stats = orders.select(
        columns=['COUNT(*) as total', 'SUM(amount) as revenue', 'AVG(amount) as avg_order'],
        where={'status': 'completed'},
        groupby='customer_id'
    ).all()
```

### Raw SQL

When you need full control, execute raw SQL:

```python
@engine.transaction
def raw_queries(tx):
    # Execute raw SQL
    results = tx.execute("""
        SELECT u.name, COUNT(o.id) as order_count
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.status = %s
        GROUP BY u.id, u.name
        HAVING COUNT(o.id) > %s
    """, ['active', 5]).all()
    
    # Get single value
    total = tx.execute("SELECT COUNT(*) FROM users").scalar()
    
    # Get simple list
    names = tx.execute("SELECT name FROM users").as_simple_list()
```

## Error Handling

Transactions automatically handle rollbacks on exceptions:

```python
@engine.transaction
def safe_transfer(tx):
    try:
        # Multiple operations that must succeed together
        from_account = tx.table('accounts').find(from_id)
        to_account = tx.table('accounts').find(to_id)
        
        from_account['balance'] -= amount
        to_account['balance'] += amount
        
        # If any operation fails, entire transaction rolls back
        
    except Exception as e:
        # Transaction automatically rolled back
        logger.error(f"Transfer failed: {e}")
        raise
```

## Development

### Setting up for Development

```bash
git clone https://github.com/your-repo/velocity-python.git
cd velocity-python
pip install -e .[dev]
```

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Type checking  
mypy src/

# Linting
flake8 src/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.
