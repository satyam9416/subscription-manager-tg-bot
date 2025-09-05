import os
import logging
from flask import Blueprint, request, jsonify
from app.bot.telegram_handler import process_update
from app.services.telegram import get_telegram_bot_service

# Configure logging
logger = logging.getLogger(__name__)

telegram_bp = Blueprint('telegram', __name__)

@telegram_bp.route('/telegram/webhook/<token>', methods=['POST'])
def telegram_webhook(token):
    # Verify the token
    if token != os.environ.get('TELEGRAM_BOT_TOKEN'):
        logger.warning(f"Invalid token received in webhook: {token}")
        return jsonify({'message': 'Invalid token'}), 401
    
    # Check if we're using webhooks
    import os
    USE_WEBHOOKS = os.environ.get("USE_WEBHOOKS", "false").lower() == "true"
    if not USE_WEBHOOKS:
        logger.info("Webhook received but system is configured to use handlers instead")
        return jsonify({'message': 'System is using handlers, not webhooks'}), 200
    
    # Process the update
    try:
        update = request.json
        logger.info(f"Received Telegram update: {update}")
        process_update(update)
        return jsonify({'message': 'Update processed successfully'}), 200
    except Exception as e:
        logger.error(f"Error processing Telegram update: {e}")
        return jsonify({'message': f'Error processing update: {str(e)}'}), 500

@telegram_bp.route('/telegram/webhook/test', methods=['GET'])
def test_webhook():
    """Test endpoint to verify the webhook is working"""
    tg_bot = get_telegram_bot_service()
    if not tg_bot:
        return jsonify({'message': 'Bot service not initialized'}), 500
    
    try:
        # Use the new service's bot instance
        webhook_info = tg_bot._run_async_in_bot_loop(tg_bot.bot.get_webhook_info())
        return jsonify({
            'message': 'Webhook info retrieved successfully',
            'webhook_url': webhook_info.url if webhook_info else None,
            'bot_running': tg_bot.running,
            'bot_token_prefix': tg_bot.bot_token[:10] + '***' if tg_bot.bot_token else None
        }), 200
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return jsonify({'message': f'Error getting webhook info: {str(e)}'}), 500