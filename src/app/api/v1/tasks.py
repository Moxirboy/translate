from typing import Any

import urllib.parse
import aiofiles
from arq.jobs import Job as ArqJob
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from ...api.dependencies import rate_limiter_dependency
from ...core.utils import queue
from ...schemas.job import Job
import os

router = APIRouter(prefix="/tasks", tags=["tasks"])

TEMP_DIR = "/tmp"


@router.post("/task", response_model=Job, status_code=201, dependencies=[Depends(rate_limiter_dependency)])
async def create_task(message: str, file: UploadFile = File(...)) -> dict[str, str]:
    """Create a new background task with a file.

    Parameters
    ----------
    message: str
        The message or data to be processed by the task.
    file: UploadFile
        The file to be processed by the task.

    Returns
    -------
    dict[str, str]
        A dictionary containing the ID of the created task.
    """
    file_location = os.path.join(TEMP_DIR, file.filename)

    async with aiofiles.open(file_location, "wb") as buffer:
        await buffer.write(await file.read())

    job = await queue.pool.enqueue_job("translate", message, file_location)  # type: ignore
    return {"id": job.job_id}


@router.get("/task/{task_id}")
async def get_task(task_id: str) -> dict[str, Any] | None:
    """Get information about a specific background task.

    Parameters
    ----------
    task_id: str
        The ID of the task.

    Returns
    -------
    Optional[dict[str, Any]]
        A dictionary containing information about the task if found, or None otherwise.
    """
    job = ArqJob(task_id, queue.pool)
    job_info: dict = await job.info()
    return vars(job_info)


@router.get("/download/{filename}")
async def download_file(filename: str) -> FileResponse:
    """Download a file from the server.

    Parameters
    ----------
    filename: str
        The name of the file to download. please if you add /tmp/* remove it. example: file.txt

    Returns
    -------
    FileResponse
        The response containing the file for download.
    """
    # Decode the URL-encoded filename

    # Construct the full file path
    file_path = os.path.join(TEMP_DIR, filename)

    # Check if the file exists before serving it
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type='application/octet-stream', filename=filename)