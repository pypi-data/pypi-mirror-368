# WireGuard Web Client

WireGuard Web Client — это Python-библиотека для управления ключами WireGuard через веб-интерфейс с использованием Selenium. Подходит для Linux и Windows.

## Возможности:
-  Создание ключа
-  Удаление ключа
-  Проверка статуса ключа
-  Управление статусом (Enable / Disable)
-  Получение ссылки для скачивания
-  Проверка статуса активности
 
## Пример использования:

```python
import asyncio
from Wg_web_client.client import WireGuardWebClient


async def main():
    client = WireGuardWebClient("45.8.98.193:51821", "/path/to/chromedriver")

    link = await client.create_key("ZurlexVPN")
    print(link)
    await client.delete_key("ZurlexVPN")
    status_active = await client.check_activity_key("ZurlexVPN")
    print(status_active)
    status = await client.get_key_status("ZurlexVPN")
    print(status)  # True или False

    await client.disable_key("ZurlexVPN")
    await client.enable_key("ZurlexVPN")


if __name__ == "__main__":
    asyncio.run(main())
```

## Установка зависимостей:

```bash
pip install selenium webdriver-manager
```

## Установка из исходников:

```bash
git clone https://github.com/Zurlex/Wg_web_client.git
cd Wg_web_client
pip install -e .
```
## Установка pip:
```bash
pip install Wg_web_client
```