from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from vivod import main  # Убедитесь, что функция main существует в vivod.py

app = FastAPI()

# Настройка для работы с шаблонами
templates = Jinja2Templates(directory="templates")

# Настройка статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    main()  # Вызов функции main из vivod.py
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/doctors", response_class=HTMLResponse)
async def get_doctors(request: Request):
    with open("results.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    doctors = []
    for clinic_id, doctor_list in data.get("clinic_doctors", {}).items():
        for doctor in doctor_list:
            first_name = doctor["doctor"]["entity"]["person"]["entity"]["firstName"]
            last_name = doctor["doctor"]["entity"]["person"]["entity"]["lastName"]
            specialization = doctor["doctor"]["entity"]["doctorType"]["name"]
            doctors.append({"first_name": first_name, "last_name": last_name, "specialization": specialization})

    return templates.TemplateResponse("doctors.html", {"request": request, "doctors": doctors})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)