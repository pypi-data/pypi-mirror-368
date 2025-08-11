"""
Proxy File Parser - библиотека для парсинга различных форматов прокси 🌐

Поддерживает 13+ форматов прокси с синхронным и асинхронным чтением файлов.
"""

from .core import ProxyData, ProxyFormat, ProxyParser, ProxyFormatType
from .sync_reader import ProxyFileReader
from .async_reader import AsyncProxyFileReader

__version__ = "0.0.1"
__author__ = "Limby"
__email__ = "bogo44tor@gmail.com"

__all__ = [
    "ProxyData",
    "ProxyFormat",
    "ProxyParser",
    "ProxyFormatType",
    "ProxyFileReader",
    "AsyncProxyFileReader"
]