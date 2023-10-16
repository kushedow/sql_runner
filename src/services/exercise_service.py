from dataclasses import dataclass

from loguru import logger

from src.classes.runner import Runner, RunnerResult
from src.classes.manager import Exercise, ExerciseManager
from src.classes.ai_manager import AIManager


@dataclass
class CheckResult:

    message: str
    is_correct: bool = False


class ExerciseService:

    def __init__(self, manager):

        self.manager: ExerciseManager = manager
        self.ai_manager: AIManager = AIManager()

    def reload_manager(self):
        logger.info(f"Выгружаем заново все таблицы")
        self.manager.load_all()

    def get_all_exercises(self) -> dict[str: Exercise]:
        """Все доступные упражнения"""
        logger.info(f"Получаем все упражнения")
        return self.manager.get_all_exercises()

    def get_exercise(self, pk: int):
        """Получить упражнение по его pk"""
        logger.info(f"Получаем упражнение {pk}")
        exercise: Exercise = self.manager.get_exercise(pk)
        return exercise

    def get_explanation(self, exercise_pk):
        """Объяснить упражнение с помощью Chat GPT"""
        # Получаем упражнение
        exercise: Exercise = self.get_exercise(exercise_pk)
        # Объясняем упражнение

        if exercise is None:
            return

        if exercise.explanation is not None:
            return exercise.explanation

        exercise.explanation = self.ai_manager.get_explanation(exercise)
        return exercise.explanation

    def run_attempt(self, pk, attempt):
        """Проверить решение ученика по его pk"""

        runner = Runner()

        # получаем упражнение
        exercise = self.get_exercise(pk)

        # готовим базу к выполнению задания
        logger.warning(f"Запускаем создание таблиц \n{exercise.database.database_tables}")
        runner.install_dump(exercise.database.database_tables)

        logger.warning(f"Запускаем наполнение таблиц \n{exercise.database.database_entitles} ")
        runner.install_dump(exercise.database.database_entitles)

        # запускаем код, полученный от клиента

        logger.warning(f"Запускаем код пользователя задания {pk} с кодом <{attempt}> ")
        user_result: RunnerResult = runner.run_query(attempt)

        logger.info(f"Запускаем проверку 'эталонного задания' {exercise.solution_code} ")
        solution_result = runner.run_query(exercise.solution_code)
        user_result_check: CheckResult = self.compare_to_solution(user_result, solution_result)

        # принудительно убиваем раннер вместе с подключением к БД
        del runner

        return user_result, user_result_check

    @staticmethod
    def compare_to_solution(at_result: RunnerResult, sl_result: RunnerResult) -> CheckResult:
        """ Сверяем результат решения пользователя с эталоннм решением """

        # Если не совпадают колонки – говорим об этом
        if at_result.columns != sl_result.columns:
            return CheckResult(is_correct=False, message=f"Колонки не совпадают. Должно быть {sl_result.columns}")

        # Если не совпадает количество строк – говорим об этом
        if len(at_result.rows) != len(sl_result.rows):
            return CheckResult(is_correct=False, message=f"Количество строк не совпадает. Должно быть {len(sl_result.columns)}")

        # TODO Тут бы добавить еще проверок

        # Если все ок
        return CheckResult(is_correct=True, message="Все верно")



