import json
from json import JSONDecodeError
from typing import Any


class ConfigLoader:
    """Класс для загрузки конфигурационных данных, таких как сообщения и статусы."""

    def __init__(self, config_path: str):
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
        except (FileNotFoundError, JSONDecodeError) as e:
            print(f"Error loading config: {e}")
            self.config = {}

    def get(self, key: str) -> Any:
        return self.config.get(key)