from typing import Dict
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

from amzsc.modules.chrome_driver.driver_manipulator import ChromeManipulator
from amzsc.handlers import safe_method
from amzsc.utils import Constants, CustomTypes


class AmazonDriver(ChromeManipulator):

    def __init__(self, driver: CustomTypes.DRIVER_TYPE) -> None:
        super().__init__(driver)

    @safe_method
    def get_product_overview(self) -> Dict[str, str]:
        data = {}
        parent_div = self.driver.find_element(By.ID, Constants.PRODUCT_OVERVIEW)
        child_divs = parent_div.find_elements(By.XPATH, "./div")
        for child_div in child_divs:
            divs = child_div.find_elements(By.TAG_NAME, "div")
            field = divs[0].text.strip()
            value = divs[1].text.strip()
            data[field] = value
        return data

    @safe_method
    def get_product_specs(self) -> Dict[str, str]:
        data = {}
        data_table = self.driver.find_element(By.ID, Constants.PRODUCT_SPECS)
        self.driver.execute_script(Constants.PRODUCT_SPECS_SCRIPT, data_table)
        rows = data_table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            if row.text.strip() == "":
                continue
            field = row.find_element(By.TAG_NAME, "th").text.strip()
            value = row.find_element(By.TAG_NAME, "td").text.strip()
            data[field] = value
        return data

    @safe_method
    def get_product_micro(self) -> Dict[str, str]:
        data = {}
        data_table = self.driver.find_element(By.CSS_SELECTOR, Constants.PRODUCT_MICRO)
        rows = data_table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            field = cells[0].text
            value = cells[1].text
            data[field] = value
        return data
