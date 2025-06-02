import asyncio

from app.parser.main import Parser


async def main():
    parser = Parser()
    url = "https://downloader.disk.yandex.ru/preview/aa4d906f50724e3c372ed50f6b3b362850a26bbd16e18442e5a5686005b8022d/683d9f41/TNHVeRgibI90AlqtnIefqAuSIq2TjNb65zb2WdH8S5oKYVpbhwxOHnDjKxzJzFJ8usTWMTb-5OmwLjQQ5QgxlA%3D%3D?uid=0&filename=photo_2025-06-02_12-44-28.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=2048x2048"
    await parser.check(url)


if __name__ == "__main__":
    asyncio.run(main())
