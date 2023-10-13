from dataclasses import asdict

from fastapi import FastAPI, Request
from starlette.datastructures import FormData
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from src.classes.manager import exercise_manager, Exercise
from src.services.exercise_service import ExerciseService

app = FastAPI()
service = ExerciseService(exercise_manager)
templates = Jinja2Templates(directory="src/templates")


@app.get("/run/{exercise_id}")
async def get(request: Request, exercise_id: int):
    """Вьюшка для отображения упражнения"""
    exercise: Exercise = service.get_exercise(exercise_id)
    return templates.TemplateResponse("index.html", {"request": request, "exercise": exercise, "result": None, "attempt_check": None})


@app.post("/run/{exercise_id}")
async def run(request: Request, exercise_id: int):
    """Вьюшка для проверки упражнения"""

    exercise: Exercise = service.get_exercise(exercise_id)
    form_data: FormData = await request.form()

    # исправляем баг с передачей неразрывных пробелов
    attempt = form_data.get("attempt").replace("\xa0", " ")

    # запускаем проверку задания
    attempt_result, attempt_check = service.run_attempt(exercise_id, attempt)

    context = {
        "request": request,
        "exercise": exercise,
        "result": asdict(attempt_result),
        "attempt_check": asdict(attempt_check),
        "attempt": attempt,
    }

    return templates.TemplateResponse("index.html", context)


# Добавляем статику на будущее
app.mount("/static", StaticFiles(directory="src/static"), name="static")
