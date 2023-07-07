from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from Routes.routes import routes

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(routes)   


