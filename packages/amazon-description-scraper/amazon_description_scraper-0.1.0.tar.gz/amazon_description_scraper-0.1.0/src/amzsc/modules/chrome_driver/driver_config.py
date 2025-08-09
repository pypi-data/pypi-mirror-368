from selenium.webdriver import ChromeOptions, Chrome, Remote
from typing import Optional
from amzsc.utils import Constants


class ChromeDriverConfig:

    @staticmethod
    def get_options(**kwargs) -> ChromeOptions:
        options = ChromeOptions()
        if kwargs.get("user_agent") is not None:
            options.add_argument(f"user-agent={kwargs.get('user_agent')}")
        if kwargs.get("proxy") is not None:
            options.add_argument(f"--proxy-server={kwargs.get('proxy')}")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-dev-shm-usage")
        if kwargs.get("headless", True):
            options.add_argument("--headless")
        options.add_argument("--log-level=3")
        options.add_argument("--mute-audio")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-features=Translate")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--autoplay-policy-no-user-gesture-required")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--force-dark-mode")
        options.add_argument("--force-show-cursor")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--force-device-scale-factor=0.8")
        if kwargs.get("position") is not None:
            options.add_argument(f"--window-position={kwargs.get('position')}")
        if kwargs.get("download_dir") is not None:
            prefs = {
                "download.default_directory": kwargs.get("download_dir"),
                "download.prompt_for_download": False,
                "directory_upgrade": True,
                "safebrowsing.enabled": True,
            }
            options.add_experimental_option("prefs", prefs)
        return options

    @staticmethod
    def get_chrome_driver(options: ChromeOptions) -> Chrome:
        driver = Chrome(options=options)
        return driver

    @staticmethod
    def get_remote_driver(
        options: ChromeOptions, remote_url: Optional[str] = None
    ) -> Remote:
        if remote_url is None:
            remote_url = "http://selenium-hub:4444/wd/hub"
        driver = Remote(options=options, command_executor=remote_url)
        return driver

    @staticmethod
    def get_driver_position(thread_id: int, thread_count: int = 10) -> str:
        min_row = 4
        min_col = 4
        tmp = int(thread_count**0.5)
        row_count = max(min_row, tmp)
        col_count = max(min_col, tmp + 1)
        row_height = Constants.MONITOR_HEIGHT // row_count
        col_width = Constants.MONITOR_WIDTH // col_count
        col = thread_id % col_count
        row = thread_id // col_count
        return f"{col_width * col},{row_height * row}"
