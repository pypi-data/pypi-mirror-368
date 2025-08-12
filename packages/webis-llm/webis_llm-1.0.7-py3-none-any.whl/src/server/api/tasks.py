from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import shutil
from pathlib import Path

from ..services.task_manager import TaskManager

router = APIRouter()
task_manager: TaskManager = None

def init_router(task_mgr: TaskManager):
    global task_manager
    task_manager = task_mgr

@router.get("/{task_id}")
def get_task_status(task_id: str):
    status = task_manager.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="任务不存在")
    return status

@router.get("/{task_id}/download")
def download_results(task_id: str):
    status = task_manager.get_task_status(task_id)
    if not status or status.status != "completed":
        raise HTTPException(status_code=404, detail="任务不存在或尚未完成")
    
    output_dir = Path(status.output_dir)
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="结果文件不存在")
    
    # 创建ZIP文件
    zip_path = task_manager.temp_dir / f"{task_id}_results.zip"
    shutil.make_archive(str(zip_path).replace('.zip', ''), 'zip', output_dir)
    
    return FileResponse(
        path=zip_path.with_suffix('.zip'),
        filename=f"{task_id}_results.zip",
        media_type="application/zip"
    )

@router.delete("/{task_id}")
def delete_task(task_id: str):
    if not task_manager.delete_task(task_id):
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"message": "任务及相关文件已删除"}
