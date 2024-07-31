import uuid
from abc import ABC
from typing import Dict, Callable, List

from config import ConfigLoader
from db_desktop import JsonStorage
from type import DictBook
from validator import Validator


class ConsoleApp(ABC):
    pass


class ConsoleLibrary(ConsoleApp):
    def __init__(self, json_path="library.json", config_path="config.json"):
        self._json = JsonStorage(file_path=json_path)
        self._json_storage: Dict | Dict[str, DictBook] = self._json.load()
        self.config = ConfigLoader(config_path=config_path)
        self.validator = Validator()

    @staticmethod
    def _print_book_info(book: DictBook) -> None:
        """Функция выводит информацию о книге"""
        print(f"ID книги: {book['id']}\n"
              f"Название книги: {book['title']}\n"
              f"Автор книги: {book['author']}\n"
              f"Год книги: {book['year']}\n"
              f"Статус книги: {book['status']}\n")

    def _valid_input(self, prompt: str, func: Callable[[str], bool]) -> str | bool:
        """Функция для валидации вводных данных"""
        count: int = 0
        while count < 3:
            user_input = input(prompt)
            if func(user_input):
                return user_input
            count += 1
            print(self.config.get("invalid_input"))
        print(self.config.get("too_many_errors"))
        return False

    def _get_valid_input(self, prompt: str, validation_func: Callable[[str], bool]) -> str:
        """Получить валидный ввод от пользователя"""
        result = self._valid_input(prompt, validation_func)
        if result is False:
            raise ValueError(self.config.get("too_many_errors"))
        return result

    def _add_book(self) -> bool:
        """Функция добавляет новую книгу проверяя на валидность данные с индивидуальным ID"""
        try:
            title: str = self._get_valid_input("Введите название книги: ",
                                               self.validator.is_valid_title).strip().title()
            author: str = self._get_valid_input("Введите автора книги: ",
                                                self.validator.is_valid_author).strip().title()
            year: str = self._get_valid_input("Введите год издания книги: ",
                                              self.validator.is_valid_year).strip().lower()
        except ValueError:
            return False

        book_id: str = str(uuid.uuid4())
        self._json_storage[book_id] = {
            "id": book_id,
            "title": title,
            "author": author,
            "year": year,
            "status": self.config.get("STATUS_AVAILABLE")
        }
        print(self.config.get("book_added").format(book_id=book_id))
        self._json.save(self._json_storage)
        return True

    def _delete_book(self) -> None:
        """Функция удаляет книгу по ID"""
        book_id = input("Введите ID книги, которую нужно удалить: ")
        if book_id in self._json_storage:
            del self._json_storage[book_id]
            print(self.config.get("book_deleted").format(book_id=book_id))
            self._json.save(self._json_storage)
        else:
            print(self.config.get("book_not_found").format(book_id=book_id))

    def _display_books(self) -> None:
        """Функция выдает список всех книг которые есть в библиотеке на данный момент"""
        if self._json_storage:
            print(f"Всего книг в библиотеке: {len(self._json_storage)} шт.\n")
            for book in self._json_storage.values():
                self._print_book_info(book)
        else:
            print(self.config.get("no_books"))

    def _change_status(self) -> bool:
        """Функция меняет статус книги"""
        book_id = input("Введите ID книги: ")
        if book_id in self._json_storage:
            try:
                new_status = self._get_valid_input(
                    "Введите новый статус книги ({} или {}): ".format(
                        self.config.get("STATUS_AVAILABLE"),
                        self.config.get("STATUS_ISSUED")
                    ),
                    lambda x: x in self.config.get("STATUSES")
                ).strip().lower()
            except ValueError:
                return False
            self._json_storage[book_id]["status"] = new_status
            print(self.config.get("status_changed").format(book_id=book_id, status=new_status))
            self._json.save(self._json_storage)
            return True
        else:
            print(self.config.get("book_not_found").format(book_id=book_id))
            return False

    def _search_book(self) -> bool:
        """Функция для поиска книги по критерию"""
        dict_func_valid: Dict[str, Callable] = {
            "title": self.validator.is_valid_title,
            "author": self.validator.is_valid_author,
            "year": self.validator.is_valid_year
        }
        try:
            criteria: str = self._get_valid_input(
                self.config.get("search_criteria"),
                lambda x: x in dict_func_valid
            ).strip().lower()
            value: str = self._get_valid_input(
                self.config.get("search_value").format(criteria=criteria),
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
            print(self.config.get("no_books_found"))
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

    def _start_menu(self) -> int:
        """Функция отображает главное меню и запрашивает у пользователя выбор действия"""
        print(self.config.get("welcome"))
        print(self.config.get("menu"))
        while True:
            try:
                answer: int = int(input())
                if 0 <= answer < 6:
                    return answer
                else:
                    raise ValueError
            except ValueError:
                print(self.config.get("input_error"))

    def main(self) -> None:
        """Главная функция для запуска приложения"""
        while True:
            answer: int = self._start_menu()
            if not self._response_handler(answer):
                print(self.config.get("goodbye"))
                break


if __name__ == '__main__':
    ConsoleLibrary().main()
