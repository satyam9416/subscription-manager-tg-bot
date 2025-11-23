from datetime import datetime, timezone
from app import db


class Subscription(db.Model):
    __tablename__ = "subscriptions"
    # __table_args__ = (
    #     db.UniqueConstraint(
    #         "user_email", "product_id", name="uix_user_email_product_id"
    #     ),
    # )

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    telegram_group_id = db.Column(
        db.Integer, db.ForeignKey("telegram_groups.id"), nullable=False
    )
    invite_link_token = db.Column(db.String(255), unique=True, nullable=True)
    invite_link_url = db.Column(db.String(512), nullable=True)
    invite_link_expires_at = db.Column(db.DateTime, nullable=True)

    subscription_starts_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    subscription_expires_at = db.Column(db.DateTime, nullable=False)

    status = db.Column(
        db.String(20), default="pending_join"
    )  # pending_join, active, expired, cancelled
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # user details
    user_email = db.Column(db.String(120), nullable=False)
    user_tg_id = db.Column(db.String(120), nullable=True)
    user_tg_username = db.Column(db.String(120), nullable=True)

    # Relationships
    product = db.relationship("Product", back_populates="subscriptions")
    telegram_group = db.relationship("TelegramGroup", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription {self.id} - User: {self.user_email}, Product: {self.product_id}>"
