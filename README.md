# Advanced Product Subscription and Telegram Group Management System

A full-stack application that allows administrators to manage products and map them to exclusive Telegram groups. Users can subscribe to products and receive time-limited, single-use invite links to join the corresponding Telegram groups.

## Features

- Product management (CRUD operations)
- Telegram group mapping to products (one-to-one)
- User subscription system
- Automatic user identification upon joining Telegram groups
- Automatic removal of users when subscriptions expire
- Flexible database configuration (local Docker or external cloud databases)
- Configurable service ports
- Docker Compose profiles for different deployment scenarios

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Marshmallow, Python Telegram Bot
- **Frontend**: React, Vite, Tailwind CSS
- **Database**: PostgreSQL
- **Deployment**: Docker, Docker Compose

## Project Structure

```
tg-manager/
├── backend/                # Flask application
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routes/         # API endpoints
│   │   ├── schemas/        # Marshmallow schemas
│   │   ├── services/       # Business logic
│   │   ├── tasks/          # Scheduled tasks
│   │   └── bot/            # Telegram bot logic
│   ├── Dockerfile          # Backend Dockerfile
│   └── requirements.txt    # Python dependencies
├── frontend/               # React application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API integration
│   │   └── hooks/          # Custom React hooks
│   ├── Dockerfile          # Frontend Dockerfile
│   └── package.json        # Node.js dependencies
├── docker-compose.yml      # Docker Compose configuration
└── README.md               # Project documentation
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Telegram Bot Token (for development and production)

### Environment Variables

Create a `.env` file in the project root. You can use the provided `env.example` file as a starting point:

```bash
cp env.example .env
```

Then edit the `.env` file with your configuration:

#### Local Development (with Docker database)

```
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=tg_manager
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Application Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Port Configuration (optional)
BACKEND_PORT=5000
FRONTEND_PORT=3000
```

#### External Database (Cloud/Third-party)

```
# External Database Configuration
POSTGRES_HOST=your-db-host.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database_name

# Application Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Port Configuration (optional)
BACKEND_PORT=5000
FRONTEND_PORT=3000
```

#### Environment Variables Reference

| Variable             | Description                   | Default       | Required |
| -------------------- | ----------------------------- | ------------- | -------- |
| `POSTGRES_USER`      | Database username             | `postgres`    | Yes      |
| `POSTGRES_PASSWORD`  | Database password             | `postgres`    | Yes      |
| `POSTGRES_DB`        | Database name                 | `tg_manager`  | Yes      |
| `POSTGRES_HOST`      | Database host                 | `db`          | Yes      |
| `POSTGRES_PORT`      | Database port                 | `5432`        | Yes      |
| `FLASK_APP`          | Flask application entry point | `run.py`      | Yes      |
| `FLASK_ENV`          | Flask environment             | `development` | No       |
| `SECRET_KEY`         | Flask secret key              | -             | Yes      |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token            | -             | Yes      |
| `BACKEND_PORT`       | Backend service port          | `5000`        | No       |
| `FRONTEND_PORT`      | Frontend service port         | `3000`        | No       |

### Running the Application

1. Clone the repository
2. Create the `.env` file with the required environment variables:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```
3. Run the application:

   **With local Docker database:**

   ```bash
   docker-compose --profile local-db up --build
   ```

   **With external database:**

   ```bash
   docker-compose up --build
   ```

4. Access the application:
   - Frontend: http://localhost:3000 (or your custom `FRONTEND_PORT`)
   - Backend API: http://localhost:5000 (or your custom `BACKEND_PORT`)

#### Docker Compose Profiles

- `local-db`: Includes the local PostgreSQL database service
- Default (no profile): Runs only backend and frontend services (for external database usage)

## API Documentation

### Products

- `GET /api/products` - List all products
- `GET /api/products/{product_id}` - Get a specific product
- `POST /api/products` - Create a new product
- `PUT /api/products/{product_id}` - Update a product
- `DELETE /api/products/{product_id}` - Delete a product

### Groups

- `GET /api/groups` - List all Telegram groups
- Supports filters: `?status=active|inactive&role=member|administrator|left`
- `GET /api/groups/unmapped` - List unmapped Telegram groups
- `DELETE /api/groups/{telegram_group_id}` - Remove bot from group and delete record

### Mapping

- `POST /api/products/{product_id}/map` - Map a product to a Telegram group
- `DELETE /api/products/{product_id}/unmap` - Unmap a product from a Telegram group

### Subscriptions

- `POST /api/subscribe` - Create a new subscription
- `GET /api/subscriptions` - List all subscriptions (admin only)

## Database Migrations

Run Alembic migrations after pulling changes:

```bash
docker-compose exec backend alembic upgrade head
```

## License

[MIT](LICENSE)
