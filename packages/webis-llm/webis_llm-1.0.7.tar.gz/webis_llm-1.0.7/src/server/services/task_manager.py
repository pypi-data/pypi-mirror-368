import uuid
from pathlib import Path
import shutil
from typing import Dict, Optional
from ..models.schemas import TaskStatus

class TaskManager:
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.tasks: Dict[str, TaskStatus] = {}
        self.temp_dir.mkdir(exist_ok=True)

    def create_task(self) -> str:
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = TaskStatus(
            status="processing",
            message="任务正在处理中"
        )
        return task_id

    def get_task_dirs(self, task_id: str) -> tuple[Path, Path]:
        input_dir = self.temp_dir / f"input_{task_id}"
        output_dir = self.temp_dir / f"output_{task_id}"
        input_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        return input_dir, output_dir

    def update_task_status(self, task_id: str, **kwargs):
        if task_id in self.tasks:
            current_status = self.tasks[task_id].dict()
            current_status.update(kwargs)
            self.tasks[task_id] = TaskStatus(**current_status)

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        return self.tasks.get(task_id)

    def delete_task(self, task_id: str) -> bool:
        if task_id not in self.tasks:
            return False

        input_dir, output_dir = self.get_task_dirs(task_id)
        
        if input_dir.exists():
            shutil.rmtree(input_dir)
        
        if output_dir.exists():
            shutil.rmtree(output_dir)
        
        zip_path = self.temp_dir / f"{task_id}_results.zip"
        if zip_path.with_suffix('.zip').exists():
            zip_path.with_suffix('.zip').unlink()
        
        del self.tasks[task_id]
        return True

    def clean_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        # TODO: 实现清理逻辑
