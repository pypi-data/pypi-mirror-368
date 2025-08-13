# Database Migration Guide for PacificPy

This guide provides instructions for setting up and running database migrations in PacificPy applications.

## SQLAlchemy Migrations with Alembic

PacificPy integrates with Alembic for SQLAlchemy database migrations.

### Installation

```bash
pip install alembic
```

### Setting up Alembic

1. Initialize Alembic in your project:

```bash
alembic init alembic
```

2. Configure `alembic.ini`:

```ini
# alembic.ini
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = postgresql://user:password@localhost/dbname
```

3. Update `alembic/env.py`:

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from myapp.models import Base  # Import your models

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Creating Migrations

Generate a new migration:

```bash
alembic revision --autogenerate -m "Create users table"
```

### Running Migrations

Apply migrations:

```bash
alembic upgrade head
```

### Downgrading Migrations

Rollback migrations:

```bash
alembic downgrade -1  # Rollback one migration
alembic downgrade base  # Rollback all migrations
```

## Tortoise ORM Migrations

Tortoise ORM has built-in migration support.

### Creating Migrations

Generate initial migration:

```bash
aerich init -t myapp.config.TORTOISE_ORM
aerich init-db
```

Generate a new migration:

```bash
aerich migrate -m "add users table"
```

### Running Migrations

Apply migrations:

```bash
aerich upgrade
```

### Downgrading Migrations

Rollback migrations:

```bash
aerich downgrade
```

## Example Configuration

### SQLAlchemy + Alembic

```python
# config.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

```python
# models.py
from sqlalchemy import Column, Integer, String
from config import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
```

### Tortoise ORM

```python
# config.py
TORTOISE_ORM = {
    "connections": {"default": "sqlite://db.sqlite3"},
    "apps": {
        "models": {
            "models": ["myapp.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
```

```python
# models.py
from tortoise.models import Model
from tortoise import fields

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
```

## Best Practices

### 1. Version Control

Always commit migration files to version control:

```bash
git add alembic/versions/
git commit -m "Add user table migration"
```

### 2. Testing Migrations

Test migrations in a separate database:

```bash
# Create test database
createdb myapp_test

# Run migrations on test database
alembic -c alembic_test.ini upgrade head
```

### 3. Backup Before Migration

Always backup your database before running migrations:

```bash
pg_dump myapp_production > backup.sql
alembic upgrade head
```

### 4. Zero Downtime Migrations

For production systems, consider zero downtime migration strategies:

```python
# Add column with default value
# alembic revision -m "Add status column"
# Modify application to use new column
# Backfill data
# Remove old column in next migration
```

## Troubleshooting

### Common Issues

1. **Migration conflicts**: Resolve by merging conflicting migrations
2. **Data loss**: Always backup before migrating
3. **Performance issues**: Run migrations during low-traffic periods
4. **Rollback failures**: Test rollbacks in staging environment

### Debugging Migrations

Check current migration status:

```bash
alembic current
alembic history
```

View SQL for a migration:

```bash
alembic upgrade head --sql
```

This guide provides a foundation for managing database migrations in PacificPy applications. Always test migrations thoroughly in staging environments before applying them to production.