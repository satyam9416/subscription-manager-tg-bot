from marshmallow import Schema, fields, validate, ValidationError


class SubscriptionSchema(Schema):
    id = fields.Int(dump_only=True)
    user_email = fields.Email(dump_only=True)
    user_tg_id = fields.Str(dump_only=True)
    user_tg_username = fields.Str(dump_only=True)
    user_email = fields.Email(dump_only=True)
    product_id = fields.Int(required=True)
    telegram_group_id = fields.Int(dump_only=True)
    invite_link_token = fields.Str(dump_only=True)
    invite_link_url = fields.Str(dump_only=True)
    invite_link_expires_at = fields.DateTime(dump_only=True)
    subscription_starts_at = fields.DateTime(dump_only=True)
    subscription_expires_at = fields.DateTime(dump_only=True)
    status = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    product = fields.Nested(
        "ProductSchema", only=("id", "name", "description"), dump_only=True
    )
    telegram_group = fields.Nested(
        "TelegramGroupSchema",
        only=("id", "telegram_group_id", "telegram_group_name"),
        dump_only=True,
    )


class SubscriptionRequestSchema(Schema):
    email = fields.Email(required=True)
    product_id = fields.Int()
    product_name = fields.Str()
    expiration_datetime = fields.DateTime(required=False)

    def validate(self, data):
        if not data.get("product_id") and not data.get("product_name"):
            raise ValidationError("Either product_id or product_name must be provided")
        return data


subscription_schema = SubscriptionSchema()
subscriptions_schema = SubscriptionSchema(many=True)
subscription_request_schema = SubscriptionRequestSchema()
