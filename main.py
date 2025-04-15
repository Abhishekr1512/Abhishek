from fastapi import FastAPI
from routes import router

app = FastAPI(title="Insta demo app upload or download image")

app.include_router(router, prefix="/api")
