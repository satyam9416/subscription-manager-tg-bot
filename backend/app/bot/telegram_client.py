import os
import logging
from datetime import datetime
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import uuid

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global instances
bot = None
application = None

# Configuration flag for using webhooks or handlers
USE_WEBHOOKS = os.environ.get("USE_WEBHOOKS", "false").lower() == "true"


def initialize_bot():
    """Initialize the Telegram bot - DEPRECATED: Use TelegramGroupBotService instead."""
    logger.warning("⚠️  initialize_bot() is deprecated. The new TelegramGroupBotService should be used instead.")
    # Return None to prevent duplicate bot instances
    return None


def start_polling():
    """Start polling for updates in a non-blocking way."""
    global application
    if application:
        try:
            # Create a new event loop for this thread
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Run the application with the new loop
            application.run_polling()
        except Exception as e:
            logger.exception(f"Error in polling:")
            # Try to restart polling after a delay
            import time

            time.sleep(10)
            start_polling()


def get_bot():
    """Get the bot instance - DEPRECATED: Use TelegramGroupBotService instead."""
    logger.warning("⚠️  get_bot() is deprecated. Use get_telegram_bot_service() instead.")
    # Return the bot from the new service to avoid conflicts
    from app.services.telegram import get_telegram_bot_service
    tg_bot_service = get_telegram_bot_service()
    return tg_bot_service.bot if tg_bot_service else None


def generate_invite_link(chat_id, expires_at):
    """Generate a unique, time-limited, single-use invite link for a Telegram group.

    Args:
        chat_id: The Telegram chat/group ID
        expires_at: Datetime when the link should expire

    Returns:
        tuple: (invite_link, invite_token) or (None, None) if failed
    """
    import asyncio

    bot_instance = get_bot()
    if not bot_instance:
        logger.error("Bot not initialized")
        return None, None

    try:
        # Generate a unique token for this invite
        invite_token = str(uuid.uuid4())

        # Calculate expiry time in Unix timestamp (seconds)
        expire_date = int(expires_at.timestamp())

        # Use the existing event loop if available, otherwise create a new one
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, use run_coroutine_threadsafe
                future = asyncio.run_coroutine_threadsafe(
                    bot_instance.create_chat_invite_link(
                        chat_id=chat_id,
                        expire_date=expire_date,
                        member_limit=1,  # Single-use
                        name=f"Subscription-{invite_token[:8]}",  # Add a name for easier identification
                    ),
                    loop,
                )
                chat_invite_link = future.result(timeout=30)
            else:
                # We're not in an async context, use run_until_complete
                chat_invite_link = loop.run_until_complete(
                    bot_instance.create_chat_invite_link(
                        chat_id=chat_id,
                        expire_date=expire_date,
                        member_limit=1,  # Single-use
                        name=f"Subscription-{invite_token[:8]}",  # Add a name for easier identification
                    )
                )
        except RuntimeError:
            # No event loop exists, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                chat_invite_link = loop.run_until_complete(
                    bot_instance.create_chat_invite_link(
                        chat_id=chat_id,
                        expire_date=expire_date,
                        member_limit=1,  # Single-use
                        name=f"Subscription-{invite_token[:8]}",  # Add a name for easier identification
                    )
                )
            finally:
                loop.close()

        return chat_invite_link.invite_link, invite_token
    except Exception as e:
        logger.error(f"Failed to generate invite link: {e}")
        return None, None


def kick_user_from_group(chat_id, user_id):
    """Remove a user from a Telegram group.

    Args:
        chat_id: The Telegram chat/group ID
        user_id: The Telegram user ID to remove

    Returns:
        bool: True if successful, False otherwise
    """
    import asyncio

    bot_instance = get_bot()
    if not bot_instance:
        logger.error("Bot not initialized")
        return False

    try:
        # Use the existing event loop if available, otherwise create a new one
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, use run_coroutine_threadsafe
                future1 = asyncio.run_coroutine_threadsafe(
                    bot_instance.ban_chat_member(
                        chat_id=chat_id,
                        user_id=user_id,
                        until_date=int(datetime.now().timestamp())
                        + 30,  # Ban for 30 seconds (minimum required)
                    ),
                    loop,
                )
                future1.result(timeout=30)

                future2 = asyncio.run_coroutine_threadsafe(
                    bot_instance.unban_chat_member(
                        chat_id=chat_id, user_id=user_id, only_if_banned=True
                    ),
                    loop,
                )
                future2.result(timeout=30)
            else:
                # We're not in an async context, use run_until_complete
                loop.run_until_complete(
                    bot_instance.ban_chat_member(
                        chat_id=chat_id,
                        user_id=user_id,
                        until_date=int(datetime.now().timestamp())
                        + 30,  # Ban for 30 seconds (minimum required)
                    )
                )
                loop.run_until_complete(
                    bot_instance.unban_chat_member(
                        chat_id=chat_id, user_id=user_id, only_if_banned=True
                    )
                )
        except RuntimeError:
            # No event loop exists, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    bot_instance.ban_chat_member(
                        chat_id=chat_id,
                        user_id=user_id,
                        until_date=int(datetime.now().timestamp())
                        + 30,  # Ban for 30 seconds (minimum required)
                    )
                )
                loop.run_until_complete(
                    bot_instance.unban_chat_member(
                        chat_id=chat_id, user_id=user_id, only_if_banned=True
                    )
                )
            finally:
                loop.close()

        return True
    except Exception as e:
        logger.error(f"Failed to kick user from group: {e}")
        return False


def sync_bot_groups():
    """Fetch and register all groups the bot is currently a member of.

    This is useful when the bot was added to groups while the server was down.

    Returns:
        list: List of registered group IDs or None if failed
    """
    from app.services import TelegramGroupService
    import asyncio

    bot_instance = get_bot()
    if not bot_instance:
        logger.error("Bot not initialized")
        return None

    try:
        registered_groups = []

        # Use the existing event loop if available, otherwise create a new one
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, use run_coroutine_threadsafe
                future = asyncio.run_coroutine_threadsafe(
                    bot_instance.get_updates(limit=100, timeout=0), loop
                )
                updates = future.result(timeout=30)
            else:
                # We're not in an async context, use run_until_complete
                updates = loop.run_until_complete(
                    bot_instance.get_updates(limit=100, timeout=0)
                )
        except RuntimeError:
            # No event loop exists, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                updates = loop.run_until_complete(
                    bot_instance.get_updates(limit=100, timeout=0)
                )
            finally:
                loop.close()

        # Process each update to find groups
        for update in updates:
            if update.my_chat_member and update.my_chat_member.chat.type in [
                "group",
                "supergroup",
            ]:
                chat = update.my_chat_member.chat
                chat_id = str(chat.id)
                chat_title = chat.title

                # Register the group
                TelegramGroupService.create_or_update_group(chat_id, chat_title)
                registered_groups.append(chat_id)
                logger.info(f"Registered group: {chat_title} ({chat_id})")

        return registered_groups
    except Exception as e:
        logger.exception(f"Failed to sync bot groups: {e}")
        return None
