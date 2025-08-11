"""Основные классы для парсинга прокси 🔧"""

import re
from typing import List, Dict, Optional, Any, Literal
from dataclasses import dataclass

# 🎯 Определяем доступные форматы через Literal
ProxyFormatType = Literal[
    'protocol://login:pass@ip:port',
    'login:pass@ip:port',
    'pass:login@ip:port',
    'ip:port:login:pass',
    'ip:port:pass:login',
    'login:pass:ip:port',
    'pass:login:ip:port',
    'port:ip:login:pass',
    'port:ip:pass:login',
    'ip:port',
    'port:ip',
    'port@ip',
    'ip@port'
]


@dataclass
class ProxyData:
    """Класс для хранения данных прокси 🌐"""
    protocol: str
    login: Optional[str] = None
    password: Optional[str] = None
    ip: str = ""
    port: int = 0
    url: str = ""

    def __post_init__(self):
        """Автоматически собираем URL из компонентов 🔧"""
        if self.login and self.password:
            self.url = f"{self.protocol}://{self.login}:{self.password}@{self.ip}:{self.port}"
        else:
            self.url = f"{self.protocol}://{self.ip}:{self.port}"

    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь 📋"""
        return {
            'protocol': self.protocol,
            'login': self.login,
            'password': self.password,
            'ip': self.ip,
            'port': self.port,
            'url': self.url
        }

    def __str__(self) -> str:
        return self.url


@dataclass(frozen=True)
class ProxyFormat:
    """Формат парсинга прокси 📝"""
    name: str
    pattern: str
    groups: List[str]  # порядок групп в regex
    description: str

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"


class ProxyParser:
    """Парсер прокси с предустановленными форматами 🔧"""

    FORMATS: Dict[ProxyFormatType, ProxyFormat] = {
        'protocol://login:pass@ip:port': ProxyFormat(
            name='protocol://login:pass@ip:port',
            pattern=r'^(?:(\w+)://)?(?:([^:@]+):([^@]+)@)?([^:]+):(\d+)$',
            groups=['protocol', 'login', 'password', 'ip', 'port'],
            description='Полный URL с протоколом и авторизацией'
        ),
        'login:pass@ip:port': ProxyFormat(
            name='login:pass@ip:port',
            pattern=r'^([^:]+):([^@]+)@([^:]+):(\d+)$',
            groups=['login', 'password', 'ip', 'port'],
            description='Логин:пароль@IP:порт'
        ),
        'pass:login@ip:port': ProxyFormat(
            name='pass:login@ip:port',
            pattern=r'^([^:]+):([^@]+)@([^:]+):(\d+)$',
            groups=['password', 'login', 'ip', 'port'],
            description='Пароль:логин@IP:порт (обратный порядок)'
        ),
        'ip:port:login:pass': ProxyFormat(
            name='ip:port:login:pass',
            pattern=r'^([^:]+):(\d+):([^:]+):(.+)$',
            groups=['ip', 'port', 'login', 'password'],
            description='IP:порт:логин:пароль'
        ),
        'ip:port:pass:login': ProxyFormat(
            name='ip:port:pass:login',
            pattern=r'^([^:]+):(\d+):([^:]+):(.+)$',
            groups=['ip', 'port', 'password', 'login'],
            description='IP:порт:пароль:логин (обратная авторизация)'
        ),
        'login:pass:ip:port': ProxyFormat(
            name='login:pass:ip:port',
            pattern=r'^([^:]+):([^:]+):([^:]+):(\d+)$',
            groups=['login', 'password', 'ip', 'port'],
            description='Логин:пароль:IP:порт'
        ),
        'pass:login:ip:port': ProxyFormat(
            name='pass:login:ip:port',
            pattern=r'^([^:]+):([^:]+):([^:]+):(\d+)$',
            groups=['password', 'login', 'ip', 'port'],
            description='Пароль:логин:IP:порт (обратная авторизация)'
        ),
        'port:ip:login:pass': ProxyFormat(
            name='port:ip:login:pass',
            pattern=r'^(\d+):([^:]+):([^:]+):(.+)$',
            groups=['port', 'ip', 'login', 'password'],
            description='Порт:IP:логин:пароль'
        ),
        'port:ip:pass:login': ProxyFormat(
            name='port:ip:pass:login',
            pattern=r'^(\d+):([^:]+):([^:]+):(.+)$',
            groups=['port', 'ip', 'password', 'login'],
            description='Порт:IP:пароль:логин'
        ),
        'ip:port': ProxyFormat(
            name='ip:port',
            pattern=r'^([^:]+):(\d+)$',
            groups=['ip', 'port'],
            description='IP:порт (без авторизации)'
        ),
        'port:ip': ProxyFormat(
            name='port:ip',
            pattern=r'^(\d+):([^:@]+)$',
            groups=['port', 'ip'],
            description='Порт:IP (обратный порядок)'
        ),
        'port@ip': ProxyFormat(
            name='port@ip',
            pattern=r'^(\d+)@([^@]+)$',
            groups=['port', 'ip'],
            description='Порт@IP (с @ разделителем)'
        ),
        'ip@port': ProxyFormat(
            name='ip@port',
            pattern=r'^([^@]+)@(\d+)$',
            groups=['ip', 'port'],
            description='IP@порт (с @ разделителем)'
        )
    }

    def parse_line(self, line: str, format_name: Optional[ProxyFormatType] = None, default_protocol="http") -> Optional[ProxyData]:
        """
        Парсит строку прокси 🎯

        Args:
            line: строка с прокси
            format_name: название формата или None для авто-определения
            default_protocol: протокол по умолчанию
        """
        line = line.strip()
        if not line or line.startswith('#'):
            return None

        if format_name:
            # Используем указанный формат
            return self._parse_with_format(line, self.FORMATS[format_name], default_protocol)

        # Авто-определение формата
        for fmt in self.FORMATS.values():
            result = self._parse_with_format(line, fmt, default_protocol)
            if result:
                return result

        return None

    def _parse_with_format(self, line: str, fmt: ProxyFormat, default_protocol="http") -> Optional[ProxyData]:
        """Парсит строку с конкретным форматом 🔍"""
        match = re.match(fmt.pattern, line)
        if not match:
            return None

        groups = match.groups()
        proxy_data = {
            'protocol': default_protocol,
            'login': None,
            'password': None,
            'ip': '',
            'port': 0
        }

        # Заполняем данные согласно группам
        for i, field_name in enumerate(fmt.groups):
            if i < len(groups) and groups[i]:
                if field_name == 'port':
                    proxy_data[field_name] = int(groups[i])
                elif field_name == 'protocol':
                    proxy_data[field_name] = groups[i].lower()
                else:
                    proxy_data[field_name] = groups[i]

        return ProxyData(**proxy_data)

    def get_available_formats(self) -> List[ProxyFormatType]:
        """Возвращает список доступных форматов 📜"""
        return list(self.FORMATS.keys())

    def get_format_info(self, format_name: ProxyFormatType) -> str:
        """Информация о формате 📋"""
        return str(self.FORMATS[format_name])