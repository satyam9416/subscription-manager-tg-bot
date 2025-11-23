import logging
import json
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext
from telegram import Update
from app import db
from app.services import TelegramGroupService, SubscriptionService

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def process_update(update):
    """Process a Telegram update.

    Args:
        update: The update object from Telegram
    """
    try:
        logger.info(f"Processing update: {json.dumps(update, default=str)}")

        # Handle new chat members (user joining a group)
        if "message" in update and "new_chat_members" in update["message"]:
            handle_new_chat_members(update)

        # Handle bot added to a group
        if "my_chat_member" in update:
            handle_bot_chat_member_update(update)

        # Handle chat join request
        if "chat_join_request" in update:
            handle_chat_join_request(update)

        # Handle message with invite link
        if (
            "message" in update
            and "text" in update["message"]
            and "t.me/" in update["message"]["text"]
        ):
            handle_message_with_invite_link(update)
    except Exception as e:
        logger.error(f"Error processing update: {e}", exc_info=True)


def handle_new_chat_members(update):
    """Handle new members joining a chat/group.

    Args:
        update: The update object from Telegram
    """
    message = update["message"]
    chat_id = str(message["chat"]["id"])
    new_members = message["new_chat_members"]

    # Check if the invite link is present
    invite_link = None
    if "invite_link" in message:
        invite_link = message["invite_link"].get("invite_link")

    logger.info(f"New members joining chat {chat_id}, invite link: {invite_link}")

    for member in new_members:
        # Skip if it's a bot
        if member.get("is_bot", False):
            continue

        user_id = str(member["id"])
        username = member.get("username")

        logger.info(f"Processing new member: {user_id} ({username}) to chat {chat_id}")

        # If we have an invite link, try to find the corresponding subscription
        if invite_link:
            # Extract the token from the invite link
            parts = invite_link.split("/")
            invite_token = parts[-1] if parts else None

            logger.info(f"Extracted invite token: {invite_token}")

            if invite_token:
                try:
                    # Update the subscription with the Telegram user info
                    subscription, error = (
                        SubscriptionService.update_subscription_with_telegram_user(
                            invite_token, user_id, username
                        )
                    )

                    if error:
                        logger.error(f"Failed to update subscription: {error}")
                    else:
                        logger.info(
                            f"Successfully updated subscription for user {user_id}"
                        )
                except Exception as e:
                    logger.error(f"Error updating subscription: {e}", exc_info=True)


def handle_chat_join_request(update):
    """Handle chat join requests.

    Args:
        update: The update object from Telegram
    """
    join_request = update["chat_join_request"]
    chat_id = str(join_request["chat"]["id"])
    user_id = str(join_request["from"]["id"])
    username = join_request.get("from", {}).get("username")
    invite_link = join_request.get("invite_link", {}).get("invite_link")

    logger.info(
        f"Join request from user {user_id} ({username}) to chat {chat_id} with invite link: {invite_link}"
    )

    # If we have an invite link, try to find the corresponding subscription
    if invite_link:
        # Extract the token from the invite link
        parts = invite_link.split("/")
        invite_token = parts[-1] if parts else None

        if invite_token:
            try:
                # Update the subscription with the Telegram user info
                subscription, error = (
                    SubscriptionService.update_subscription_with_telegram_user(
                        invite_token, user_id, username
                    )
                )

                if error:
                    logger.error(f"Failed to update subscription: {error}")
                else:
                    logger.info(f"Successfully updated subscription for user {user_id}")

                    # Approve the join request
                    from app.bot.telegram_client import get_bot
                    import asyncio

                    bot = get_bot()
                    if bot:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(
                                bot.approve_chat_join_request(
                                    chat_id=chat_id, user_id=user_id
                                )
                            )
                            logger.info(
                                f"Approved join request for user {user_id} to chat {chat_id}"
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to approve join request: {e}", exc_info=True
                            )
                        finally:
                            loop.close()
            except Exception as e:
                logger.error(f"Error updating subscription: {e}", exc_info=True)


def handle_message_with_invite_link(update):
    """Handle messages that might contain invite links.

    Args:
        update: The update object from Telegram
    """
    message = update["message"]
    text = message["text"]
    user_id = str(message["from"]["id"])
    username = message["from"].get("username")

    # Check if this looks like an invite link
    if "t.me/+" in text or "t.me/joinchat/" in text:
        logger.info(f"Message with potential invite link from user {user_id}: {text}")

        # Extract the token from the invite link
        import re

        match = re.search(r"t\.me/(?:joinchat/|\+)([a-zA-Z0-9_-]+)", text)
        if match:
            invite_token = match.group(1)
            logger.info(f"Extracted invite token: {invite_token}")

            try:
                # Update the subscription with the Telegram user info
                subscription, error = (
                    SubscriptionService.update_subscription_with_telegram_user(
                        invite_token, user_id, username
                    )
                )

                if error:
                    logger.error(f"Failed to update subscription: {error}")
                else:
                    logger.info(f"Successfully updated subscription for user {user_id}")
            except Exception as e:
                logger.error(f"Error updating subscription: {e}", exc_info=True)


def handle_bot_chat_member_update(update):
    """Handle updates to the bot's chat member status.

    Args:
        update: The update object from Telegram
    """
    chat_member = update["my_chat_member"]
    chat = chat_member["chat"]

    # Only process group chats
    if chat["type"] not in ["group", "supergroup"]:
        return

    chat_id = str(chat["id"])
    chat_title = chat.get("title", "Unknown Group")
    new_status = chat_member["new_chat_member"]["status"]

    if new_status in ["member", "administrator"]:
        # Bot was added to a group or promoted to admin
        logger.info(f"Bot added to group: {chat_title} ({chat_id})")

        try:
            # Register the group in our database
            group = TelegramGroupService.create_or_update_group(chat_id, chat_title)
            logger.info(f"Successfully registered group: {group.id}")
        except Exception as e:
            logger.error(f"Error registering group: {e}", exc_info=True)

    elif new_status in ["left", "kicked"]:
        # Bot was removed from a group
        logger.info(f"Bot removed from group: {chat_title} ({chat_id})")

        try:
            # Mark the group as inactive in our database
            TelegramGroupService.mark_group_as_inactive(chat_id)
            logger.info(f"Marked group {chat_id} as inactive in database")
        except Exception as e:
            logger.error(f"Error marking group as inactive: {e}", exc_info=True)


def setup_handlers(application):
    """Set up handlers for the Telegram bot.

    Args:
        application: The Telegram application instance
    """
    # Add handlers for different types of updates
    application.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_chat_members_update
        )
    )
    application.add_handler(
        MessageHandler(
            filters.StatusUpdate.CHAT_CREATED, handle_bot_chat_member_update_obj
        )
    )
    application.add_handler(
        MessageHandler(filters.ChatType.GROUPS, handle_message_with_invite_link_update)
    )
    # Add handler for bot being added to or removed from a group
    from telegram.ext import ChatMemberHandler

    application.add_handler(ChatMemberHandler(handle_bot_chat_member_update_obj))

    # Add handler for chat join requests
    # application.add_handler(MessageHandler(filters.StatusUpdate.CHAT_JOIN_REQUEST, handle_chat_join_request_update))

    logger.info("Telegram handlers have been set up")


# Handler versions that work with Update objects directly


async def handle_new_chat_members_update(update: Update, context: CallbackContext):
    """Handle new members joining a chat/group with Update object.

    Args:
        update: The update object from Telegram
        context: The callback context
    """
    if not update.message or not update.message.new_chat_members:
        return

    message = update.message
    chat_id = str(message.chat.id)
    new_members = message.new_chat_members

    # Message object doesn't have invite_link attribute in this version
    invite_link = None

    logger.info(f"New members joining chat {chat_id}, invite link: {invite_link}")

    for member in new_members:
        # Skip if it's a bot
        if member.is_bot:
            continue

        user_id = str(member.id)
        username = member.username

        logger.info(f"Processing new member: {user_id} ({username}) to chat {chat_id}")

        # If we have an invite link, try to find the corresponding subscription
        if invite_link:
            # Extract the token from the invite link
            parts = invite_link.split("/")
            invite_token = parts[-1] if parts else None

            logger.info(f"Extracted invite token: {invite_token}")

            if invite_token:
                try:
                    # Update the subscription with the Telegram user info
                    subscription, error = (
                        SubscriptionService.update_subscription_with_telegram_user(
                            invite_token, user_id, username
                        )
                    )

                    if error:
                        logger.error(f"Failed to update subscription: {error}")
                    else:
                        logger.info(
                            f"Successfully updated subscription for user {user_id}"
                        )
                except Exception as e:
                    logger.error(f"Error updating subscription: {e}", exc_info=True)


async def handle_chat_join_request_update(update: Update, context: CallbackContext):
    """Handle chat join requests with Update object.

    Args:
        update: The update object from Telegram
        context: The callback context
    """
    if not update.chat_join_request:
        return

    join_request = update.chat_join_request
    chat_id = str(join_request.chat.id)
    user_id = str(join_request.from_user.id)
    username = join_request.from_user.username

    # Safely access invite_link if available
    invite_link = None
    try:
        if hasattr(join_request, "invite_link") and join_request.invite_link:
            invite_link = join_request.invite_link.invite_link
    except AttributeError:
        pass

    logger.info(
        f"Join request from user {user_id} ({username}) to chat {chat_id} with invite link: {invite_link}"
    )

    # If we have an invite link, try to find the corresponding subscription
    if invite_link:
        # Extract the token from the invite link
        parts = invite_link.split("/")
        invite_token = parts[-1] if parts else None

        if invite_token:
            try:
                # Update the subscription with the Telegram user info
                subscription, error = (
                    SubscriptionService.update_subscription_with_telegram_user(
                        invite_token, user_id, username
                    )
                )

                if error:
                    logger.error(f"Failed to update subscription: {error}")
                else:
                    logger.info(f"Successfully updated subscription for user {user_id}")

                    # Approve the join request
                    try:
                        await join_request.approve()
                        logger.info(
                            f"Approved join request for user {user_id} to chat {chat_id}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to approve join request: {e}", exc_info=True
                        )
            except Exception as e:
                logger.error(f"Error updating subscription: {e}", exc_info=True)


async def handle_message_with_invite_link_update(
    update: Update, context: CallbackContext
):
    """Handle messages that might contain invite links with Update object.

    Args:
        update: The update object from Telegram
        context: The callback context
    """
    if not update.message or not update.message.text:
        return

    message = update.message
    text = message.text
    user_id = str(message.from_user.id)
    username = message.from_user.username

    # Check if this looks like an invite link
    if "t.me/+" in text or "t.me/joinchat/" in text:
        logger.info(f"Message with potential invite link from user {user_id}: {text}")

        # Extract the token from the invite link
        import re

        match = re.search(r"t\.me/(?:joinchat/|\+)([a-zA-Z0-9_-]+)", text)
        if match:
            invite_token = match.group(1)
            logger.info(f"Extracted invite token: {invite_token}")

            try:
                # Update the subscription with the Telegram user info
                subscription, error = (
                    SubscriptionService.update_subscription_with_telegram_user(
                        invite_token, user_id, username
                    )
                )

                if error:
                    logger.error(f"Failed to update subscription: {error}")
                else:
                    logger.info(f"Successfully updated subscription for user {user_id}")
            except Exception as e:
                logger.error(f"Error updating subscription: {e}", exc_info=True)


async def handle_bot_chat_member_update_obj(update: Update, context: CallbackContext):
    """Handle updates to the bot's chat member status with Update object.

    Args:
        update: The update object from Telegram
        context: The callback context
    """
    if not update.my_chat_member:
        return

    chat_member = update.my_chat_member
    chat = chat_member.chat

    # Only process group chats
    if chat.type not in ["group", "supergroup"]:
        return

    chat_id = str(chat.id)
    chat_title = chat.title
    new_status = chat_member.new_chat_member.status

    if new_status in ["member", "administrator"]:
        # Bot was added to a group or promoted to admin
        logger.info(f"Bot added to group: {chat_title} ({chat_id})")

        try:
            from flask import current_app

            with current_app.app_context():

                group = TelegramGroupService.create_or_update_group(chat_id, chat_title)
                logger.info(f"Successfully registered group: {group.id}")
        except Exception as e:
            logger.error(f"Error registering group: {e}", exc_info=True)

    elif new_status in ["left", "kicked"]:
        # Bot was removed from a group
        logger.info(f"Bot removed from group: {chat_title} ({chat_id})")

        try:
            # Import the Flask app directly from the app package
            from app import create_app

            app = create_app()

            # Mark the group as inactive in our database using app context
            with app.app_context():
                TelegramGroupService.mark_group_as_inactive(chat_id)
                logger.info(f"Marked group {chat_id} as inactive in database")
        except Exception as e:
            logger.error(f"Error marking group as inactive: {e}", exc_info=True)
