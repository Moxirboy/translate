from fastcrud import FastCRUD

from app.models.task import Tasks
from app.schemas.task import TaskRead, TaskCreateInternal, TaskUpdate


CRUDTask = FastCRUD[Tasks,  TaskCreateInternal, TaskUpdate,TaskRead,None,None]
crud_tasks = CRUDTask(Tasks)
