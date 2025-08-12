from pydantic import BaseModel
from typing import List, Dict, Optional
from pathlib import Path

class TaskStatus(BaseModel):
    status: str
    message: str
    output_dir: Optional[str] = None
    results: Optional[List[Dict]] = None
    error: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None

class ProcessResult(BaseModel):
    task_id: str
    status: str
    result_count: Optional[int] = None
    message: str
    error: Optional[str] = None
