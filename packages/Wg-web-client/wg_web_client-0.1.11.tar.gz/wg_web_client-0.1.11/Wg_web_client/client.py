import asyncio
import logging
import re

from aiohttp import ClientSession
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Wg_web_client.exceptions import WGAutomationError
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class WireGuardWebClient:
    def __init__(self, ip: str, chromedriver_path: str = None):
        self.ip = ip
        self.chromedriver_path = chromedriver_path

    async def _setup(self):
        try:
            from .driver_factory import create_driver
            loop = asyncio.get_running_loop()
            self.driver = await loop.run_in_executor(None, create_driver, self.chromedriver_path)
            self.wait = WebDriverWait(self.driver, 3)
        except Exception as e:
            logger.error(f"Error in _setup: {str(e)}")
            raise

    async def create_key(self, key_name: str) -> str:
        await self._setup()
        try:
            logger.info(f"Создание ключа: {key_name}")
            self.driver.get(f"http://{self.ip}")

            # Нажимаем кнопку "New"
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'New')]]"))).click()
            await asyncio.sleep(1)

            # Вводим имя ключа
            name_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Name']")))
            name_input.send_keys(key_name)
            await asyncio.sleep(1)

            # Нажимаем "Create"
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Create')]"))).click()
            await asyncio.sleep(3)  # Даём время интерфейсу создать ключ

            # Получаем список блоков клиентов
            client_blocks = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'relative overflow-hidden')]"))
            )

            target_block = None
            for block in reversed(client_blocks):
                try:
                    block.find_element(By.XPATH, f".//span[normalize-space(text())='{key_name}']")
                    target_block = block
                    break
                except NoSuchElementException:
                    continue

            if not target_block:
                logger.error(f"❌ Не найден блок с ключом: {key_name}")
                raise WGAutomationError(f"Не найден блок с именем ключа '{key_name}'")

            await asyncio.sleep(2)  # Ждём появления ссылки на скачивание

            download_link = target_block.find_element(
                By.XPATH, ".//a[contains(@href, '/api/wireguard/client/') and contains(@href, '/configuration')]"
            )
            download_url = download_link.get_attribute("href")
            full_download_url = f"http://{self.ip}{download_url.lstrip('.')}" if not download_url.startswith(
                "http") else download_url

            logger.info(f"✅ Ключ '{key_name}' успешно создан. Ссылка: {full_download_url}")
            return full_download_url
        except Exception as e:
            logger.error(f"Ошибка при создании ключа '{key_name}': {str(e)}")
            raise
        finally:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Ошибка закрытия драйвера: {str(e)}")

    async def delete_key(self, key_name: str) -> None:
        await self._setup()
        try:
            logger.info(f"Удаление ключа: {key_name}")
            self.driver.get(f"http://{self.ip}")

            client_blocks = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[contains(@class,'relative overflow-hidden')]")
                )
            )

            target_block = None
            for block in reversed(client_blocks):
                try:
                    block.find_element(By.XPATH, f".//span[normalize-space(text())='{key_name}']")
                    target_block = block
                    break
                except NoSuchElementException:
                    continue

            if not target_block:
                logger.error(f"Ключ не найден для удаления: {key_name}")
                raise WGAutomationError(f"Не найден ключ для удаления: '{key_name}'")

            try:
                delete_button = target_block.find_element(By.XPATH, ".//button[@title='Delete Client']")
                delete_button.click()
                await asyncio.sleep(1)

                confirm_button = self.wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH, "//button[contains(text(),'Delete Client') and contains(@class,'bg-red-600')]"
                    ))
                )
                confirm_button.click()
            except (NoSuchElementException, ElementClickInterceptedException) as e:
                logger.warning(f"Не удалось нажать кнопку удаления: {e}")
                raise WGAutomationError("Удаление не удалось из-за проблем с элементами интерфейса.")

            logger.info(f"Ключ успешно удалён: {key_name}")

        except (WGAutomationError, RuntimeError) as e:
            logger.error(f"Ошибка удаления ключа '{key_name}': {str(e)}")
            raise
        finally:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Ошибка закрытия драйвера: {str(e)}")

    async def get_key_status(self, key_name: str) -> bool:
        url = f"http://{self.ip}/api/wireguard/client"
        try:
            logger.info(f"Проверка статуса ключа: {key_name}")
            async with ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        logger.error(f"Ошибка запроса API {url}: Статус {resp.status}")
                        raise Exception(f"Ошибка запроса: {resp.status}")
                    data = await resp.json()

            for client in data:
                if client["name"] == key_name:
                    logger.info(f"Статус ключа '{key_name}': {'включен' if client['enabled'] else 'выключен'}")
                    return client["enabled"]

            logger.error(f"Клиент '{key_name}' не найден на сервере")
            raise Exception(f"Клиент '{key_name}' не найден на сервере.")
        except Exception as e:
            logger.error(f"Ошибка получения статуса для ключа '{key_name}': {str(e)}")
            raise

    import re
    from selenium.common.exceptions import NoSuchElementException

    async def check_activity_key(self, key_name: str) -> bool:
        """
        True, если у клиента есть не нулевой суммарный трафик (по правой колонке).
        """
        await self._setup()
        try:
            logger.info(f"Проверка активности ключа: {key_name}")
            self.driver.get(f"http://{self.ip}")
            await asyncio.sleep(1)

            client_blocks = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[contains(@class,'relative overflow-hidden')]")
                )
            )

            for block in client_blocks:
                try:
                    # Находим нужную карточку по имени
                    block.find_element(By.XPATH, f".//span[normalize-space(text())='{key_name}']")

                    # 1) Надёжный способ: по title "Общий объём ..."
                    stats_titles = block.find_elements(
                        By.XPATH,
                        ".//div[contains(@class,'justify-end')]//span[starts-with(@title,'Общий объём')]"
                    )

                    for st in stats_titles:
                        title_txt = (st.get_attribute("title") or "").lower()
                        # Ищем число с единицами (Б, КБ/МБ/ГБ и т.д.)
                        m = re.search(r'([\d\.,]+)\s*(б|кб|мб|гб|kb|mb|gb)', title_txt, re.IGNORECASE)
                        if m:
                            val = float(m.group(1).replace(',', '.'))
                            if val > 0:
                                logger.info(
                                    f"Ключ '{key_name}' имеет суммарный трафик {m.group(1)} {m.group(2)} — активен")
                                return True

                    # 2) Фолбэк: нижняя строка с суммой в правых мини-блоках
                    totals = block.find_elements(
                        By.XPATH,
                        ".//div[contains(@class,'justify-end')]//div[contains(@class,'min-w-20') or contains(@class,'md:min-w-24')]"
                        "//span[contains(@class,'font-regular')]"
                    )
                    for el in totals:
                        t = el.text.strip()
                        if any(u in t for u in ('КБ', 'МБ', 'ГБ', 'KB', 'MB', 'GB')) and not t.startswith('0'):
                            logger.info(f"Ключ '{key_name}' имеет суммарный трафик {t} — активен")
                            return True

                    logger.info(f"Ключ '{key_name}' без суммарного трафика — не активен")
                    return False

                except NoSuchElementException:
                    continue

            logger.warning(f"Ключ '{key_name}' не найден на странице")
            return False

        except Exception as e:
            logger.error(f"Ошибка при проверке активности ключа '{key_name}': {e}")
            return False
        finally:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Ошибка закрытия драйвера: {e}")

    async def enable_key(self, key_name: str) -> None:
        await self._setup()
        try:
            logger.info(f"Включение ключа: {key_name}")
            self.driver.get(f"http://{self.ip}")
            await asyncio.sleep(1)

            blocks = self.driver.find_elements(By.XPATH, "//div[contains(@class,'border-b')]")
            for block in blocks:
                try:
                    block.find_element(By.XPATH, f".//span[normalize-space(text())='{key_name}']")
                    try:
                        toggle = block.find_element(By.XPATH, ".//div[@title='Enable Client']")
                        toggle.click()
                        logger.info(f"✅ Ключ '{key_name}' включён")
                    except (NoSuchElementException, ElementClickInterceptedException):
                        logger.warning(f"⚠️ Ключ '{key_name}' уже включён или не кликабелен")
                    return
                except NoSuchElementException:
                    continue
            logger.error(f"Ключ '{key_name}' не найден для включения")
        except (OSError, RuntimeError) as e:
            logger.error(f"Ошибка включения ключа '{key_name}': {str(e)}")
            raise
        finally:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Ошибка закрытия драйвера: {str(e)}")

    async def disable_key(self, key_name: str) -> None:
        await self._setup()
        try:
            logger.info(f"Отключение ключа: {key_name}")
            self.driver.get(f"http://{self.ip}")
            await asyncio.sleep(1)

            blocks = self.driver.find_elements(By.XPATH, "//div[contains(@class,'border-b')]")
            for block in blocks:
                try:
                    block.find_element(By.XPATH, f".//span[normalize-space(text())='{key_name}']")
                    try:
                        toggle = block.find_element(By.XPATH, ".//div[@title='Disable Client']")
                        toggle.click()
                        logger.info(f"⛔ Ключ '{key_name}' отключён")
                    except (NoSuchElementException, ElementClickInterceptedException):
                        logger.warning(f"⚠️ Ключ '{key_name}' уже отключён или не кликабелен")
                    return
                except NoSuchElementException:
                    continue
            logger.error(f"Ключ '{key_name}' не найден для отключения")
        except (OSError, RuntimeError) as e:
            logger.error(f"Ошибка отключения ключа '{key_name}': {str(e)}")
            raise
        finally:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Ошибка закрытия драйвера: {str(e)}")
