import logging

from fastapi import FastAPI

from app.middleware import ProcessTimeMiddleware
from app.routers import tasks, users

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

app = FastAPI(title="Task Manager")

app.add_middleware(ProcessTimeMiddleware)

app.include_router(users.router)
app.include_router(tasks.router)


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok"}