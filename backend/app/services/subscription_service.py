from datetime import datetime, timedelta, timezone
from app import db
from app.models import User, Product, TelegramGroup, Subscription
from sqlalchemy.exc import SQLAlchemyError
from app.bot.telegram_client import generate_invite_link
from app.services.telegram import tg_bot


class SubscriptionService:
    @staticmethod
    def get_all_subscriptions(
        page=1,
        per_page=10,
        sort_by="created_at",
        sort_order="desc",
        search=None,
        status=None,
        product_id=None,
        user_id=None,
    ):
        query = Subscription.query

        # Apply filters
        if status:
            query = query.filter(Subscription.status == status)

        if product_id:
            query = query.filter(Subscription.product_id == product_id)

        if user_id:
            query = query.filter(Subscription.user_id == user_id)

        # Apply search
        if search:
            # Join with User to search by email
            query = query.join(User).filter(User.email.ilike(f"%{search}%"))

        # Apply sorting
        if sort_by == "email":
            # Join with User to sort by email
            query = query.join(User, isouter=True)
            if sort_order == "asc":
                query = query.order_by(User.email.asc())
            else:
                query = query.order_by(User.email.desc())
        else:
            # Sort by Subscription attributes
            sort_column = getattr(Subscription, sort_by, Subscription.created_at)
            if sort_order == "asc":
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())

        # Apply pagination
        total = query.count()
        query = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "items": query.items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,  # Ceiling division
        }

    @staticmethod
    def get_subscription_by_id(subscription_id):
        return Subscription.query.get(subscription_id)

    @staticmethod
    def get_subscription_by_invite_token(invite_token):
        return Subscription.query.filter_by(invite_link_token=invite_token).first()

    @staticmethod
    def get_active_subscriptions_by_user_id(user_id):
        return Subscription.query.filter_by(user_id=user_id, status="active").all()

    @staticmethod
    def get_expired_subscriptions():
        now = datetime.utcnow()
        return Subscription.query.filter(
            Subscription.status == "active", Subscription.subscription_expires_at <= now
        ).all()

    @staticmethod
    def create_subsciption_by_product_name(
        email,
        product_name,
        expiration_datetime=None,
        force_renew=False,
    ):
        product = Product.query.filter_by(name=product_name).first()
        if not product:
            return None, "Product not found"
        return SubscriptionService.create_subscription(
            email, product.id, expiration_datetime, force_renew
        )

    @staticmethod
    def create_subscription(
        email: str,
        product_id: int,
        expiration_datetime: datetime = None,
        force_renew: bool = False,
    ):
        # Set default expiration to 30 days from now if not provided
        subscription_expires_at = (
            expiration_datetime
            if expiration_datetime
            else datetime.now(timezone.utc) + timedelta(days=30)
        )
        try:
            # Check if product exists and has a mapped group
            product = Product.query.get(product_id)
            if not product:
                return None, "Product not found"

            if not product.telegram_group:
                return None, "Product is not mapped to a Telegram group"

            # Get or create user
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(email=email)
                db.session.add(user)
                db.session.flush()  # Get user ID without committing

            # Check if user already has an active subscription for this product
            existing_subscription = Subscription.query.filter(
                Subscription.user_id == user.id,
                Subscription.product_id == product_id,
                Subscription.status.in_(["active", "pending_join"]),
            ).first()

            if existing_subscription and not force_renew:
                return None, "User already has an ongoing subscription for this product"

            if existing_subscription:
                SubscriptionService.cancel_subscription_by_email_and_product_id(
                    email, product_id
                )

            subscription = Subscription(
                user_id=user.id,
                product_id=product_id,
                telegram_group_id=product.telegram_group.id,
                subscription_expires_at=subscription_expires_at,
                status="pending_join",
            )
            db.session.add(subscription)
            db.session.flush()  # Get subscription ID without committing

            import uuid

            invite_token = str(uuid.uuid4())[:32]
            success, _, invite_link = tg_bot.create_invite_link(
                product.telegram_group.telegram_group_id, invite_token
            )

            if not success or not invite_link:
                db.session.rollback()
                return None, "Failed to generate invite link"

            subscription.invite_link_url = invite_link
            subscription.invite_link_token = invite_token
            subscription.invite_link_expires_at = subscription_expires_at

            db.session.commit()
            return subscription, None
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def update_subscription_with_telegram_user(
        invite_token, telegram_user_id, telegram_username
    ):
        try:
            subscription = Subscription.query.filter_by(
                invite_link_token=invite_token
            ).first()
            if not subscription:
                return None, "Subscription not found"

            # Update user with Telegram information
            user = subscription.user
            user.telegram_user_id = telegram_user_id
            user.telegram_username = telegram_username

            # Update subscription status
            subscription.status = "active"

            db.session.commit()
            return subscription, None
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def expire_subscription(subscription_id):
        try:
            subscription = Subscription.query.get(subscription_id)
            if not subscription:
                return False

            subscription.status = "expired"
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def cancel_subscription(subscription_id):
        try:
            subscription = Subscription.query.get(subscription_id)
            if not subscription:
                return None, "Subscription not found"

            return SubscriptionService.cancel_subscription_by_email_and_product_id(
                subscription.user.email, subscription.product_id
            )

        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def cancel_subscription_by_email_and_product_id(email, product_id):
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                return None, "User not found"

            subscription = Subscription.query.filter(
                Subscription.user_id == user.id,
                Subscription.product_id == product_id,
                Subscription.status.in_(["active", "pending_join"]),
            ).first()
            if not subscription:
                return None, "Subscription not found"

            tg_bot.remove_user(
                subscription.telegram_group.telegram_group_id, user.telegram_user_id
            )

            subscription.status = "cancelled"

            db.session.commit()
            return subscription, None

        except Exception as e:
            db.session.rollback()
            raise e

    def update_subscription_status(subscription_id, new_status):

        if new_status not in ["pending_join", "active", "expired", "cancelled"]:
            raise ValueError("Invalid status")

        try:
            subscription = Subscription.query.get(subscription_id)
            if not subscription:
                return False

            subscription.status = new_status
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
