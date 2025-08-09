import logging
import pandas as pd

from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
from pathlib import Path
from typing import Dict, List, Literal, Optional

from amzsc.modules.chrome_driver import AmazonDriver, ChromeDriverConfig
from amzsc.modules.proxy import get_proxy
from amzsc.utils import Constants
from amzsc.utils.file_worker import write_to_json
from amzsc.utils.marketplace import get_zone


logger = logging.getLogger(__name__)


def scrape_one(client: AmazonDriver, marketplace: str, asin: str) -> Dict[str, str]:
    data = {"asin": asin, "marketplace": marketplace}
    zone = get_zone(marketplace)
    url = f"https://www.amazon.{zone}/dp/{asin}"
    client.get(url)

    product_overview = client.get_product_overview()
    if product_overview:
        data = data | product_overview

    product_specs = client.get_product_specs()
    if product_specs:
        data = data | product_specs

    product_micro = client.get_product_micro()
    if product_micro:
        data = data | product_micro

    return data


def scrape_all(
    marketplaces: List[str],
    asins: List[str],
    thread_id: int,
    thread_count: int = 10,
    proxy_key: Optional[str] = None,
    headless: bool = True,
    is_remote: bool = False,
    remote_url: Optional[str] = None,
    jsonl_output_path: Optional[Path] = None,
) -> List[Dict[str, str]]:
    client = None
    data: List[Dict[str, str]] = []
    try:
        proxy = get_proxy(proxy_key) if proxy_key else None
        position = ChromeDriverConfig.get_driver_position(thread_id, thread_count)
        options = ChromeDriverConfig.get_options(
            proxy=proxy,
            position=position,
            user_agent=UserAgent().random,
            headless=headless,
        )
        if is_remote:
            driver = ChromeDriverConfig.get_remote_driver(options, remote_url)
        else:
            driver = ChromeDriverConfig.get_chrome_driver(options)
        client = AmazonDriver(driver)
        for i in range(len(asins)):
            asin = asins[i]
            marketplace = marketplaces[i]
            row = scrape_one(client, marketplace, asin)
            logger.info("Thread %d: ASIN %s from %s", thread_id, asin, marketplace)
            if jsonl_output_path:
                write_to_json(jsonl_output_path, row)
                logger.debug("Thread %d: ASIN %s to JSONL file", thread_id, asin)
            data.append(row)
    except Exception as e:
        logger.error(str(e))
    finally:
        if client is not None:
            client.quit()
        return data


class AmazonScraper:

    def __init__(
        self,
        proxy_key: Optional[str] = None,
        headless: bool = True,
        is_remote: bool = False,
        remote_url: Optional[str] = None,
        batch_size: int = 10,
        thread_count: int = 10,
        jsonl_output_path: Optional[Path] = None,
        logging_level: str = "DEBUG",
    ) -> None:
        """
        Initialize the AmazonScraper.

        Args:
            proxy_key: If parsed, use proxy to prevent Amazon from block the host computer.
                WWProxy API key. Defaults to None.
            headless: If set to `True`, run the Selenium instances in headless mode.
                Defaults to True.
            is_remote: If set to `True`, use Selenium Grid for the instances.
                Defaults to False.
            remote_url: Selenium Grid remote URL. Required `is_remote` = True to activate.
                Defaults to None.
            batch_size: The number of URLs to be processed in one instance before quiting it.
                Defaults to 10.
            thread_count: The number of threads to use in the process. Defaults to 10.
            jsonl_output_path: If parsed, append results in JSONL type in the parsed path.
                Defaults to None.
            logging_level: Logging level. Defaults to "DEBUG".

        Raises:
            ValueError: If `thread_count` is not a positive integer.
            TypeError: If `logging_level` is not one of the predefined levels.
        """
        self.__proxy_key = proxy_key
        self.headless = headless
        self.is_remote = is_remote
        self.remote_url = remote_url
        self.batch_size = batch_size
        self.thread_count = thread_count
        if self.thread_count <= 0:
            raise ValueError("thread_count must be a positive integer")

        # Set up output options
        self.jsonl_output_path = jsonl_output_path

        # Configure logging
        levels = Constants.LOGGING_LEVELS
        if logging_level not in levels:
            raise TypeError("logging_level must be one of: " + ", ".join(levels))
        logger.setLevel(logging_level)
        logger.debug(
            "Initializing AmazonScraper with thread_count=%d, batch_size=%d"
            % (self.thread_count, self.batch_size),
        )

    @property
    def proxy_key(self) -> Optional[str]:
        return self.__proxy_key

    def scrape(
        self,
        asins: List[str],
        marketplaces: Optional[List[str]] = None,
        marketplace: Optional[Literal["US", "UK", "DE", "FR", "ES", "IT"]] = None,
    ) -> pd.DataFrame:
        """
        Scrape product data from Amazon for a list of ASINs.

        Args:
            asins: An array of ASINs to scrape.
            marketplaces: Corresponding array of marketplaces to ASINs. Defaults to None.
                Has to be the same length as `asins`.
            marketplace: Marketplace for all ASINs. Defaults to None.
                If `marketplaces` is not set, `marketplace` must be set.
                If `marketplace` is set, it will be used for all ASINs.

        Raises:
            ValueError: asins must not be an empty list.
            ValueError: marketplaces must be the same length as asins.

        Returns:
            A pandas DataFrame containing the scraped data.
        """
        if len(asins) == 0:
            raise ValueError("asins must not be an empty list")
        if marketplace is not None and marketplaces is None:
            marketplaces = [marketplace] * len(asins)
        if marketplaces is None or len(marketplaces) != len(asins):
            raise ValueError("Invalid marketplaces array length")

        chunks = [
            (marketplaces[i : i + self.batch_size], asins[i : i + self.batch_size])
            for i in range(0, len(asins), self.batch_size)
        ]
        args = [
            self.thread_count,
            self.proxy_key,
            self.headless,
            self.is_remote,
            self.remote_url,
            self.jsonl_output_path,
        ]
        with ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            futures = [
                executor.submit(
                    scrape_all, chunk[0], chunk[1], i + 1 % self.thread_count, *args
                )
                for i, chunk in enumerate(chunks)
            ]
            results = []
            for future in futures:
                results.extend(future.result())
            df_output = pd.DataFrame(results)
        return df_output
