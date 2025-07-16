from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ProjectCreate(BaseModel):
    project_name: str
    start_date: Optional[datetime] = None
    company_name: str
    timezone: Optional[str] = "Africa/Addis_Ababa"
    objectives: Optional[List[str]] = []
    project_type: Optional[str] = Field(
        default="scheduled",
        pattern="^(scheduled|documented)$"
    )

class TaskCreate(BaseModel):
    project_name: str
    task_name: str
    start_time: Optional[datetime] = None
    expected_duration: str
    priority: Optional[str] = "medium"
    members: Optional[List[str]] = []
    description: Optional[str] = None
    estimated_cost: Optional[float] = 0.0
    dependencies: Optional[List[str]] = []

class TaskUpdateCreate(BaseModel):
    project_name: str
    task_name: str   
    status_percentage: int = Field(ge=0, le=100)
    description: Optional[str] = None
    image_filename: Optional[str] = None
    
class BatchTaskCreate(BaseModel):
    tasks: List[TaskCreate]

    
class MarkAsRequest(BaseModel):
    project_name: str
    task_name: str
    status: str

class PostponeRequest(BaseModel):
    project_name: str
    task_name: str
    new_start_time: datetime
    new_duration: Optional[str] = None