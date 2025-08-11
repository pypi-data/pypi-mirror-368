"""Синхронное чтение прокси из файлов 📁"""

import random
from typing import List, Dict, Optional, Union
from pathlib import Path

from .core import ProxyData, ProxyParser, ProxyFormatType


class ProxyFileReader:
    """Чтение прокси из файлов 📁"""

    def __init__(self):
        self.parser = ProxyParser()
        self.encoding = 'utf-8'

    def get_proxies(self, file_path: Union[str, Path], format_name: Optional[ProxyFormatType] = None,
                    default_protocol="http") -> List[ProxyData]:
        """
        Читает прокси из файла 📖

        Args:
            file_path: путь к файлу
            format_name: формат прокси или None для авто-определения
            default_protocol: протокол по умолчанию
        """
        proxies = []
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Файл {file_path} не найден")

        with open(file_path, 'r', encoding=self.encoding) as f:
            for line_num, line in enumerate(f, 1):
                original_line = line.strip()
                if not original_line or original_line.startswith('#'):
                    continue

                try:
                    proxy = self.parser.parse_line(original_line, format_name, default_protocol)
                    if proxy:
                        proxies.append(proxy)
                    else:
                        # 🔥 Подробный вывод ошибок
                        print(f"❌ Строка {line_num}: '{original_line}' не соответствует формату '{format_name or 'авто'}'")
                except Exception as e:
                    print(f"❌ Ошибка парсинга строки {line_num}: '{original_line}' - {e}")

        return proxies

    def get_random_proxy(self, file_path: Union[str, Path], format_name: Optional[ProxyFormatType] = None,
                         default_protocol: str = "http") -> Optional[ProxyData]:
        """
        Получает случайный прокси из файла 🎲

        Args:
            file_path: путь к файлу
            format_name: формат прокси или None для авто-определения
            default_protocol: протокол по умолчанию

        Returns:
            Случайный прокси или None если файл пустой
        """
        # 📖 Используем существующий метод
        proxies = self.get_proxies(file_path, format_name, default_protocol)

        if not proxies:
            return None

        # 🎲 Возвращаем случайный
        return random.choice(proxies)

    def get_formats(self) -> Dict[ProxyFormatType, str]:
        """Получить все доступные форматы 📋"""
        return {name: fmt.description for name, fmt in self.parser.FORMATS.items()}