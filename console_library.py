import uuid
from abc import ABC
from typing import Dict, Callable, List
from datetime import datetime
from db_desktop import JsonStorage
from type import DictBook


class ConsoleApp(ABC):
    pass


class ConsoleLibrary(ConsoleApp):

    def __init__(self):
        self._json = JsonStorage()
        self._json_storage: Dict | Dict[str, DictBook] = self._json.load()

    @staticmethod
    def _print_book_info(book: DictBook) -> None:
        """Функция выводит информацию о книге"""
        print(f"ID книги: {book['id']}\n"
              f"Название книги: {book['title']}\n"
              f"Автор книги: {book['author']}\n"
              f"Год книги: {book['year']}\n"
              f"Статус книги: {book['status']}\n")

    @staticmethod
    def _valid_input(prompt: str, func: Callable[[str], bool]) -> str | bool:
        """Функция для валидации вводных данных"""
        count: int = 0
        while count < 3:
            user_input = input(prompt)
            if func(user_input):
                return user_input
            count += 1
            print("Неверный ввод. Попробуйте снова.")
        print("Слишком много ошибок. Возвращение в главное меню.")
        return False

    @staticmethod
    def _is_valid_title(title: str) -> bool:
        """Функция проверяет название книги на валидность"""
        return bool(title.strip()) and all(part.isalnum() for part in title.split())

    @staticmethod
    def _is_valid_author(author: str) -> bool:
        """Функция проверяет автора книги на валидность"""
        return bool(author.strip()) and all(part.isalpha() for part in author.split())

    @staticmethod
    def _is_valid_year(year: str) -> bool:
        """Функция проверяет год издания книги на валидность"""
        return year.isdigit() and 0 <= int(year) <= datetime.now().year

    def _get_valid_input(self, prompt: str, validation_func: Callable[[str], bool]) -> str:
        """Получить валидный ввод от пользователя"""
        result = self._valid_input(prompt, validation_func)
        if result is False:
            raise ValueError("Слишком много ошибок")
        return result

    def _add_book(self) -> bool:
        """Функция добавляет новую книгу проверяя на валидность данные с индивидуальным ID"""
        try:
            title: str = self._get_valid_input("Введите название книги: ", self._is_valid_title).strip().title()
            author: str = self._get_valid_input("Введите автора книги: ", self._is_valid_author).strip().title()
            year: str = self._get_valid_input("Введите год издания книги: ", self._is_valid_year).strip().lower()
        except ValueError:
            return False

        book_id: str = str(uuid.uuid4())
        self._json_storage[book_id] = {
            "id": book_id,
            "title": title,
            "author": author,
            "year": year,
            "status": 'в наличии'
        }
        print(f"Книга добавлена с ID: {book_id}")
        self._json.save(self._json_storage)
        return True

    def _delete_book(self) -> None:
        """Функция удаляет книгу по ID"""
        book_id = input("Введите ID книги, которую нужно удалить: ")
        if book_id in self._json_storage:
            del self._json_storage[book_id]
            print(f"Книга с ID {book_id} удалена.")
            self._json.save(self._json_storage)
        else:
            print(f"Книга с ID {book_id} не найдена.")

    def _display_books(self) -> None:
        """Функция выдает список всех книг которые есть в библиотеке на данный момент"""
        if self._json_storage:
            print(f"Всего книг в библиотеке: {len(self._json_storage)} шт.\n")
            for book in self._json_storage.values():
                self._print_book_info(book)
        else:
            print("Библиотека пуста.")

    def _change_status(self) -> bool:
        """Функция меняет статус книги"""
        book_id = input("Введите ID книги: ")
        if book_id in self._json_storage:
            try:
                new_status = self._get_valid_input(
                    "Введите новый статус книги (“в наличии” или “выдана”): ",
                    lambda x: x in ["в наличии", "выдана"]
                ).strip().lower()
            except ValueError:
                return False
            self._json_storage[book_id]["status"] = new_status
            print(f"Статус книги с ID {book_id} изменен на {new_status}.")
            self._json.save(self._json_storage)
            return True
        else:
            print(f"Книга с ID {book_id} не найдена.")
            return False

    def _search_book(self) -> bool:
        """Функция для поиска книги по критерию"""
        dict_func_valid: Dict[str, Callable] = {
            "title": self._is_valid_title,
            "author": self._is_valid_author,
            "year": self._is_valid_year
        }
        try:
            criteria: str = self._get_valid_input(
                "Введите критерий поиска (“title”, “author” или “year”): ",
                lambda x: x in dict_func_valid
            ).strip().lower()
            value: str = self._get_valid_input(
                f"Введите значение для {criteria}: ",
                dict_func_valid[criteria]
            ).strip().lower()
        except ValueError:
            return False

        found_books: List = [book for book in self._json_storage.values() if book[criteria].lower() == value]
        if found_books:
            print(f"Всего книг в библиотеке: {len(found_books)} шт.\n")
            for book in found_books:
                self._print_book_info(book)
            return True
        else:
            print("Книги не найдены.\n")
            return False

    def _response_handler(self, answer: int) -> None | bool:
        """Функция обрабатывает пользовательский ввод и выполняет соответствующие действия"""
        functions: Dict[int, Callable] = {
            1: self._add_book,
            2: self._delete_book,
            3: self._search_book,
            4: self._display_books,
            5: self._change_status
        }
        if answer == 0:
            self._json.save(self._json_storage)
            return False
        if answer in functions:
            functions[answer]()
            return True

    @staticmethod
    def _start_menu() -> int:
        """Функция отображает главное меню и запрашивает у пользователя выбор действия"""
        text: str = ("Добрый день.\n"
                     "Введите цифру с действием.\n"
                     "1) Добавление книги\n"
                     "2) Удаление книги\n"
                     "3) Поиск книги\n"
                     "4) Отображение всех книг\n"
                     "5) Изменение статуса книги\n"
                     "0) Выход")
        print(text)
        while True:
            try:
                answer: int = int(input())
                if 0 <= answer < 6:
                    return answer
                else:
                    raise ValueError
            except ValueError:
                print("Нужно вводить только цифры от 0 до 5.")

    def main(self) -> None:
        """Главная функция для запуска приложения"""
        while True:
            answer: int = self._start_menu()
            if not self._response_handler(answer):
                print("Всего доброго")
                break
