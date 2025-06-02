import asyncio
import glob
import logging
import os
import shutil
import tempfile
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core import settings

logger = logging.getLogger(__name__)


class ParseJSON:
    def __init__(self, download_dir):
        self.download_dir = download_dir

    def wait_for_file(self, timeout: int = 15):
        """Ждём появления файла *.json в папке download_dir."""
        end_time = time.time() + timeout
        while time.time() < end_time:
            files = glob.glob(os.path.join(self.download_dir, "*.json"))
            if files:
                return files[0]
            time.sleep(0.5)
        raise TimeoutError("JSON файл не был скачан за время ожидания.")

    def parse_json(self):
        # Ждем скачивания файла
        json_file_path = self.wait_for_file(timeout=20)
        logger.debug(f"Файл скачан: {json_file_path}")

        # Читаем содержимое файла
        with open(json_file_path, "r", encoding="utf-8") as f:
            json_content = f.read()
        logger.info(json_content)
        return json_content


class Parser:
    def __init__(self):
        self.driver = None
        self.download_dir = None

    async def check(self, url: str):
        self.download_dir = tempfile.mkdtemp()
        if self.driver is None:
            self._driver_run()
        if not self.driver:
            logger.error("Driver not initialized. Skipping check.")
            return
        logger.info(f"Start checking {url}")
        try:
            await self.__get(url)
            return ParseJSON(self.download_dir).parse_json()
        finally:
            if self.driver is not None:
                self.driver.quit()
            # Удаляем временную папку с файлами
            shutil.rmtree(self.download_dir, ignore_errors=True)

    def _driver_run(self):
        try:
            options = uc.ChromeOptions()
            # Создаём временную папку для скачивания
            prefs = {
                "download.default_directory": self.download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            }
            options.add_experimental_option("prefs", prefs)

            options.binary_location = "/usr/bin/chromium"
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            self.driver = uc.Chrome(options=options)
            self.driver.implicitly_wait(5)
            self.driver.set_page_load_timeout(120)
        except Exception as ex:
            logger.exception("Error in run driver")
            self.driver = None
            raise

    async def __get(self, url: str):
        self.driver.get(settings.parser.main_url)
        await asyncio.sleep(1)
        photo_tab = self.driver.find_element(
            By.CSS_SELECTOR, 'a[href="#b-checkform_tab-qrfile"]'
        )
        photo_tab.click()
        await asyncio.sleep(1)
        # Вводим ссылку в input
        logger.debug("Вводим ссылку в input")
        input_field = self.driver.find_element(By.ID, "b-checkform_qrurl")
        input_field.clear()
        input_field.send_keys(url)
        await asyncio.sleep(1)
        # Нажимаем кнопку "Проверить"
        logger.debug("Нажимаем кнопку " "Проверить" "")
        container = self.driver.find_element(By.ID, "b-checkform_tab-qrfile")
        submit_button = container.find_element(
            By.CSS_SELECTOR, "button.b-checkform_btn-send"
        )
        submit_button.click()
        await asyncio.sleep(2)
        submit_button.click()
        await asyncio.sleep(2)
        wait = WebDriverWait(self.driver, 20)
        # Кликаем по кнопке "Сохранить в"
        save_dropdown_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div.b-check_btn-save button.dropdown-toggle")
            )
        )
        save_dropdown_btn.click()
        await asyncio.sleep(1)
        # Кликаем по пункту "JSON"
        json_option = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.b-check_btn-json"))
        )
        json_option.click()
        await asyncio.sleep(5)
