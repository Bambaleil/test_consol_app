import json
from typing import Any


class ConfigLoader:
    """Класс для загрузки конфигурационных данных, таких как сообщения и статусы."""

    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as file:
            self.config = json.load(file)

    def get(self, key: str) -> Any:
        return self.config.get(key)