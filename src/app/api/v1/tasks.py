from typing import Annotated, Any,List
import urllib.parse
import aiofiles
import uuid
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from arq.jobs import Job as ArqJob
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException,Form, Query
from fastapi.responses import FileResponse
from app.api.dependencies import rate_limiter_dependency
from app.core.utils import queue
from app.schemas.job import Job
import os
from app.crud.crud_tasks import crud_tasks
from app.models.user import Users
from app.api.dependencies import get_current_user
from app.core.db.database import async_get_db
from app.schemas.task import TaskCreateInternal,TaskRead, TaskUpdate
router = APIRouter(prefix="/tasks", tags=["tasks"])

TEMP_REQ_DIR = "/tmp/req/"
TEMP_PROCESS_DIR = "/tmp/pro/"
@router.post("/task", response_model=Job, status_code=201, dependencies=[Depends(rate_limiter_dependency)])
async def create_task(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    master_lang: str = Form(...),
    slave_lang: str = Form(...),
    file: UploadFile = File(...),
    user: Users | None = Depends(get_current_user),
) -> dict[str, str]:
    """Create a new background task with a file."""
    if user:
        user_id = user["uuid"]
        os.makedirs(TEMP_REQ_DIR, exist_ok=True)
        file_location = os.path.join(TEMP_REQ_DIR, file.filename)
        os.makedirs(TEMP_PROCESS_DIR, exist_ok=True)
        destination_location = os.path.join(TEMP_PROCESS_DIR, file.filename)
        async with aiofiles.open(file_location, "wb") as buffer:
            await buffer.write(await file.read())
        id = uuid.uuid4()
        job = await queue.pool.enqueue_job("translate",file_location,destination_location,id)  # type: ignore
        Job = TaskCreateInternal(
           id=id,
           user_id=user_id,
           job_id=job.job_id,
           master_lang=master_lang,
           slave_lang=slave_lang,
           name=name,
           status="pending",
           requested_path=file_location,
           processed_path=destination_location
        )
        res = await crud_tasks.create(db=db, object=Job)
        print(res)
        return {"id": job.job_id}


@router.get("/task/{task_id}")
async def get_task(task_id: str, db: Annotated[AsyncSession, Depends(async_get_db)], user: Users | None = Depends(get_current_user),
) -> dict[str, Any] | None:
    """Get information about a specific background task.

    Parameters
    ----------
    db
    task_id: str
        The ID of the task.

    Returns
    -------
    Optional[dict[str, Any]]
        A dictionary containing information about the task if found, or None otherwise.
    """

    
    job = ArqJob(task_id, queue.pool)
    job_info: dict = await job.info()
    if job_info and hasattr(job_info, 'success'):
        if job_info.success:
            task_id = job_info.args[3]
            user_id = user["uuid"]
            if task_id and user_id:
                task_update = TaskUpdate(
                    id=task_id,
                    user_id=user_id,
                    status="success"
                )
                res = await crud_tasks.update(db=db, id=task_id, object=task_update)
    

    return vars(job_info)


@router.get("/download/{task_id}")
async def download_file(task_id: str, db: Annotated[AsyncSession, Depends(async_get_db)], user: Users | None = Depends(get_current_user),
) -> FileResponse:
    """Download a file from the server.

    Parameters
    ----------
    db
    task_id
        The name of the file to download. please if you add /tmp/* remove it. example: file.txt

    Returns
    -------
    FileResponse
        The response containing the file for download.
    """
    # Decode the URL-encoded filename
    crud_task = await crud_tasks.get(db=db, job_id=task_id,user_id=user["uuid"])
    # Check if the file exists before serving it
    if not os.path.exists(crud_task.processed_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(crud_task.processed_path, media_type='application/octet-stream', filename=crud_task.processed_path)


@router.get("/jobs", response_model=PaginatedListResponse[TaskRead], dependencies=[Depends(rate_limiter_dependency)])
async def get_all_jobs(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 10,
    user: Users | None = Depends(get_current_user),
) -> dict:

    tasks_data = await crud_tasks.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=TaskRead,
        user_id=user["uuid"],
    )

    response: dict[str, Any] = paginated_response(crud_data=tasks_data, page=page, items_per_page=items_per_page)
    return response