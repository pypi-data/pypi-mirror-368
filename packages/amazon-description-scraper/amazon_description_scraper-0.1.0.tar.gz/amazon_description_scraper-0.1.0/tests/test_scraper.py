import pandas as pd
from amzsc import AmazonScraper


def test_amazon_scraper() -> None:
    """Test the AmazonScraper class."""
    proxy_key = "demo_proxy_key"
    scraper = AmazonScraper(
        proxy_key=proxy_key,
        jsonl_output_path="data/pytest_output.jsonl",
        headless=True,
        logging_level="DEBUG",
    )
    assert scraper is not None, "AmazonScraper instance should not be None"
    assert scraper.headless is True, "Headless mode should be enabled"
    assert scraper.proxy_key == proxy_key, "Proxy should be set correctly"
    assert scraper.jsonl_output_path, "JSONL output path should be set"

    results = scraper.scrape(asins=["B07WC4TDJJ"], marketplace="US")
    assert isinstance(results, pd.DataFrame), "Search results should be a list"


# def test_amazon_scraper_with_proxy() -> None:
#     """Test the AmazonScraper class with a proxy."""
#     proxy_key = "demo_proxy_key"
#     scraper = AmazonScraper(proxy_key=proxy_key)
#     assert scraper is not None, "AmazonScraper instance should not be None"
#     assert scraper.proxy_key == proxy_key, "Proxy should be set correctly"


# def test_amazon_scraper_with_jsonl_output() -> None:
#     """Test the AmazonScraper class with JSONL output."""
#     scraper = AmazonScraper(jsonl_output_path="data/pytest_output.jsonl")
#     assert scraper is not None, "AmazonScraper instance should not be None"
#     assert scraper.jsonl_output_path, "Headless mode should be enabled"

#     results = scraper.scrape(asins=["B07WC4TDJJ"], marketplace="US")
#     assert isinstance(results, pd.DataFrame), "Search results should be a list"
#     assert len(results) > 0, "Search results should not be empty"
