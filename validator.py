from datetime import datetime


class Validator:
    """Класс для валидации входных данных."""
    @staticmethod
    def is_valid_title(title: str) -> bool:
        """Функция проверяет название книги на валидность"""
        return bool(title.strip()) and all(part.isalnum() for part in title.split())

    @staticmethod
    def is_valid_author(author: str) -> bool:
        """Функция проверяет автора книги на валидность"""
        return bool(author.strip()) and all(part.isalpha() for part in author.split())

    @staticmethod
    def is_valid_year(year: str) -> bool:
        """Функция проверяет год издания книги на валидность"""
        return year.isdigit() and 0 <= int(year) <= datetime.now().year