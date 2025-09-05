import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from app.services import SubscriptionService
from app.bot.telegram_client import kick_user_from_group
from app.services.telegram import get_telegram_bot_service

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None


def check_expired_subscriptions():
    """Check for expired subscriptions and remove users from groups."""
    logger.info("Checking for expired subscriptions...")

    try:
        # Get all expired subscriptions
        expired_subscriptions = SubscriptionService.get_expired_subscriptions()

        for subscription in expired_subscriptions:
            logger.info(f"Processing expired subscription: {subscription.id}")

            # Skip if user doesn't have Telegram info
            if not subscription.user.telegram_user_id:
                logger.warning(
                    f"User {subscription.user_id} has no Telegram ID, skipping removal"
                )
                continue

            # Remove user from the Telegram group
            tg_bot = get_telegram_bot_service()
            if tg_bot:
                success, message = tg_bot.remove_user(
                    subscription.telegram_group.telegram_group_id,
                    subscription.user.telegram_user_id,
                )
            else:
                success, message = False, "Telegram bot service not available"

            if success:
                logger.info(
                    f"User {subscription.user.telegram_user_id} removed from group {subscription.telegram_group.telegram_group_id}"
                )

                # Update subscription status
                SubscriptionService.expire_subscription(subscription.id)
            else:
                logger.error(
                    f"Failed to remove user {subscription.user.telegram_user_id} from group {subscription.telegram_group.telegram_group_id}"
                )

    except Exception as e:
        logger.error(f"Error checking expired subscriptions: {e}")


def init_scheduler():
    """Initialize the scheduler for subscription expiry checks."""
    global scheduler

    if scheduler:
        scheduler.shutdown()

    scheduler = BackgroundScheduler()

    # Check for expired subscriptions every hour
    scheduler.add_job(check_expired_subscriptions, "interval", hours=1)

    scheduler.start()
    logger.info("Subscription scheduler initialized")


def shutdown_scheduler():
    """Shutdown the scheduler."""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        logger.info("Subscription scheduler shutdown")
