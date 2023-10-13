from dataclasses import dataclass, asdict
import gspread
from src.config import SHEET_ID


@dataclass
class Database:

    """Базы данных для упражнений"""

    database_name: str  # ключ для базы данных
    database_tables: str  # код для создания таблиц
    database_entitles: str  # код для наполнения таблиц
    database_structure: str  # визуальная структура таблицы


@dataclass
class Exercise:

    """Базы данных для упражнений"""

    pk: int  # номер упражнения
    title: str  # название упражнения
    hint: str  # подсказка
    instruction: str  # текст инструкции
    database_name: str  # имя базы данных для линковки с исходниками БД

    source_code: str  # исходный код, который будет в редакторе
    solution_code: str  # код решения для проверки результатов

    database: Database = None  # ссылка на базу данных

    def __post_init__(self):
        self.pk = int(self.pk)

    def dict(self):
        return asdict(self)


class ExerciseManager:

    """Обертка упражнения и базы данных из гугл-документов"""

    def __init__(self, sheet_id):
        self.gc = gspread.service_account()
        self.file = self.gc.open_by_key(sheet_id)

        self.sheet_databases = self.file.get_worksheet(1)  # ссылка на интерфейс таблицы базы данных
        self.sheet_exercises = self.file.get_worksheet(0)  # ссылка на интерфейс таблицы упражнений

        self.exercises = self._load_exercises()

    def _load_databases(self) -> dict[str: Database]:
        """Загружаем базы данных"""
        records: dict = self.sheet_databases.get_all_records()
        return {db["database_name"]: Database(**db) for db in records}

    def _load_exercises(self) -> dict[str:Exercise]:
        """Загружаем упражнения"""

        databases: dict[int: Database] = self._load_databases()
        records: dict = self.sheet_exercises.get_all_records()
        exercises: dict[int:] = {ex["pk"]: Exercise(**ex) for ex in records}

        # досыпаем к заданиям информацию по базам данных
        for ex in exercises.values():
            ex.database = databases.get(ex.database_name)

        return exercises

    def get_exercise(self, pk: int) -> Exercise | None:
        """Достает из кеша упражнение"""
        return self.exercises.get(pk, None)


# создаем экземпляр интерфейса
exercise_manager = ExerciseManager(SHEET_ID)
