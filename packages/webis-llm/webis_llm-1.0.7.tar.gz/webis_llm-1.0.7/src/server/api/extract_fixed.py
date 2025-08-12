from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from typing import List, Optional
from pathlib import Path
import time

from ..services.extractor import ContentExtractor
from ..services.task_manager import TaskManager
from ..models.schemas import ProcessResult

router = APIRouter()
extractor: ContentExtractor = None
task_manager: TaskManager = None

def init_router(content_extractor: ContentExtractor, task_mgr: TaskManager):
    global extractor, task_manager
    extractor = content_extractor
    task_manager = task_mgr

@router.post("/process-html")
async def process_html(
    files: List[UploadFile] = File(...),
    tag_probs: Optional[UploadFile] = None,
    model_type: str = Form("node")
):
    task_id = task_manager.create_task()
    input_dir, output_dir = task_manager.get_task_dirs(task_id)
    
    # 保存上传的文件
    for file in files:
        file_path = input_dir / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(await file.read())
    
    # 处理tag_probs
    tag_probs_path = None
    if tag_probs:
        tag_probs_path = output_dir / "tag_probs.json"
        with open(tag_probs_path, "wb") as f:
            f.write(await tag_probs.read())
    else:
        tag_probs_path = Path(__file__).resolve().parent.parent.parent.parent / 'config' / 'tag_probs.json'
    
    try:
        result = extractor.process_files(input_dir, output_dir, tag_probs_path, model_type)
        task_manager.update_task_status(task_id, **result.dict())
        
        return ProcessResult(
            task_id=task_id,
            status=result.status,
            result_count=len(result.results) if result.results else 0,
            message=result.message
        )
        
    except Exception as e:
        task_manager.update_task_status(task_id, status="failed", error=str(e), message="处理失败")
        return JSONResponse(
            status_code=500,
            content=ProcessResult(
                task_id=task_id,
                status="failed",
                message="处理失败",
                error=str(e)
            ).dict()
        )

@router.post("/process-async")
async def process_async(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    tag_probs: Optional[UploadFile] = None,
    model_type: str = Form("node")
):
    task_id = task_manager.create_task()
    input_dir, output_dir = task_manager.get_task_dirs(task_id)
    
    # 保存上传的文件
    for file in files:
        file_path = input_dir / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(await file.read())
    
    # 处理tag_probs
    tag_probs_path = None
    if tag_probs:
        tag_probs_path = output_dir / "tag_probs.json"
        with open(tag_probs_path, "wb") as f:
            f.write(await tag_probs.read())
    else:
        tag_probs_path = Path(__file__).resolve().parent.parent.parent.parent / 'config' / 'tag_probs.json'
    
    # 异步处理函数
    def process_task():
        try:
            result = extractor.process_files(input_dir, output_dir, tag_probs_path, model_type)
            task_manager.update_task_status(task_id, **result.dict())
        except Exception as e:
            task_manager.update_task_status(task_id, status="failed", error=str(e), message="处理失败")
    
    # 添加到后台任务
    background_tasks.add_task(process_task)
    
    return {"task_id": task_id, "status": "processing", "message": "任务已提交处理"}

@router.get("/fetch-url")
async def fetch_url(
    url: str,
    remove_scripts: bool = True,
    remove_images: bool = True
):
    if not url or not (url.startswith('http://') or url.startswith('https://')):
        raise HTTPException(
            status_code=400,
            detail="无效的URL，URL必须以http://或https://开头"
        )
    
    html_content, title, status_code = extractor.fetch_url(url)
    
    if html_content is None:
        raise HTTPException(
            status_code=status_code or 500,
            detail=f"获取URL内容失败: {url}"
        )
    
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/process-url")
async def process_url(url: str, model_type: str = "node"):
    if not url or not (url.startswith('http://') or url.startswith('https://')):
        raise HTTPException(
            status_code=400,
            detail="无效的URL，URL必须以http://或https://开头"
        )
    
    task_id = task_manager.create_task()
    input_dir, output_dir = task_manager.get_task_dirs(task_id)
    
    html_content, title, status_code = extractor.fetch_url(url)
    
    if html_content is None:
        raise HTTPException(
            status_code=status_code or 500,
            detail=f"获取URL内容失败: {url}"
        )
    
    # 保存HTML内容
    filename = f"url_content_{int(time.time())}.html"
    file_path = input_dir / filename
    
    if isinstance(html_content, bytes):
        with open(file_path, "wb") as f:
            f.write(html_content)
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
    
    # 使用默认的tag_probs文件
    tag_probs_path = Path(__file__).resolve().parent.parent.parent.parent / 'config' / 'tag_probs.json'
    
    task_manager.update_task_status(
        task_id,
        url=url,
        title=title
    )
    
    try:
        result = extractor.process_files(input_dir, output_dir, tag_probs_path, model_type)
        task_manager.update_task_status(task_id, **result.dict())
        
        return ProcessResult(
            task_id=task_id,
            status=result.status,
            result_count=len(result.results) if result.results else 0,
            message=result.message
        )
        
    except Exception as e:
        task_manager.update_task_status(task_id, status="failed", error=str(e), message="处理失败")
        return JSONResponse(
            status_code=500,
            content=ProcessResult(
                task_id=task_id,
                status="failed",
                message="处理失败",
                error=str(e)
            ).dict()
        )
