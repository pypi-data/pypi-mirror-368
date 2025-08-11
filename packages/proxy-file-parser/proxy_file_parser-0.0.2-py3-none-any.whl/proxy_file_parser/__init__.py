"""
Proxy File Parser - библиотека для парсинга различных форматов прокси 🌐

Поддерживает 13+ форматов прокси с синхронным и асинхронным чтением файлов.
"""

from .core import ProxyData, ProxyFormat, ProxyParser, ProxyFormatType
from .async_parser import AsyncProxyParser
from .sync_parser import ProxyParser

__version__ = "0.0.2"
__author__ = "Limby"
__email__ = "bogo44tor@gmail.com"

__all__ = [
    "ProxyData",
    "ProxyFormat",
    "ProxyParser",
    "ProxyFormatType",
    "AsyncProxyParser"
]