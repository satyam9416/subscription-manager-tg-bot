from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    import os

    # Configure the app
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        f"postgresql://{os.environ.get('POSTGRES_USER', 'postgres')}:"
        f"{os.environ.get('POSTGRES_PASSWORD', 'postgres')}@"
        f"{os.environ.get('POSTGRES_HOST', 'db')}:5432/"
        f"{os.environ.get('POSTGRES_DB', 'tg_manager')}",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Register blueprints
    from app.routes.product_routes import product_bp
    from app.routes.group_routes import group_bp
    from app.routes.subscription_routes import subscription_bp
    from app.routes.telegram_routes import telegram_bp

    app.register_blueprint(product_bp, url_prefix="/api")
    app.register_blueprint(group_bp, url_prefix="/api")
    app.register_blueprint(subscription_bp, url_prefix="/api")
    app.register_blueprint(telegram_bp, url_prefix="/api")

    # Health check route
    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'message': 'Backend is running'}

    @app.route('/')
    def root():
        return {'message': 'Telegram Bot Manager API', 'status': 'running'}

    # Initialize Telegram bot
    # with app.app_context():
    #     from app.bot import initialize_bot, USE_WEBHOOKS

    #     initialize_bot()

    #     # Set up webhook if using webhook mode
    #     if USE_WEBHOOKS:
    #         from app.bot.telegram_client import get_bot
    #         import os

    #         webhook_url = os.environ.get("WEBHOOK_URL")
    #         if webhook_url and get_bot():
    #             try:
    #                 import asyncio

    #                 loop = asyncio.new_event_loop()
    #                 asyncio.set_event_loop(loop)

    #                 try:
    #                     token = os.environ.get("TELEGRAM_BOT_TOKEN")
    #                     webhook_path = f"{webhook_url}/api/telegram/webhook/{token}"
    #                     loop.run_until_complete(get_bot().set_webhook(url=webhook_path))
    #                     app.logger.info(f"Webhook set to {webhook_path}")
    #                 finally:
    #                     loop.close()
    #             except Exception as e:
    #                 app.logger.error(f"Failed to set webhook: {e}")
    from app.services.telegram import get_telegram_bot_service
    
    # Initialize Telegram bot service (singleton)
    tg_bot = get_telegram_bot_service()
    if tg_bot:
        tg_bot.init_app(app)
        tg_bot.start_bot()

    # Initialize scheduled tasks
    from app.tasks.subscription_tasks import init_scheduler

    init_scheduler()

    return app
