import sqlite3
from dataclasses import dataclass

from loguru import logger
from prettytable import PrettyTable


@dataclass
class RunnerResult:
    """Результат выполнения запроса"""

    executed: bool  # Выполнен ли запрос
    rows: tuple = ()  # Список столбцов
    columns: tuple = ()  # Список названий колонок
    errors: list = None  # Cписок ошибок
    pretty: str = ""  # Текстовое представление таблички с результатом

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def __post_init__(self) -> None:
        """Рисует красивую табличку """

        table: PrettyTable = PrettyTable()
        table.field_names = self.columns

        for row in self.rows:
            table.add_row(row)

        self.pretty = str(table)


class Runner:

    """Выполняет SQL операции: устанавливает дамп, делает запрос"""

    def __init__(self):
        self.connect: sqlite3.Connection = sqlite3.connect(':memory:')
        self.cur = self.connect.cursor()
        self.query_result: RunnerResult = RunnerResult(False)

    def install_dump(self, query) -> sqlite3.Cursor:
        """ Загружает дамп из файла в базу чтобы использовать в упражнении"""
        result = self.cur.executescript(query) # Выполняем запрос с помощью курсора
        return result

    def run_query(self, query: str) -> RunnerResult:
        """Возвращает результаты запроса в специальном виде с указанием строк и столбцов"""

        try:
            self.cur.execute(query)    # Выполняем запрос с помощью курсора

        except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
            logger.debug(f"Запрос запущен но выполнен с ошибкой {e}")
            self.query_result: RunnerResult = RunnerResult(executed=True, errors=e)
            return self.query_result
        else:
            logger.debug("Запрос запущен и выполнен без ошибки")

        # Получаем колонки и делаем фикс при пустом отправленном запросе
        columns = [name[0] for name in self.cur.description] if self.cur.description else []

        # Получаем строки
        rows = self.cur.fetchall()

        # Запихиваем это все в датакласс
        self.query_result: RunnerResult = RunnerResult(
            rows=tuple(rows), columns=tuple(columns), executed=True
        )

        # Отдаем готовый датакласс
        return self.query_result

    # def check_result(self, query_result):




