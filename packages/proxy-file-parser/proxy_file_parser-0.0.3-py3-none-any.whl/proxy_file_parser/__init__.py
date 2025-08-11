"""
Proxy File Parser - библиотека для парсинга различных форматов прокси 🌐

Поддерживает 13+ форматов прокси с синхронным и асинхронным чтением файлов.
"""

from .async_parser import async_proxy_parser
from .sync_parser import proxy_parser

__version__ = "0.1.0"
__author__ = "Limby"
__email__ = "bogo44tor@gmail.com"

__all__ = [
    "async_proxy_parser",
    "proxy_parser"

]