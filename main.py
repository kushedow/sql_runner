from dataclasses import asdict

from fastapi import FastAPI, Request
from starlette.datastructures import FormData
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from src.classes.manager import exercise_manager, Exercise
from src.services.exercise_service import ExerciseService

app = FastAPI()
service = ExerciseService(exercise_manager)
render = Jinja2Templates(directory="src/templates").TemplateResponse
app.mount("/static", StaticFiles(directory="src/static"), name="static")


@app.get("/")
async def get(request: Request):
    """Вьюшка для главной – все упражнения"""
    all_exercises = service.get_all_exercises()
    return render("index.html", {"request": request, "exercises": all_exercises})


@app.get("/reload")
async def reload(request: Request):
    service.reload_manager()
    return HTMLResponse(content="Reloaded")


@app.get("/run/{exercise_id}")
async def get(request: Request, exercise_id: int):
    """Вьюшка для отображения упражнения"""
    exercise: Exercise = service.get_exercise(exercise_id)
    return render("exercise.html", {"request": request, "exercise": exercise, "result": None, "attempt_check": None})


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

    return render("exercise.html", context)


@app.get("/explain/{exercise_pk}")
async def explain(request: Request, exercise_pk: int) -> JSONResponse:
    """Вьюшка для объяснения решений задач через OPEN AI"""

    explanation = service.get_explanation(exercise_pk)

    if explanation is not None:
        return JSONResponse({"message": explanation})

    return JSONResponse({"message": "No explanation was created or exercise not found"}, 400)



