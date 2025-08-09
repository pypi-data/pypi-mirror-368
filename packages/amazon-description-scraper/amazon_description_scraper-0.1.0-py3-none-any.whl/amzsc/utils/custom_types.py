from selenium.webdriver import Chrome, Remote
from typing import Union


class CustomTypes:
    DRIVER_TYPE = Union[Chrome, Remote]
