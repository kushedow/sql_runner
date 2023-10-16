import os

import openai
from loguru import logger

from src.classes.manager import Exercise

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if OPENAI_API_KEY is None:
    raise NameError("OPENAI_API_KEY is not set")


class AIManager:

    @staticmethod
    def _build_prompt(exercise: Exercise):
        prompt = f"Есть таблица в базе данных, которая формируется таким запросом:" \
                 f"{exercise.database.database_tables} ;" \
                 f"У нас есть задание:" \
                 f"<Начало>{exercise.instruction}<Конец>" \
                 f"Объясни максимально подробно, с объяснением каждого ключевого слова, почему решением задачи будет" \
                 f"<Начало>{exercise.solution_code}<Конец>"

        return prompt.strip()

    @staticmethod
    def _make_request(prompt):
        """Выполняем запрос"""
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
        response = completion.choices[0].message.content
        return response

    def get_explanation(self, exercise):
        """Получаем ответ от OPEN AI"""
        logger.debug("Отправляем ")
        prompt = self._build_prompt(exercise)
        response = self._make_request(prompt)
        return response
