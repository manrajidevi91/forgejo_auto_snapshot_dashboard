
from utils.logger import app_logger as logger

# This service will be responsible for creating notifications (e.g., toasts).
# In a Flask app, this might involve using websockets or SSE to push notifications to the client.

def send_toast(message, category='info'):
    """Placeholder for sending a toast notification."""
    logger.info(f"NOTIFICATION: [{category.upper()}] {message}")
    # This would eventually trigger a frontend event.
    pass
