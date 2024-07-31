import unittest
from unittest.mock import patch, MagicMock
import uuid

from console_library import ConsoleLibrary
from db_desktop import JsonStorage
from config import ConfigLoader
from validator import Validator


class TestConsoleLibrary(unittest.TestCase):
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Подготовка моков для зависимостей
        self.mock_json_storage = MagicMock(spec=JsonStorage)
        self.mock_config_loader = MagicMock(spec=ConfigLoader)
        self.mock_validator = MagicMock(spec=Validator)

        # Создание тестируемого объекта с моками
        self.library = ConsoleLibrary(json_path="test_library.json", config_path="test_config.json")
        self.library._json = self.mock_json_storage
        self.library.config = self.mock_config_loader
        self.library.validator = self.mock_validator

        # Пример данных
        self.book_id = str(uuid.uuid4())
        self.test_book = {
            "id": self.book_id,
            "title": "Test Title",
            "author": "Test Author",
            "year": "2020",
            "status": "в наличии"
        }

    @patch('builtins.input', side_effect=["Test Title", "Test Author", "2020"])
    @patch('builtins.print')
    def test_add_book(self, mock_print, mock_input):
        """Тест для добавления книги"""
        # Настройка моков
        self.mock_validator.is_valid_title.return_value = True
        self.mock_validator.is_valid_author.return_value = True
        self.mock_validator.is_valid_year.return_value = True
        self.mock_config_loader.get.return_value = "в наличии"

        # Выполнение тестируемого метода
        result = self.library._add_book()

        # Проверка результатов
        self.assertTrue(result)
        self.mock_json_storage.save.assert_called_once()
        mock_print.assert_called_once()

    @patch('builtins.input', side_effect=[str(uuid.uuid4())])
    @patch('builtins.print')
    def test_delete_book_not_found(self, mock_print, mock_input):
        """Тест для удаления книги, которая не найдена"""
        self.mock_json_storage._json_storage = {}

        # Выполнение тестируемого метода
        self.library._delete_book()

        # Проверка результатов
        mock_print.assert_called_once_with(self.mock_config_loader.get("book_not_found").format(book_id=mock_input()))

    @patch('builtins.input', side_effect=["Test Title"])
    @patch('builtins.print')
    def test_search_book(self, mock_print, mock_input):
        """Тест для поиска книги по названию"""
        self.mock_validator.is_valid_title.return_value = True
        self.mock_json_storage._json_storage = {self.book_id: self.test_book}
        self.mock_config_loader.get.side_effect = [
            "Введите критерий поиска (title, author или year): ",
            "Введите значение для title: "
        ]

        # Выполнение тестируемого метода
        result = self.library._search_book()

        # Проверка результатов
        self.assertTrue(result)
        mock_print.assert_called()

    @patch('builtins.input', side_effect=[str(uuid.uuid4()), "в наличии"])
    @patch('builtins.print')
    def test_change_status_not_found(self, mock_print, mock_input):
        """Тест для изменения статуса книги, которая не найдена"""
        self.mock_json_storage._json_storage = {}

        # Выполнение тестируемого метода
        result = self.library._change_status()

        # Проверка результатов
        self.assertFalse(result)
        mock_print.assert_called_once_with(self.mock_config_loader.get("book_not_found").format(book_id=mock_input()))

    @patch('builtins.print')
    def test_display_books(self, mock_print):
        """Тест для отображения всех книг"""
        self.mock_json_storage._json_storage = {self.book_id: self.test_book}

        # Выполнение тестируемого метода
        self.library._display_books()

        # Проверка результатов
        mock_print.assert_called()


if __name__ == '__main__':
    unittest.main()
