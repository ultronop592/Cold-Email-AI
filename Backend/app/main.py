from fastapi import FastAPI
from routes.generte_email import router

app = FastAPI()

app.include_router(router)