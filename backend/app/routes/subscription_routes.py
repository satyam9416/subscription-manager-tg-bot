from flask import Blueprint, request, jsonify
from app.models import User
from marshmallow import ValidationError
from app.services import SubscriptionService
from app.schemas import (
    subscription_schema,
    subscriptions_schema,
    subscription_request_schema,
)
import logging

subscription_bp = Blueprint("subscription", __name__)


@subscription_bp.route("/subscriptions", methods=["GET"])
def get_subscriptions():
    # Get query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    sort_by = request.args.get("sort_by", "created_at")
    sort_order = request.args.get("sort_order", "desc")
    search = request.args.get("search")
    status = request.args.get("status")
    product_id = request.args.get("product_id", type=int)
    user_id = request.args.get("user_id", type=int)
    
    # Limit per_page to prevent performance issues
    per_page = min(per_page, 100)
    
    # Get paginated subscriptions
    result = SubscriptionService.get_all_subscriptions(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
        status=status,
        product_id=product_id,
        user_id=user_id
    )
    
    # Return paginated response
    return jsonify({
        "items": subscriptions_schema.dump(result["items"]),
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "pages": result["pages"]
    }), 200


@subscription_bp.route("/subscribe", methods=["POST"])
def create_subscription():
    try:
        data = subscription_request_schema.load(request.json)
        expiration_datetime = data.get("expiration_datetime")

        if data.get("product_id"):
            subscription, error = SubscriptionService.create_subscription(
                data["email"],
                data["product_id"],
                expiration_datetime,
                bool(request.args.get("force_renew", type=int)),
            )
        else:
            subscription, error = (
                SubscriptionService.create_subsciption_by_product_name(
                    data["email"],
                    data["product_name"],
                    expiration_datetime,
                    bool(request.args.get("force_renew", type=int)),
                )
            )

        if error:
            return jsonify({"message": error}), 400

        # Return only necessary information to the user
        result = {
            "message": "Subscription created successfully",
            "invite_link": subscription.invite_link_url,
            "invite_expires_at": subscription.invite_link_expires_at,
            "subscription_expires_at": subscription.subscription_expires_at,
        }

        return jsonify(result), 201
    except ValidationError as e:
        return jsonify({"message": "Validation error", "errors": e.messages}), 400
    except Exception as e:
        logging.exception("Error creating subscription")
        return jsonify({"message": str(e)}), 500


@subscription_bp.route("/subscriptions", methods=["DELETE"])
def cancel_subscription_by_email():
    try:
        data = subscription_request_schema.load(request.json)
        subscription, error = (
            SubscriptionService.cancel_subscription_by_email_and_product_id(
                data["email"], data["product_id"]
            )
        )

        if error:
            return jsonify({"message": error}), 400

        return jsonify({"message": "Subscription cancelled successfully"}), 200
    except ValidationError as e:
        return jsonify({"message": "Validation error", "errors": e.messages}), 400
    except Exception as e:
        logging.exception("Error cancelling subscription")
        return jsonify({"message": str(e)}), 500


@subscription_bp.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "email": user.email
        })
    return jsonify(result), 200

@subscription_bp.route("/subscriptions/<int:subscription_id>/cancel", methods=["POST"])
def cancel_subscription(subscription_id):
    try:
        subscription, error = SubscriptionService.cancel_subscription(subscription_id)

        if error:
            return jsonify({"message": error}), 400

        return jsonify({"message": "Subscription cancelled successfully"}), 200
    except ValidationError as e:
        return jsonify({"message": "Validation error", "errors": e.messages}), 400
    except Exception as e:
        logging.exception("Error cancelling subscription")
        return jsonify({"message": str(e)}), 500
