import selenium.common.exceptions as se
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from typing import Any, Callable, Tuple, Union
from amzsc.utils import CustomTypes


CONDITION_TYPE = Callable[
    [Tuple[str, str]], Callable[[WebDriver], Union[WebElement, bool]]
]


class ChromeManipulator:
    def __init__(self, driver: CustomTypes.DRIVER_TYPE) -> None:
        self.driver = driver

    def __str__(self) -> str:
        return "DriverManipulator"

    def get(self, url: str) -> None:
        self.driver.get(url)

    def refresh(self) -> None:
        self.driver.refresh()

    def quit(self) -> None:
        self.driver.quit()

    def wait(self, timeout: int = 10) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout)
