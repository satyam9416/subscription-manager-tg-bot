# Environment Variables Setup

This document explains how to configure the application to use either a local Docker database or an external third-party database.

## Local Development with Docker Database

For local development, you can use the included PostgreSQL container. Create a `.env` file in the project root with:

```bash
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=tg_manager
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Application Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Port Configuration (optional)
BACKEND_PORT=5000
FRONTEND_PORT=3000
```

Then run:

```bash
docker-compose --profile local-db up
```

## Using External Database

To use an external database (cloud-hosted, AWS RDS, etc.), create a `.env` file with your external database credentials:

```bash
# External Database Configuration
POSTGRES_HOST=your-db-host.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database_name

# Application Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Port Configuration (optional)
BACKEND_PORT=5000
FRONTEND_PORT=3000
```

Then run:

```bash
docker-compose up
```

## Popular Cloud Provider Examples

### AWS RDS PostgreSQL

```bash
POSTGRES_HOST=your-instance.region.rds.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
```

### Google Cloud SQL

```bash
POSTGRES_HOST=your-instance-ip
POSTGRES_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
```

### Azure Database for PostgreSQL

```bash
POSTGRES_HOST=your-server.postgres.database.azure.com
POSTGRES_PORT=5432
POSTGRES_USER=your_username@your-server
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
```

### DigitalOcean Managed Database

```bash
POSTGRES_HOST=your-cluster.db.ondigitalocean.com
POSTGRES_PORT=25060
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
```

## Port Configuration

You can customize the ports for both frontend and backend services using environment variables:

```bash
# Port Configuration (optional)
BACKEND_PORT=5000    # Default: 5000
FRONTEND_PORT=3000   # Default: 3000
```

### Examples:

**Custom ports:**

```bash
# .env file
BACKEND_PORT=8000
FRONTEND_PORT=4000
```

**Different port ranges:**

```bash
# .env file
BACKEND_PORT=8080
FRONTEND_PORT=8081
```

## Key Changes Made

1. **Database Service Profile**: The local database service now uses the `local-db` profile, making it optional
2. **Flexible Database Host**: Added `POSTGRES_HOST` and `POSTGRES_PORT` environment variables
3. **Configurable Ports**: Added `BACKEND_PORT` and `FRONTEND_PORT` environment variables for port customization
4. **Optional Dependencies**: The backend service can now start without the local database if external database is configured
5. **Backward Compatibility**: Default values ensure existing setups continue to work

## Usage

- **With local database**: `docker-compose --profile local-db up`
- **With external database**: `docker-compose up` (no profile needed)
- **Backend only**: `docker-compose up backend frontend` (when using external database)
