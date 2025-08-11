# selenium_web_automation_utils/logging_utils.py
import logging
from colorlog import ColoredFormatter

# ——————————————————————————————————————————————
# 1) Create logger
# ——————————————————————————————————————————————
logger = logging.getLogger("selenium_web_automation")
logger.setLevel(logging.INFO)  # default level

# ——————————————————————————————————————————————
# 2) Create console handler with color
# ——————————————————————————————————————————————
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# choose your format & colors
formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s (webdriver)%(reset)s %(message)s",
    log_colors={
        "DEBUG":    "cyan",
        "INFO":     "green",
        "WARNING":  "yellow",
        "ERROR":    "red",
        "CRITICAL": "bold_red",
    },
    reset=True,
    secondary_log_colors={},
    style="%",
)

console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# prevent messages from also going to the root logger
logger.propagate = False
