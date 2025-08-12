from fastapi import APIRouter
import subprocess
import sys

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "网页内容提取API服务正在运行"}

@router.get("/check-model-server")
def check_model_server():
    try:
        import requests
        # 检查模型服务器健康状态
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            return {"status": "online"}
        else:
            return {"status": "offline", "reason": f"Health check failed with status code {response.status_code}"}
    except Exception as e:
        return {"status": "offline", "reason": str(e)}

@router.get("/install-dependencies")
def install_dependencies():
    try:
        dependencies = [
            "fastapi",
            "uvicorn",
            "python-multipart",
            "aiofiles",
            "pydantic",
            "requests",
            "tqdm",
            "beautifulsoup4",
            "lxml",
            "vllm"
        ]
        
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade"] + dependencies
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return {
                "status": "failed",
                "message": "依赖安装失败",
                "error": result.stderr
            }
            
        return {
            "status": "success",
            "message": "所有依赖已安装成功",
            "details": dependencies
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": f"安装过程出错: {str(e)}"
        }

@router.get("/check-model-server")
def check_model_server():
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            return {
                "status": "online",
                "message": "模型服务器正在运行",
                "details": response.json()
            }
        else:
            return {
                "status": "error",
                "message": "模型服务器响应异常",
                "statusCode": response.status_code
            }
    except requests.exceptions.RequestException:
        return {
            "status": "offline",
            "message": "模型服务器未运行或无法连接",
            "hint": "请确保已启动了node_model_server.py"
        }
