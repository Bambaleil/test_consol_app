from abc import ABC, abstractmethod
import json
from json import JSONDecodeError
from typing import Dict, Any

from type import DictBook


class Storage(ABC):
    """Абстрактный класс для хранения данных"""

    @abstractmethod
    def save(self, info: Any) -> None:
        """Абстрактная функция для сохранения данных"""
        pass

    @abstractmethod
    def load(self) -> Any:
        """Абстрактная функция для загрузки данных"""
        pass


class JsonStorage(Storage):
    """Класс для хранения данных в json формате"""

    def __init__(self, file_path: str = "library.json"):
        self._file_path = file_path

    def save(self, info: Dict | Dict[str, DictBook]) -> None:
        """Функция для сохранения данных в json формате"""
        with open(self._file_path, 'w', encoding='utf-8') as file:
            json.dump(info, file, ensure_ascii=False, indent=4)

    def load(self) -> Dict | Dict[str, DictBook]:
        """Функция для загрузки данных в json формате"""
        try:
            with open(self._file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, JSONDecodeError):
            return {}
