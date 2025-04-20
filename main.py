from fastapi import FastAPI
from routes import router
import uvicorn

app = FastAPI(title="Insta demo app upload or download image")

app.include_router(router, prefix="/api")

# this block is to run the swagger locally and test the APIs.
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)