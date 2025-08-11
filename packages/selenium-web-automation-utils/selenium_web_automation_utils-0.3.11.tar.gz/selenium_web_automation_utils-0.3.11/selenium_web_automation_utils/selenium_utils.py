# selenium_web_automation_utils/selenium_utils.py
import os
import time
import random
from contextlib import contextmanager, redirect_stderr
from pathlib import Path
from typing import Optional, List, Iterator

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver
from selenium.webdriver.support.wait import WebDriverWait

from selenium_web_automation_utils.logging_utils import logger

# compatibility shim (must come before uc import)
from .compatibility import *
import undetected_chromedriver as uc

from .logging_listener import LoggingListener, clean_error_partition

# A small pool of common desktop UAs—feel free to expand this list
USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.170 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
]


@contextmanager
def stderr_to_null():
    """Temporarily suppress stderr output."""
    with open(os.devnull, 'w') as devnull:
        with redirect_stderr(devnull):
            yield


@contextmanager
def get_webdriver(
        *,
        implicitly_wait_seconds: int = 5,
        user_agent: Optional[str] = None,
        proxy: Optional[str] = None,
        user_profile_path: Optional[str] = None,
        disable_webdriver_detection: bool = True,
        suppress_stderr: bool = True,
        download_dir: Optional[str] = None,
        chrome_extensions: Optional[List[str]] = None,
        use_guest_profile: bool = False,
        mobile_emulation: bool = False,
        use_undetected: bool = False,
        headless: bool = False,
) -> Iterator[WebDriver]:
    """
    Yields a configured Chrome WebDriver (selenium or undetected-chromedriver),
    then ensure it is cleanly quit on exit.

    This context manager supports both standard Selenium Chrome and
    undetected-chromedriver for bypassing basic bot-detection. It also
    lets you customize user-agent, proxy, download folder, extensions,
    headless mode, mobile emulation, and profile reuse.

    Parameters
    ----------
    implicitly_wait_seconds : int, default=5
        How many seconds to implicitly wait when locating elements.
    user_agent : str or None, default=None
        Custom User-Agent string to present. If None, a random UA is chosen. (Google for 'What is my user agent')
    proxy : str or None, default=None
        Proxy server URL (e.g. "http://user:pass@host:port") to route all requests.
    user_profile_path : str or None, default=None
        Path to an existing Chrome user profile for session persistence. (see: chrome://version/)
    disable_webdriver_detection : bool, default=True
        Whether to hide the WebDriver `navigator.webdriver` flag.
    suppress_stderr : bool, default=True
        Redirect ChromeDriver’s stderr output to /dev/null.
    download_dir : str or None, default=None
        Filesystem path for automatic downloads (sets Chrome prefs).
    chrome_extensions : list of str or None, default=None
        File paths to any `.crx` extensions to load on startup.
    use_guest_profile : bool, default=False
        Launch Chrome in Guest mode instead of loading a user profile.
    mobile_emulation : bool, default=False
        Emulate a mobile viewport and user-agent for mobile testing.
    use_undetected : bool, default=False
        Use `undetected-chromedriver` rather than vanilla Selenium.
    headless : bool, default=False
        Run in headless mode (no visible browser window). Also forced in CI.

    Yields
    ------
    selenium.webdriver.Chrome
        A configured Chrome WebDriver instance ready for navigation.

    Examples
    --------
    >> with get_webdriver(user_agent='CustomUA/1.0', headless=True) as driver:
    ...     driver.get('https://example.com')
    >> # Outside the block, driver.quit() has been called automatically.
    """
    logger.info(
        "Launching %sChrome WebDriver (undetected=%s, headless=%s)",
        "undetected-" if use_undetected else "",
        use_undetected,
        headless
    )

    if use_undetected and uc is None:
        raise ImportError(
            "undetected-chromedriver is not installed. "
            "Run: pip install undetected-chromedriver"
        )

    # pick a random UA if none provided
    ua = user_agent or random.choice(USER_AGENT_LIST)

    # pick the right Options class
    Options = uc.ChromeOptions if use_undetected else webdriver.ChromeOptions
    options = Options()

    # only set excludeSwitches for the normal Selenium path, not undetected-chromedriver
    if not use_undetected:
        options.add_experimental_option(
            "excludeSwitches", ["enable-logging", "enable-automation"]
        )

    options.add_argument(f"--user-agent={ua}")
    options.add_argument("log-level=3")  # Set log level to ERROR to reduce verbosity
    options.add_argument("--silent")  # Suppresses log messages from ChromeDriver

    # set proxy if given
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")

    # set download directory
    if download_dir:
        prefs = {
            "download.default_directory": str(Path(download_dir).resolve()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        options.add_experimental_option("prefs", prefs)

    # add extensions
    if chrome_extensions:
        for ext in chrome_extensions:
            options.add_extension(ext)

    # headless / CI flags
    if os.getenv("CI") or headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    else:
        if use_guest_profile:
            options.add_argument("--guest")
        elif user_profile_path:
            p = Path(user_profile_path)
            options.add_argument(f"--user-data-dir={p.parent}")
            options.add_argument(f"--profile-directory={p.name}")

    if mobile_emulation:
        options.add_experimental_option("mobileEmulation", {
            "deviceMetrics": {"width": 360, "height": 740, "pixelRatio": 4},
            "userAgent": (
                "Mozilla/5.0 (Linux; Android 7.0; SM-G950U; wv) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
                "Chrome/90.0.4430.91 Mobile Safari/537.36"
            )
        })

    if disable_webdriver_detection and not use_undetected:
        options.add_argument("--disable-blink-features=AutomationControlled")

    # instantiate
    if use_undetected:
        # silence UC’s __del__ on Windows, so it doesn't try to quit twice
        uc.Chrome.__del__ = lambda self: None
        driver = uc.Chrome(options=options)
    else:
        if suppress_stderr:
            with stderr_to_null():
                driver = webdriver.Chrome(options=options)
        else:
            driver = webdriver.Chrome(options=options)

    # Log events in webdriver
    driver = EventFiringWebDriver(driver, LoggingListener())

    if disable_webdriver_detection and not use_undetected:
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

    driver.implicitly_wait(implicitly_wait_seconds)

    try:
        yield driver
    finally:
        logger.info("Quitting WebDriver")
        driver.quit()


def find_element_wait(driver,
                      by: str,
                      locator, timeout=10, raise_exception=True):
    """
    Find an element on a web page and wait for it to be clickable.

    Args:
        driver (webdriver.Chrome): The webdriver instance to use.
        by (str): The locator strategy to use (See: selenium.webdriver.common.by)
        locator (str): The locator value to use with the specified strategy.
        timeout (int, optional): The maximum time to wait for the element to be clickable. Defaults to 30.
        raise_exception (bool, optional): Whether to raise an exception if the element is not found. Defaults to True.

    Returns:
        webdriver.WebElement: The found element.

    Raises:
        Exception: If the element is not found and raise_exception is True.
    """
    logger.debug("⌛ waiting up to %ss for element %s=%s", timeout, by, locator)
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )
    except TimeoutException:
        logger.warning("⌛ timeout after %ss waiting for %s=%s", timeout, by, locator)
        if raise_exception:
            raise


def find_element_by_text(driver, tag, text, anywhere_incl_children=True, timeout=10, raise_exception=True):
    """
        Find an element on a web page by text and wait for it to be clickable.

        Args:
            driver (webdriver.Chrome): The webdriver instance to use.
            tag (str): The HTML tag to search for.
            text (str): The text to search for within the element.
            anywhere_incl_children (bool, optional): Search for text anywhere in element or direct node only (if False).
            timeout (int, optional): The maximum time to wait for the element to be clickable. Defaults to 30.
            raise_exception (bool, optional): Whether to raise an exception if element is not found. Defaults to True.

        Returns:
            webdriver.WebElement: The found element.

        Raises:
            Exception: If the element is not found and raise_exception is True.
        """
    if anywhere_incl_children:
        xpath = f"//{tag}[contains(., '{text}')]"
    else:
        xpath = f"//{tag}[contains(text(), '{text}')]"
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element
    except Exception as e:
        if raise_exception:
            raise e


def find_element_until_none(driver, xpath, timeout=10):
    """
    Generator function that yields elements found by the specified XPath expression until no more elements are found.

    Parameters:
    - driver: The WebDriver instance used to perform the search.
    - xpath: The XPath expression used to locate elements.
    - timeout: Maximum time (in secs) to wait for the element to appear before considering it not found (default: 10).

    Yields:
    - WebElement: The found WebElement that matches the XPath expression.

    Exceptions:
    - Prints an error message if an exception occurs during element search.
    - Stops yielding elements when no more elements are found or an exception is raised.

    Example:
    >>> for element in find_element_until_none(driver, "//*[local-name()='svg' and @aria-label='Go back']"):
    >>>     element.click()
    """
    while True:
        try:
            yield find_element_wait(driver, By.XPATH, xpath, timeout=timeout, raise_exception=True)
        except Exception as e:
            logger.warning("No longer able to find element with xpath %r: %s", xpath, e)
            return


def scroll_and_find_element(driver,
                            by: str,
                            locator: str,
                            timeout: float = 120,
                            scroll_pause: float = 1.0,
                            raise_exception: bool = True):
    """
    Scrolls down the page one viewport at a time to locate an element.

    This helper will:
      1. Measure the viewport height once.
      2. Try to find the element with a quick visibility check each loop.
      3. If not found, scroll down by one viewport and pause for lazy-loaded content.
      4. Repeat until the element is visible or the overall timeout elapses.
      5. If the bottom of the page is reached without finding the element,
         it will scroll back to the top before exiting.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        by (str): Locator strategy (e.g. By.ID, By.XPATH).
        locator (str): The locator expression for the target element.
        timeout (float): Total seconds to wait before giving up. Defaults to 120.
        scroll_pause (float): Seconds to sleep after each scroll. Defaults to 1.0.
        raise_exception (bool): If True, raises TimeoutException when not found;
                                if False, returns None on timeout.

    Returns:
        WebElement: The matching element, if found.
        None: If not found within the timeout and raise_exception is False.

    Raises:
        TimeoutException: If the element is not found within the timeout
                          and raise_exception is True.
    """
    end_time = time.time() + timeout
    viewport_height = driver.execute_script("return window.innerHeight")
    logger.debug("Viewport height = %s", viewport_height)
    logger.debug("⌛ will wait up to %.1fs for element %s=%s", timeout, by, locator)

    while time.time() < end_time:
        try:
            el = WebDriverWait(driver, 1).until(
                EC.visibility_of_element_located((by, locator))
            )
            driver.execute_script("window.scrollTo(0, 0);")
            logger.debug("✅ Found %s=%s. Scrolled back to top", by, locator)
            return el

        except TimeoutException:
            driver.execute_script(f"window.scrollBy(0, {viewport_height});")
            time.sleep(scroll_pause)

            # check if we've reached (or passed) the bottom
            current_scroll = driver.execute_script("return window.scrollY")
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            if current_scroll + viewport_height >= scroll_height:
                logger.debug("📄 reached page bottom at scrollY=%s", current_scroll)
                break

    # not found: reset scroll
    driver.execute_script("window.scrollTo(0, 0);")
    logger.debug("🔙 Scrolled back to top after not finding %s=%s", by, locator)

    msg = f"Element not found within {timeout}s: {by}={locator}"
    if raise_exception:
        raise TimeoutException(msg)
    return None


# Helper function to add random delays
def human_delay(min_delay=0.1, max_delay=0.5):
    time.sleep(random.uniform(min_delay, max_delay))


def type_keys(web_element: WebElement, message: str, min_delay: int = 50, max_delay: int = 200):
    """
    Types a message into a web element character by character with a random delay between keystrokes.

    Parameters:
    - web_element: The WebElement where the message will be typed.
    - message: The string message to be typed into the web element.
    - min_delay: Minimum time delay between keystrokes in milliseconds.
    - max_delay: Maximum time delay between keystrokes in milliseconds.

    Returns:
    - None: This function does not return any value.

    Example:
    >> type_keys(web_element, "Hello World")
    """
    for char in message:
        web_element.send_keys(char)
        # Introduce a new random delay between keystrokes
        time.sleep(random.randint(min_delay, max_delay) / 1000)


def scroll_randomly(driver, min_scrolls=1, max_scrolls=5):
    scrolls = random.randint(min_scrolls, max_scrolls)
    for _ in range(scrolls):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")  # Scroll down
        human_delay(1, 3)  # Random delay between scrolls


def move_mouse_randomly(driver: WebDriver) -> None:
    """
    Simulate random mouse movements to mimic human behavior.

    Chooses a random point within the viewport (using window.innerWidth/innerHeight)
    and moves the mouse there relative to the <body> element to avoid out-of-bounds.
    Swallows any errors to prevent noisy tracebacks.
    """
    try:
        # get viewport dimensions
        width = driver.execute_script("return window.innerWidth")
        height = driver.execute_script("return window.innerHeight")

        # pick a random target within the viewport
        target_x = random.randint(0, width - 1)
        target_y = random.randint(0, height - 1)

        # find the <body> element as a stable reference
        body = driver.find_element(By.TAG_NAME, "body")

        # perform the move relative to <body>
        ActionChains(driver) \
            .move_to_element_with_offset(body, target_x, target_y) \
            .perform()

        # small pause after moving
        time.sleep(random.uniform(0.1, 0.5))

    except Exception as e:
        # transient failure is fine—log and continue
        logger.warning("⚠ move_mouse_randomly transient failure: %s", clean_error_partition(e))


def mimic_human(
        driver: WebDriver,
        min_sleep: float = 2.0,
        max_sleep: float = 5.0,
        random_scroll: bool = False,
        random_mouse_move: bool = False,
        quiet: bool = False,
) -> None:
    """
    Pause and optionally scroll/move mouse to mimic a human user.

    Parameters
    ----------
    driver
        The WebDriver instance to use for scrolling / mouse moves.
    min_sleep
        Minimum number of seconds to sleep.
    max_sleep
        Maximum number of seconds to sleep.
    random_scroll
        If True, perform a small random scroll after sleeping.
    random_mouse_move
        If True, perform a small random mouse movement after sleeping.
    quiet
        If True, suppress the printout of what it’s doing.
    """
    sleep_secs = random.uniform(min_sleep, max_sleep)
    if not quiet:
        actions = [f"sleep {sleep_secs:.2f}s"]
        if random_scroll:
            actions.append("scroll")
        if random_mouse_move:
            actions.append("mouse move")
        logger.info("Mimic human: %s", ", ".join(actions))

    time.sleep(sleep_secs)

    if random_scroll:
        try:
            scroll_randomly(driver, min_scrolls=1, max_scrolls=3)
        except Exception as e:
            logger.warning("mimic_human scroll failed: %s", e)

    if random_mouse_move:
        try:
            move_mouse_randomly(driver)
        except Exception as e:
            logger.warning("mimic_human mouse move failed: %s", e)
