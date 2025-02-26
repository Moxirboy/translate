from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class TaskBase(BaseModel):
    id: UUID = Field(..., description="The ID of the task to be updated")
    user_id: UUID
    job_id: Optional[str] = Field(None, description="The job ID of the task")
    master_lang: Optional[str] = Field(None, description="The master language of the task")
    slave_lang: Optional[str] = Field(None, description="The slave language of the task")
    name: Optional[str] = Field(None, description="The name of the task")
    status: Optional[str] = Field(None, description="The status of the task")
    requested_path: Optional[str] = Field(None, description="The file path associated with the task")
    processed_path: Optional[str] = Field(None, description="The file path associated with the task")

class TaskCreate(BaseModel):
    master_lang: str
    slave_lang: str
    name: str

    class Config:
        orm_mode = True

class TaskCreateInternal(TaskBase):
    id: UUID = Field(..., description="The ID of the task to be updated")
class TaskUpdate(TaskBase):
    status: Optional[str] = Field(None, description="The status of the task")


class TaskRead(BaseModel):
    id: UUID = Field(..., description="The ID of the task to be updated")
    user_id: UUID
    job_id: Optional[str] = Field(None, description="The job ID of the task")
    master_lang: Optional[str] = Field(None, description="The master language of the task")
    slave_lang: Optional[str] = Field(None, description="The slave language of the task")
    name: Optional[str] = Field(None, description="The name of the task")
    status: Optional[str] = Field(None, description="The status of the task")
    path: Optional[str] = Field(None, description="The file path associated with the task")