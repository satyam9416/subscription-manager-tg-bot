from marshmallow import Schema, fields


class TelegramGroupSchema(Schema):
    id = fields.Str(dump_only=True)
    telegram_group_id = fields.Str(required=True)
    telegram_group_name = fields.Str(required=True)
    bot_role = fields.Str(allow_none=True)
    product_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    is_active = fields.Bool(dump_only=True)

    # Include product information if available
    product = fields.Nested(
        "ProductSchema", exclude=("telegram_group",), dump_only=True
    )


telegram_group_schema = TelegramGroupSchema()
telegram_groups_schema = TelegramGroupSchema(many=True)
