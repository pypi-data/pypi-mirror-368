"""Асинхронное чтение прокси из файлов 📁⚡"""

import asyncio
import random
from typing import List, Optional, Union
from pathlib import Path

try:
    import aiofiles
except ImportError:
    aiofiles = None

from .core import ProxyData, ProxyParser, ProxyFormatType


class AsyncProxyFileReader:
    """Асинхронное чтение прокси из файлов 📁⚡"""

    def __init__(self):
        if aiofiles is None:
            raise ImportError("aiofiles required for async operations. Install with: pip install proxy-file-parser[async]")
        self.parser = ProxyParser()
        self.encoding = 'utf-8'

    async def get_proxies(self, file_path: Union[str, Path],
                          format_name: Optional[ProxyFormatType] = None,
                          default_protocol: str = "http") -> List[ProxyData]:
        """
        Асинхронно читает прокси из файла 📖⚡

        Args:
            file_path: путь к файлу
            format_name: формат прокси или None для авто-определения
            default_protocol: протокол по умолчанию
        """
        proxies = []
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Файл {file_path} не найден")

        # 🚀 Асинхронное чтение файла
        async with aiofiles.open(file_path, 'r', encoding=self.encoding) as f:
            line_num = 0
            async for line in f:
                line_num += 1
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                try:
                    proxy = self.parser.parse_line(line, format_name, default_protocol)
                    if proxy:
                        proxies.append(proxy)
                    else:
                        # 🔥 Выводим ошибку с подробностями
                        print(f"❌ Строка {line_num}: '{line}' не соответствует формату '{format_name or 'авто'}'")
                except Exception as e:
                    print(f"❌ Ошибка в строке {line_num}: {line} - {e}")

        return proxies

    async def get_random_proxy(self, file_path: Union[str, Path],
                               format_name: Optional[ProxyFormatType] = None,
                               default_protocol: str = "http") -> Optional[ProxyData]:
        """
        Асинхронно получает случайный прокси 🎲⚡

        Args:
            file_path: путь к файлу
            format_name: формат прокси или None для авто-определения
            default_protocol: протокол по умолчанию
        """
        proxies = await self.get_proxies(file_path, format_name, default_protocol)

        if not proxies:
            return None

        return random.choice(proxies)

    async def get_random_proxies(self, file_path: Union[str, Path],
                                 count: int,
                                 format_name: Optional[ProxyFormatType] = None,
                                 default_protocol: str = "http",
                                 unique: bool = True) -> List[ProxyData]:
        """
        Асинхронно получает несколько случайных прокси 🎯⚡

        Args:
            file_path: путь к файлу
            count: количество прокси
            format_name: формат прокси или None для авто-определения
            default_protocol: протокол по умолчанию
            unique: если True, то прокси не повторяются
        """
        proxies = await self.get_proxies(file_path, format_name, default_protocol)

        if not proxies:
            return []

        if unique and count >= len(proxies):
            return proxies
        elif unique:
            return random.sample(proxies, count)
        else:
            return [random.choice(proxies) for _ in range(count)]

    async def read_multiple_files(self, file_paths: List[Union[str, Path]],
                                  format_name: Optional[ProxyFormatType] = None,
                                  default_protocol: str = "http") -> List[ProxyData]:
        """
        Параллельное чтение множественных файлов 🚀

        Args:
            file_paths: список путей к файлам
            format_name: формат прокси или None для авто-определения
            default_protocol: протокол по умолчанию
        """
        # 🔥 Запускаем все файлы параллельно
        tasks = [
            self.get_proxies(file_path, format_name, default_protocol)
            for file_path in file_paths
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 📊 Объединяем результаты
        all_proxies = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Ошибка в файле {file_paths[i]}: {result}")
            else:
                all_proxies.extend(result)

        return all_proxies