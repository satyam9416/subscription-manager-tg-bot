from app import db
from app.models import TelegramGroup, Product
from sqlalchemy.exc import SQLAlchemyError


class TelegramGroupService:
    @staticmethod
    def get_all_groups(status: str = None, role: str = None):
        query = TelegramGroup.query
        if status == "active":
            query = query.filter_by(is_active=True)
        elif status == "inactive":
            query = query.filter_by(is_active=False)

        if role:
            query = query.filter_by(bot_role=role)

        return query.all()

    @staticmethod
    def get_unmapped_groups():
        return TelegramGroup.query.filter_by(product_id=None).all()

    @staticmethod
    def get_group_by_id(group_id):
        return TelegramGroup.query.get(group_id)

    @staticmethod
    def get_group_by_telegram_id(telegram_group_id):
        # Convert telegram_group_id to string
        telegram_group_id_str = str(telegram_group_id)
        return TelegramGroup.query.filter_by(
            telegram_group_id=telegram_group_id_str
        ).first()

    @staticmethod
    def create_or_update_group(telegram_group_id, telegram_group_name):
        try:
            # Convert telegram_group_id to string to match database column type
            telegram_group_id_str = str(telegram_group_id)

            group = TelegramGroup.query.filter_by(
                telegram_group_id=telegram_group_id_str
            ).first()

            if not group:
                group = TelegramGroup(
                    telegram_group_id=telegram_group_id_str,
                    telegram_group_name=telegram_group_name,
                )
                db.session.add(group)
            else:
                group.telegram_group_name = telegram_group_name
                group.is_active = True

            db.session.commit()
            return group
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def map_product_to_group(product_id, telegram_group_id, telegram_group_name):
        try:
            # Check if product exists
            product = Product.query.get(product_id)
            if not product:
                return None, "Product not found"

            # Check if product is already mapped to a group
            if product.telegram_group:
                return None, "Product is already mapped to a group"

            # Convert telegram_group_id to string
            telegram_group_id_str = str(telegram_group_id)

            # Get or create the telegram group
            group = TelegramGroup.query.filter_by(
                telegram_group_id=telegram_group_id_str
            ).first()
            if not group:
                group = TelegramGroup(
                    telegram_group_id=telegram_group_id_str,
                    telegram_group_name=telegram_group_name,
                )
                db.session.add(group)
            elif group.product_id:
                return None, "Telegram group is already mapped to another product"

            # Map the product to the group
            group.product_id = product_id
            db.session.commit()
            return group, None
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def unmap_product(product_id):
        try:
            # Find the group mapped to this product
            group = TelegramGroup.query.filter_by(product_id=product_id).first()
            if not group:
                return False

            # Unmap the product
            group.product_id = None
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def mark_group_as_inactive(telegram_group_id):
        try:
            # Convert telegram_group_id to string
            telegram_group_id_str = str(telegram_group_id)

            group = TelegramGroup.query.filter_by(
                telegram_group_id=telegram_group_id_str
            ).first()
            if group:
                group.is_active = False
                group.bot_role = "left"
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_group_by_id(telegram_group_id):
        try:
            # Convert telegram_group_id to string
            telegram_group_id_str = str(telegram_group_id)

            group = TelegramGroup.query.filter_by(
                telegram_group_id=telegram_group_id_str
            ).first()
            if group:
                db.session.delete(group)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def set_bot_role(telegram_group_id, bot_role: str, is_active: bool = None):
        try:
            telegram_group_id_str = str(telegram_group_id)
            group = TelegramGroup.query.filter_by(
                telegram_group_id=telegram_group_id_str
            ).first()
            if not group:
                return False

            group.bot_role = bot_role
            if is_active is not None:
                group.is_active = is_active

            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def remove_bot_and_delete(telegram_group_id):
        from app.services.telegram import tg_bot

        # Always attempt to leave chat; ignore failures
        try:
            tg_bot.leave_chat(int(telegram_group_id))
        except Exception:
            pass

        # Delete the group record
        return TelegramGroupService.delete_group_by_id(telegram_group_id)
