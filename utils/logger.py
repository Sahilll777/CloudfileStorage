# utils/logger.py
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_action(user_id, action, filename=None):
    msg = f"User {user_id} performed {action}"
    if filename:
        msg += f" on file '{filename}'"
    logging.info(msg)
