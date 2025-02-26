import asyncio
import logging
from time import sleep
import uuid
import uvloop
from arq.worker import Worker
from app.schemas.task import TaskUpdate
from app.crud.crud_tasks import crud_tasks
from app.core.db.database import async_get_db
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


# -------- background tasks --------
async def translate(ctx: 'Worker', file_location: str,destination_location: str, id: uuid.UUID) -> str:
    # Simulate some work (e.g., translation)
    await asyncio.sleep(30)

    print(f"Processing file at {file_location}")
    
    return f"Task is complete!"


# -------- base functions --------
async def startup(ctx: Worker) -> None:
    logging.info("Worker Started")


async def shutdown(ctx: Worker) -> None:
    logging.info("Worker end")
