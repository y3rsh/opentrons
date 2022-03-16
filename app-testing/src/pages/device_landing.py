"""Model for the App page that displays info and settings for the app."""
from rich.console import Console
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.driver.highlight import highlight
from src.driver.base import Base, Element

class DeviceLanding:
    """Elements and actions for the Page that loads when the app is opened."""

    def __init__(self, driver: WebDriver, console: Console, execution_id: str) -> None:
        """Initialize with driver."""
        self.base: Base = Base(driver, console, execution_id)

    header: Element = Element((By.ID, "DevicesLanding_title"), "Header that is 'Devices'")
    header: Element = Element((By.ID, "RobotStatusBanner_robotModel"), "Header that is 'Devices'")