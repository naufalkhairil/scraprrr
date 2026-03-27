"""
Selenium WebDriver management for Traveloka scraping.

This module handles the creation and configuration of Chrome WebDriver instances,
including anti-detection measures and connection to remote Selenium servers.
"""

import logging
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


def create_driver(remote_url: str = "http://localhost:4444/wd/hub") -> WebDriver:
    """
    Create a Selenium WebDriver connected to the Docker Selenium server.

    Configures Chrome with anti-detection measures to avoid bot detection.

    Args:
        remote_url: URL of the Selenium Grid server. Defaults to local Docker container.

    Returns:
        Configured WebDriver instance.
    """
    logger.info("Creating Selenium WebDriver instance...")
    logger.debug(f"Connecting to remote URL: {remote_url}")

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1366,768")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    logger.debug("Chrome options configured")

    driver = webdriver.Remote(
        command_executor=remote_url,
        options=chrome_options,
    )

    # Execute CDP commands to hide automation
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """,
        },
    )

    logger.info("Selenium WebDriver created successfully")
    return driver


def quit_driver(driver: WebDriver) -> None:
    """
    Safely quit a WebDriver instance.

    Args:
        driver: The WebDriver instance to quit.
    """
    if driver:
        logger.info("Closing WebDriver session...")
        driver.quit()
        logger.info("WebDriver session closed")
