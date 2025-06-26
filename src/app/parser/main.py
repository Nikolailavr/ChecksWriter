import glob
import json
import logging
import os
import shutil
import tempfile
import time
from pathlib import Path

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.parser.exceptions import BadQRCodeError
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
            json_content = json.load(f)
        logger.info(json_content)
        return json_content


class Parser:
    def __init__(self):
        self.driver = None
        self.download_dir = None

    def check(self, filename: str):
        self.download_dir = tempfile.mkdtemp()
        if self.driver is None:
            self._driver_run()
        if not self.driver:
            logger.error("Driver not initialized. Skipping check.")
            return
        if Path(settings.uploader.DIR / filename).exists():
            logger.info(f"Файл {filename} найден")
        else:
            logger.error(f"Файл {filename} не найден")
            raise FileExistsError(f"Файл {filename} не найден")
        logger.info(f"Start checking file={filename}")
        try:
            self._get_by_photo(filename)
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
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            self._driver = uc.Chrome(
                options=options,
                driver_executable_path=settings.parser.driver_path,
                use_subprocess=True,
                version_main=None,  # отключает автоопределение версии
            )
            self.driver.implicitly_wait(5)
            self.driver.set_page_load_timeout(120)
        except Exception as ex:
            logger.exception("Error in run driver")
            self.driver = None
            raise ex

    def _get_by_photo(self, filename: str = "image.jpg"):
        try:
            self.driver.get(settings.parser.main_url)

            # Ожидаем и кликаем вкладку "Фото"
            logger.info('Ожидаем и кликаем вкладку "Фото"')
            photo_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'a[href="#b-checkform_tab-qrfile"]')
                )
            )
            photo_tab.click()
            time.sleep(2)

            # Находим элемент input типа file
            logger.info("Находим элемент input типа file")
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input.b-checkform_qrfile[type='file']")
                )
            )
            # Отправляем путь к файлу напрямую в input
            logger.info("Отправляем путь к файлу напрямую в input")
            logger.info(f"Путь файла: {settings.uploader.DIR / filename}")
            file_input.send_keys(os.path.abspath(settings.uploader.DIR / filename))

            # Дожидаемся обработки
            logger.info("Дожидаемся обработки")
            time.sleep(2)

            # Скроллим до середины страницы
            logger.info("Скроллим до конца страницы")
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(2)

            logger.info("Ждем появления кнопки загрузки")
            save_dropdown = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "div.b-check_btn-save button.dropdown-toggle",
                    )
                )
            )
            save_dropdown.click()
            time.sleep(1)

            # Сохраняем в JSON
            logger.info("Сохраняем в JSON")
            json_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.b-check_btn-json"))
            )
            self.driver.execute_script("arguments[0].click();", json_button)
            time.sleep(2)

        except Exception as ex:
            logger.error(f"Ошибка при обработке чека: {str(ex)}")
            raise BadQRCodeError
