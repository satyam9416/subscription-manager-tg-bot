from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.services import TelegramGroupService
from app.schemas import telegram_group_schema, telegram_groups_schema

group_bp = Blueprint("group", __name__)


@group_bp.route("/groups", methods=["GET"])
def get_groups():
    status = request.args.get("status")  # 'active' | 'inactive' | None
    role = request.args.get("role")  # e.g., 'member' | 'administrator' | 'left'
    groups = TelegramGroupService.get_all_groups(status=status, role=role)
    return jsonify(telegram_groups_schema.dump(groups)), 200


@group_bp.route("/groups/unmapped", methods=["GET"])
def get_unmapped_groups():
    groups = TelegramGroupService.get_unmapped_groups()
    return jsonify(telegram_groups_schema.dump(groups)), 200


@group_bp.route("/products/<int:product_id>/map", methods=["POST"])
def map_product_to_group(product_id):
    try:
        data = request.json
        if (
            not data
            or "telegram_group_id" not in data
            or "telegram_group_name" not in data
        ):
            return (
                jsonify(
                    {
                        "message": "Missing required fields: telegram_group_id and telegram_group_name"
                    }
                ),
                400,
            )

        group, error = TelegramGroupService.map_product_to_group(
            product_id, data["telegram_group_id"], data["telegram_group_name"]
        )

        if error:
            return jsonify({"message": error}), 400

        return jsonify(telegram_group_schema.dump(group)), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@group_bp.route("/products/<int:product_id>/unmap", methods=["DELETE"])
def unmap_product(product_id):
    try:
        success = TelegramGroupService.unmap_product(product_id)
        if not success:
            return jsonify({"message": "No mapping found for this product"}), 404
        return jsonify({"message": "Product unmapped successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@group_bp.route("/groups/<string:telegram_group_id>", methods=["DELETE"])
def remove_bot_and_delete_group(telegram_group_id):
    try:
        success = TelegramGroupService.remove_bot_and_delete(telegram_group_id)
        if not success:
            return jsonify({"message": "Group not found"}), 404
        return jsonify({"message": "Bot removed and group deleted"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@group_bp.route("/groups/<string:telegram_group_id>/message", methods=["POST"])
def send_message_to_group(telegram_group_id):
    try:
        data = request.json or {}
        text = data.get("text")
        if not text or not isinstance(text, str) or not text.strip():
            return jsonify({"message": "'text' is required"}), 400

        from app.services.telegram import tg_bot

        success, message = tg_bot.send_message(int(telegram_group_id), text.strip())
        status_code = 200 if success else 500
        return jsonify({"message": message, "success": success}), status_code
    except ValueError:
        return jsonify({"message": "Invalid telegram_group_id"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500
