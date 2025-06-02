import asyncio
import logging

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)


class Parser:
    def __init__(self):
        self.driver = None

    async def start_checking(self) -> None:
        """Запуск проверки всех ссылок"""
        try:
            self._driver_run()

            self.driver.quit()
        except Exception as ex:
            logger.error(ex)

    async def check(self, url: str):
        need_quit = False
        if self.driver is None:
            self._driver_run()
            need_quit = True
        logger.info(f"Start checking {url}")

        if need_quit:
            self.driver.quit()

    def _driver_run(self):
        try:
            self.driver = uc.Chrome(
                browser_executable_path="/usr/bin/chromium",
            )
            self.driver.implicitly_wait(5)
            self.driver.set_page_load_timeout(120)
        except Exception as ex:
            logger.error("Error in run driver")

    async def _get_url_data(self, url: str) -> None:
        try:
            self.driver.get(url)
            await asyncio.sleep(60)
            price_element = self.driver.find_element(
                By.ID, value="state-webPrice-3121879-default-1"
            )
            attr = price_element.get_attribute("data-state")
            logger.info(f"{attr=}")
        except Exception as ex:
            logger.error(f"Error get data from url ({url}): {ex}")
            return None


async def main():
    parser = Parser()
    await parser.check("https://proverkacheka.com/")


if __name__ == "__main__":
    asyncio.run(main())
