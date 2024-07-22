import unittest
from unittest.mock import patch

from console_library import ConsoleLibrary


class TestConsoleLibrary(unittest.TestCase):

    def setUp(self):
        """Подготовка к тестам"""
        self.library = ConsoleLibrary()
        self.library._json_storage = {}

    def test_is_valid_title(self):
        self.assertTrue(self.library._is_valid_title("Valid Title"))
        self.assertFalse(self.library._is_valid_title("Invalid Title!"))

    def test_is_valid_author(self):
        self.assertTrue(self.library._is_valid_author("Author"))
        self.assertFalse(self.library._is_valid_author("Author1"))

    def test_is_valid_year(self):
        self.assertTrue(self.library._is_valid_year("2023"))
        self.assertFalse(self.library._is_valid_year("abcd"))
        self.assertFalse(self.library._is_valid_year("3000"))

    @patch('builtins.input', side_effect=['Valid Title', 'Author', '2023'])
    def test_add_book(self, mock_input):
        self.library._add_book()
        self.assertEqual(len(self.library._json_storage), 1)
        book = list(self.library._json_storage.values())[0]
        self.assertEqual(book['title'], 'Valid Title')
        self.assertEqual(book['author'], 'Author')
        self.assertEqual(book['year'], '2023')
        self.assertEqual(book['status'], 'в наличии')

    @patch('builtins.input', side_effect=['Invalid Title!', 'Valid Title', 'Author', '2023'])
    def test_add_book_with_invalid_title(self, mock_input):
        self.library._add_book()
        self.assertEqual(len(self.library._json_storage), 1)
        book = list(self.library._json_storage.values())[0]
        self.assertEqual(book['title'], 'Valid Title')

    @patch('builtins.input', side_effect=['invalid-id'])
    def test_delete_book_invalid_id(self, mock_input):
        with patch('builtins.print') as mocked_print:
            self.library._delete_book()
            mocked_print.assert_called_with('Книга с ID invalid-id не найдена.')

    @patch('builtins.input', side_effect=['Valid Title', 'Author', '2023'])
    def test_delete_book(self, mock_input):
        self.library._add_book()
        book_id = list(self.library._json_storage.keys())[0]
        with patch('builtins.input', side_effect=[book_id]):
            self.library._delete_book()
            self.assertEqual(len(self.library._json_storage), 0)

    @patch('builtins.input', side_effect=['Valid Title', 'Author', '2023'])
    def test_display_books(self, mock_input):
        self.library._add_book()
        with patch('builtins.print') as mocked_print:
            self.library._display_books()
            book = list(self.library._json_storage.values())[0]
            mocked_print.assert_any_call(f"Всего книг в библиотеке: 1 шт.\n")
            mocked_print.assert_any_call(
                f"ID книги: {book['id']}\nНазвание книги: {book['title']}\nАвтор книги: {book['author']}\n"
                f"Год книги: {book['year']}\nСтатус книги: {book['status']}\n")

    @patch('builtins.input', side_effect=['title', 'Valid Title'])
    def test_search_book(self, mock_input):
        self.library._json_storage = {
            '1': {'id': '1', 'title': 'Valid Title', 'author': 'Author', 'year': '2023', 'status': 'в наличии'}
        }
        with patch('builtins.print') as mocked_print:
            self.library._search_book()
            mocked_print.assert_any_call(f"Всего книг в библиотеке: 1 шт.\n")
            mocked_print.assert_any_call(
                f"ID книги: 1\n"
                f"Название книги: Valid Title\n"
                f"Автор книги: Author\n"
                f"Год книги: 2023\n"
                f"Статус книги: в наличии\n")

    @patch('builtins.input', side_effect=['Valid Title', 'Author', '2023'])
    def test_change_status(self, mock_input):
        self.library._add_book()
        book_id = list(self.library._json_storage.keys())[0]
        with patch('builtins.input', side_effect=[book_id, 'выдана']):
            self.library._change_status()
            self.assertEqual(self.library._json_storage[book_id]['status'], 'выдана')


if __name__ == '__main__':
    unittest.main()
