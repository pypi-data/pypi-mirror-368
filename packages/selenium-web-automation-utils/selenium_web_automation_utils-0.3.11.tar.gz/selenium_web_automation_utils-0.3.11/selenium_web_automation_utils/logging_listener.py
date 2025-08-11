# selenium_web_automation_utils/logging_listener.py
import re

from selenium.webdriver.support.events import AbstractEventListener
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime
from selenium_web_automation_utils.logging_utils import logger
from selenium.common.exceptions import (
    WebDriverException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException
)


def clean_error_partition(e: Exception) -> str:
    """
    Return a concise, user-friendly Selenium error message.
    - Prefer e.msg if present (WebDriverException subclasses).
    - Strip 'Stacktrace', 'For documentation...', and '(Session info: ...)' tails.
    """
    raw = getattr(e, "msg", str(e))
    msg = raw.split("Stacktrace", 1)[0]

    # Remove "For documentation..." trailers and "(Session info: ...)" tails (case-insensitive)
    msg = re.sub(r"\s*For documentation.*?$", "", msg, flags=re.I | re.S)
    msg = re.sub(r"\s*\(Session info:.*?$", "", msg, flags=re.I | re.S)

    return msg.strip()


class LoggingListener(AbstractEventListener):

    def before_navigate_to(self, url: str, driver: WebDriver):
        logger.info("→ before_navigate_to: %s", url)

    def after_navigate_to(self, url: str, driver: WebDriver):
        logger.info("← after_navigate_to: %s (title=%r)",
                    driver.current_url, driver.title)

    def before_find(self, by, value, driver: WebDriver):
        logger.debug("→ before_find: %s=%s", by, value)

    def after_find(self, by, value, driver: WebDriver):
        logger.debug("← after_find: %s=%s", by, value)

    def before_click(self, element: WebElement, driver: WebDriver):
        snippet = element.get_attribute("outerHTML")[:100].replace("\n", "")
        logger.info("→ before_click on %s…", snippet)

    def before_execute_script(self, script: str, driver: WebDriver):
        logger.debug("→ before_execute_script: %s",
                     script[:100].replace("\n", " "))

    def after_execute_script(self, script: str, driver: WebDriver):
        logger.debug("← after_execute_script")

    def before_switch_to_frame(self, frame, driver: WebDriver):
        logger.info("→ before_switch_to_frame: %r", frame)

    def after_switch_to_frame(self, frame, driver: WebDriver):
        logger.info("← after_switch_to_frame: %r", frame)

    def before_alert_accept(self, driver: WebDriver):
        try:
            text = driver.switch_to.alert.text
        except Exception:
            text = "<no alert text>"
        logger.info("→ before_alert_accept: %s", text)

    def after_alert_accept(self, driver: WebDriver):
        logger.info("← after_alert_accept")

    def on_exception(self, exception, driver: WebDriver):
        """
        Log real WebDriver exceptions, but ignore benign attribute-lookup noise
        """
        msg = clean_error_partition(exception)
        low = msg.lower()

        # Ignore benign attribute-lookup noise, regardless of exception type
        if ("attribute 'shape'" in low) or ("attribute '__len__'" in low):
            logger.debug("↩︎ Ignoring benign attribute-lookup error: %s", msg)
            return

        # Downgrade common, expected Selenium exceptions to WARNING
        expected_types = (NoSuchElementException, StaleElementReferenceException, TimeoutException)
        expected_needles = ("no such element", "stale element reference", "timeout")
        is_expected = isinstance(exception, expected_types) or any(n in low for n in expected_needles)

        try:
            current = driver.current_url
        except WebDriverException:
            current = "<couldn't fetch URL>"

        if is_expected:
            logger.warning("⚠ WebDriver expected exception: `%s` at `%s`", msg, current)
        else:
            logger.error("‼ WebDriver exception: `%s` at `%s`", msg, current)
