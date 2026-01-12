import logging
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# ------------------------
# Agent Logger
# ------------------------
agent_logger = logging.getLogger("agent")
agent_logger.setLevel(logging.DEBUG)  # Capture all levels

# Formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# File handler → INFO+ messages
info_handler = logging.FileHandler("logs/agent.log")
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)
agent_logger.addHandler(info_handler)

# File handler → DEBUG+ messages
debug_handler = logging.FileHandler("logs/agent_debug.log")
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(formatter)
agent_logger.addHandler(debug_handler)

# Console handler → INFO+ messages
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
agent_logger.addHandler(console_handler)

# Logging helpers
def log_info(message):
    agent_logger.info(message)

def log_debug(message):
    agent_logger.debug(message)

def log_error(message):
    agent_logger.error(message)
