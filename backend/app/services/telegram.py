import logging
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
from telegram import Update, ChatMember, Bot
from telegram.ext import (
    Application,
    ChatMemberHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ChatJoinRequestHandler,
)
from telegram.constants import ChatMemberStatus
from telegram.error import TelegramError
import threading
from concurrent.futures import ThreadPoolExecutor


# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramGroupBotService:
    def __init__(self, bot_token: str = None):
        self.bot_token = bot_token
        self.application = Application.builder().token(bot_token).build()
        self.bot = Bot(token=bot_token)

        # Threading for running bot alongside Flask
        self.bot_thread = None
        self.running = False
        self.event_loop = None
        self.executor = ThreadPoolExecutor(max_workers=4)

        self.setup_handlers()

    def init_app(self, app):
        self.app = app

    def setup_handlers(self):
        """Setup all event handlers"""
        # Chat member updates (bot added/removed, user joins/leaves)
        self.application.add_handler(
            ChatMemberHandler(
                self._handle_chat_member_update, ChatMemberHandler.CHAT_MEMBER
            )
        )

        # My chat member updates (specifically for bot being added/removed)
        self.application.add_handler(
            ChatMemberHandler(
                self._handle_my_chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER
            )
        )

        # Message handler for tracking joins via invite links
        self.application.add_handler(
            MessageHandler(
                filters.StatusUpdate.NEW_CHAT_MEMBERS, self._handle_new_members
            )
        )

        self.application.add_handler(ChatJoinRequestHandler(self._handle_join_request))

    async def _handle_my_chat_member_update(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle bot being added or removed from groups"""
        try:
            chat = update.effective_chat
            new_member = update.my_chat_member.new_chat_member
            old_member = update.my_chat_member.old_chat_member

            # Bot added to group
            if old_member.status in [
                ChatMemberStatus.LEFT,
            ] and new_member.status in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
            ]:
                await self._on_bot_added_to_group(chat, context)

            if new_member.status in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
            ]:
                # Persist role
                def run_in_flask_context():
                    with self.app.app_context():
                        from app.services.telegram_group_service import (
                            TelegramGroupService,
                        )

                        role_value = (
                            "administrator"
                            if new_member.status == ChatMemberStatus.ADMINISTRATOR
                            else "member"
                        )
                        TelegramGroupService.set_bot_role(chat.id, role_value)

                self.executor.submit(run_in_flask_context)

            # Bot removed from group
            elif old_member.status in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
            ] and new_member.status in [ChatMemberStatus.LEFT]:
                await self._on_bot_removed_from_group(chat, context)

        except Exception as e:
            logger.exception(f"Error handling my chat member update: {e}")

    async def _handle_chat_member_update(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle regular chat member updates (users joining/leaving)"""
        try:
            chat = update.effective_chat
            user = update.chat_member.from_user
            new_member = update.chat_member.new_chat_member
            old_member = update.chat_member.old_chat_member

            # User joined the group
            if old_member.status in [
                ChatMemberStatus.LEFT,
            ] and new_member.status in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.RESTRICTED,
            ]:
                await self._on_user_joined_group(chat, user, context)

            # User left the group
            elif old_member.status in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.RESTRICTED,
            ] and new_member.status in [ChatMemberStatus.LEFT]:
                await self._on_user_left_group(chat, user, context)

        except Exception as e:
            logger.error(f"Error handling chat member update: {e}")

    async def _handle_new_members(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle new members joining via invite links"""
        try:
            chat = update.effective_chat
            new_members = update.message.new_chat_members

            for member in new_members:
                # Try to identify which invite link was used
                invite_token = await self._identify_invite_token(
                    chat.id, member.id, context
                )
                if invite_token:
                    await self._on_user_joined_via_invite(
                        chat, member, invite_token, context
                    )

        except Exception as e:
            logger.error(f"Error handling new members: {e}")

    async def _on_bot_added_to_group(self, chat, context: ContextTypes.DEFAULT_TYPE):
        """Called when bot is added to a group"""

        logger.info(f"🟢 Bot added to group: {chat.title} (ID: {chat.id})")

        # Run Flask context operations in a thread
        def run_in_flask_context():
            with self.app.app_context():
                from app.services.telegram_group_service import TelegramGroupService

                TelegramGroupService.create_or_update_group(chat.id, chat.title)
                TelegramGroupService.set_bot_role(chat.id, "member", is_active=True)

        # Execute in thread pool to avoid blocking
        self.executor.submit(run_in_flask_context)

        # Send welcome message
        try:
            welcome_text = (
                f"🎉 Hello! I've been added to **{chat.title}**\n\n"
                "I can help you manage this group with the following features:\n"
                "• Track invite links with custom tokens\n"
                "• Remove users via API\n"
                "• Monitor group activities\n\n"
                "The bot is now ready to receive API commands!"
            )
            await context.bot.send_message(
                chat_id=chat.id, text=welcome_text, parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Could not send welcome message: {e}")

    async def _on_bot_removed_from_group(
        self, chat, context: ContextTypes.DEFAULT_TYPE
    ):
        """Called when bot is removed from a group"""
        logger.info(f"🔴 Bot removed from group: {chat.title} (ID: {chat.id})")

        # Run Flask context operations in a thread
        def run_in_flask_context():
            with self.app.app_context():
                from app.services.telegram_group_service import TelegramGroupService

                TelegramGroupService.set_bot_role(chat.id, "left", is_active=False)
                TelegramGroupService.delete_group_by_id(chat.id)

        self.executor.submit(run_in_flask_context)

    async def _on_user_joined_group(
        self, chat, user, context: ContextTypes.DEFAULT_TYPE
    ):
        """Called when a user joins the group"""
        logger.info(
            f"👤 User {user.full_name} (ID: {user.id}) joined group {chat.title}"
        )

    async def _on_user_left_group(self, chat, user, context: ContextTypes.DEFAULT_TYPE):
        """Called when a user leaves the group"""
        logger.info(f"👋 User {user.full_name} (ID: {user.id}) left group {chat.title}")

    async def _on_user_joined_via_invite(
        self, chat, user, invite_token: str, context: ContextTypes.DEFAULT_TYPE
    ):
        """Called when a user joins via a tracked invite link"""
        logger.info(
            f"🔗 User {user.full_name} (ID: {user.id}) joined {chat.title} via invite token: {invite_token}"
        )

        # Run Flask context operations in a thread
        def run_in_flask_context():
            with self.app.app_context():
                from app.services.subscription_service import SubscriptionService

                SubscriptionService.update_subscription_with_telegram_user(
                    invite_token, user.id, user.username
                )

        self.executor.submit(run_in_flask_context)

    async def _identify_invite_token(
        self, chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE
    ) -> Optional[str]:
        """Try to identify which invite link was used"""
        return None

    async def _handle_join_request(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handles chat join requests and approves/declines based on the invite link name.
        """
        join_request = update.chat_join_request
        chat_id = join_request.chat.id
        user_id = join_request.from_user.id
        user_name = join_request.from_user.full_name
        invite_link_name = (
            join_request.invite_link.name if join_request.invite_link else "N/A"
        )
        invite_link_url = (
            join_request.invite_link.invite_link if join_request.invite_link else "N/A"
        )

        logger.info(
            f"Received join request from {user_name} (ID: {user_id}) for chat {chat_id} "
            f"via link '{invite_link_name}' ({invite_link_url})"
        )

        with self.app.app_context():
            from app.services.subscription_service import SubscriptionService

            subsciption = SubscriptionService.get_subscription_by_invite_token(
                invite_link_name
            )

        if not subsciption:
            logger.error(f"Subscription not found for invite token: {invite_link_name}")
            return

        if subsciption.status == "pending_join":
            try:
                await join_request.approve()
                # Send a confirmation message to the chat
                # await context.bot.send_message(
                #     chat_id=chat_id,
                #     text=f"✅ Join request from {user_name} via link '{invite_link_name}' has been automatically APPROVED.",
                # )
                logger.info(
                    f"Approved join request for {user_name} via link '{invite_link_name}'"
                )

                with self.app.app_context():
                    SubscriptionService.update_subscription_with_telegram_user(
                        invite_link_name, user_id, user_name
                    )

                    SubscriptionService.update_subscription_status(
                        subsciption.id, "active"
                    )

            except Exception as e:
                logger.error(f"Failed to approve join request for {user_name}: {e}")
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"❌ Failed to approve join request from {user_name} via link '{invite_link_name}'. Error: {e}",
                )
            finally:
                return

        if subsciption.status == "active":
            logger.info(
                f"Subscription already active for invite token: {invite_link_name}"
            )

        if (
            subsciption.status == "expired"
            or subsciption.subscription_expires_at > datetime.now()
        ):
            logger.info(f"Subscription expired for invite token: {invite_link_name}")

        if subsciption.status == "cancelled":
            logger.info(f"Subscription cancelled for invite token: {invite_link_name}")

        try:
            await join_request.decline()
            # Send a confirmation message to the chat
            # await context.bot.send_message(
            #     chat_id=chat_id,
            #     text=f"🚫 Join request from {user_name} via link '{invite_link_name}' has been automatically DECLINED. "
            #     "This link does not meet auto-approval criteria.",
            # )
            logger.info(
                f"Declined join request for {user_name} via link '{invite_link_name}'"
            )
        except Exception as e:
            logger.error(f"Failed to decline join request for {user_name}: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ Failed to decline join request from {user_name} via link '{invite_link_name}'. Error: {e}",
            )

    # Helper method to run async function in bot's event loop
    def _run_async_in_bot_loop(self, coro):
        """Run an async coroutine in the bot's event loop"""
        if self.event_loop and self.event_loop.is_running():
            # If event loop is running, schedule the coroutine
            future = asyncio.run_coroutine_threadsafe(coro, self.event_loop)
            return future.result(timeout=60)  # 30 second timeout
        else:
            # If no event loop is running, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()

    # API METHODS

    async def create_invite_link_aysnc(
        self, chat_id: int, token: str
    ) -> Tuple[bool, str, Optional[str]]:
        """
        API method to create an invite link with custom token
        Returns: (success: bool, message: str, invite_link: Optional[str])
        """
        try:
            # Check if chat exists in our records

            # Get chat info
            try:
                chat = await self.bot.get_chat(chat_id)
            except TelegramError as e:
                return False, f"Could not access chat: {str(e)}", None

            # Create invite link
            invite_link = await self.bot.create_chat_invite_link(
                chat_id=chat_id,
                name=token,
                member_limit=None,
                expire_date=None,
                creates_join_request=True,
            )

            logger.info(
                f"✅ API: Created invite link for chat {chat_id} with token {token}"
            )
            return True, "Invite link created successfully", invite_link.invite_link

        except Exception as e:
            logger.error(f"❌ API: Error creating invite link: {e}")
            return False, f"Error creating invite link: {str(e)}", None

    async def remove_user_api_async(
        self, chat_id: int, user_id: int
    ) -> Tuple[bool, str]:
        """
        API method to remove a user from a group
        Returns: (success: bool, message: str)
        """
        try:

            # Check if user exists in chat
            try:
                member = await self.bot.get_chat_member(chat_id, user_id)
                if member.status in [ChatMemberStatus.LEFT]:
                    return False, f"User {user_id} is not in the chat"
            except TelegramError as e:
                return False, f"Could not find user in chat: {str(e)}"

            # Remove user
            await self.bot.ban_chat_member(chat_id, user_id)
            await self.bot.unban_chat_member(
                chat_id, user_id
            )  # Unban to allow rejoining

            logger.info(f"✅ API: Removed user {user_id} from chat {chat_id}")
            return True, f"User {user_id} removed successfully"

        except Exception as e:
            logger.error(f"❌ API: Error removing user: {e}")
            return False, f"Error removing user: {str(e)}"

    # SYNCHRONOUS WRAPPERS

    def create_invite_link(
        self, chat_id: int, token: str
    ) -> Tuple[bool, str, Optional[str]]:
        """Synchronous wrapper for create_invite_link_aysnc"""
        return self._run_async_in_bot_loop(
            self.create_invite_link_aysnc(chat_id, token)
        )

    def remove_user(self, chat_id: int, user_id: int) -> Tuple[bool, str]:
        """Synchronous wrapper for remove_user_api_async"""
        return self._run_async_in_bot_loop(self.remove_user_api_async(chat_id, user_id))

    async def leave_chat_async(self, chat_id: int) -> Tuple[bool, str]:
        try:
            await self.bot.leave_chat(chat_id)
            logger.info(f"✅ Bot left chat {chat_id}")
            return True, "Bot left the chat"
        except Exception as e:
            logger.error(f"❌ Error leaving chat {chat_id}: {e}")
            return False, f"Error leaving chat: {str(e)}"

    def leave_chat(self, chat_id: int) -> Tuple[bool, str]:
        return self._run_async_in_bot_loop(self.leave_chat_async(chat_id))

    # BOT LIFECYCLE MANAGEMENT

    def start_bot(self):
        """Start the bot in a separate thread"""

        def run_bot():
            logger.info("🚀 Starting Telegram Bot Service...")
            self.running = True

            # Create and set the event loop for the bot thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.event_loop = loop

            try:
                self.application.run_polling(allowed_updates=Update.ALL_TYPES)
            except Exception as e:
                logger.error(f"Error running bot: {e}")
            finally:
                self.running = False
                self.event_loop = None

        if not self.running:
            self.bot_thread = threading.Thread(target=run_bot, daemon=True)
            self.bot_thread.start()
            logger.info("✅ Bot service started in background thread")

    def stop_bot(self):
        """Stop the bot"""
        if self.running:
            self.running = False
            if self.application.updater:
                self.application.updater.stop()
            logger.info("🛑 Bot service stopped")

        if self.event_loop.is_running():
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)
            logger.info("🛑 Bot event loop stopped")


import os

tg_bot = TelegramGroupBotService(os.environ.get("TELEGRAM_BOT_TOKEN"))
