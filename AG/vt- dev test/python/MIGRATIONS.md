# Database Migration Commands

## Initialize Alembic (if starting fresh)
```bash
cd python
alembic init alembic
```

## Create a new migration
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Create empty migration
alembic revision -m "description"
```

## Apply migrations
```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision>
```

## View migration history
```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads
```

## Docker Commands
```bash
# Run migrations in Docker
docker-compose exec backend alembic upgrade head

# Create migration in Docker
docker-compose exec backend alembic revision --autogenerate -m "add new column"
```
