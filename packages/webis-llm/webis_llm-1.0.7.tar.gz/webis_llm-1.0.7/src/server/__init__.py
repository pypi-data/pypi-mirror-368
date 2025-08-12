#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import extract, tasks, utils
from .services.extractor import ContentExtractor
from .services.task_manager import TaskManager

def load_api_key():
    try:
        project_root = Path(__file__).resolve().parent.parent.parent
        api_keys_path = project_root / 'config' / 'api_keys.json'
        
        if api_keys_path.exists():
            with open(api_keys_path, 'r') as f:
                import json
                api_keys = json.load(f)
                api_key = api_keys.get('deepseek_api_key')
                if api_key and api_key != "your-api-key-here":
                    print(f"成功: 从配置文件 {api_keys_path} 读取到DeepSeek API密钥")
                    return api_key
                else:
                    print(f"警告: API密钥配置文件 {api_keys_path} 中的密钥无效或为默认值")
                    return None
        else:
            print(f"警告: API密钥配置文件不存在: {api_keys_path}")
            return None
    except Exception as e:
        print(f"读取API密钥文件时出错: {str(e)}")
        return None

def create_app():
    # 获取API密钥
    api_key = load_api_key()
    if not api_key:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if api_key:
            print("成功: 从环境变量DEEPSEEK_API_KEY读取到DeepSeek API密钥")
        else:
            print("警告: 未设置DeepSeek API密钥，DeepSeek功能将无法使用")
    
    # 创建FastAPI应用
    app = FastAPI(
        title="网页内容提取API",
        description="提供网页内容提取、数据集生成、模型预测、结果恢复和DeepSeek优化功能的API服务",
        version="1.0.0"
    )

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=86400,
    )

    # 创建临时目录
    temp_dir = Path("./temp_api_data")
    temp_dir.mkdir(exist_ok=True)

    # 初始化服务
    task_manager = TaskManager(temp_dir)
    content_extractor = ContentExtractor(api_key)

    # 初始化路由
    extract.init_router(content_extractor, task_manager)
    tasks.init_router(task_manager)

    # 注册路由
    app.include_router(utils.router, tags=["utils"])
    app.include_router(extract.router, prefix="/extract", tags=["extract"])
    app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

    return app

def main():
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        limit_concurrency=100,
        limit_max_requests=10000,
    )

if __name__ == "__main__":
    main()
