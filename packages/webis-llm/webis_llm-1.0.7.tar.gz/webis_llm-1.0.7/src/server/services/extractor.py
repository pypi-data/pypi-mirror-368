from pathlib import Path
from typing import Optional
from ..models.schemas import TaskStatus
from src.core.html_processor import HtmlProcessor
from src.core.dataset_processor import process_json_folder
from src.core.llm_predictor import process_predictions
from src.core.content_restorer import restore_text_from_json
from src.core.gpt_extaractor import process_all_html
from src.utils.url_fetcher import (
    UrlFetcher, 
    RENDER_METHOD_PLAYWRIGHT, 
    RENDER_METHOD_SELENIUM, 
    RENDER_METHOD_REQUESTS,
    has_playwright,
    has_selenium
)

class ContentExtractor:
    def __init__(self, deepseek_api_key: Optional[str] = None):
        self.deepseek_api_key = deepseek_api_key

    def process_files(self, input_dir: Path, output_dir: Path, tag_probs_path: Path, model_type: str = "node") -> TaskStatus:
        try:
            # 数据预处理
            processor = HtmlProcessor(input_dir, output_dir)
            processor.process_html_folder()
            
            # 数据集生成
            dataset_dir = output_dir / "dataset"
            dataset_dir.mkdir(exist_ok=True)
            process_json_folder(
                output_dir / "content_output",
                output_dir / "dataset" / "extra_datasets.json",
                tag_probs_path
            )
            
            # 模型预测
            process_predictions(
                output_dir / "dataset" / "extra_datasets.json",
                output_dir / "dataset" / "pred_results.json"
            )
            
            # 结果恢复
            predicted_dir = output_dir / "predicted_texts"
            predicted_dir.mkdir(exist_ok=True)
            restore_text_from_json(
                output_dir / "dataset" / "pred_results.json",
                predicted_dir
            )
            
            # DeepSeek提取
            if not self.deepseek_api_key:
                return TaskStatus(
                    status="failed",
                    error="未设置DEEPSEEK_API_KEY环境变量",
                    message="缺少DeepSeek API密钥"
                )
                
            deepseek_dir = output_dir / "deepseek_predicted_texts"
            deepseek_dir.mkdir(exist_ok=True)
            process_all_html(input_dir, deepseek_dir, self.deepseek_api_key)
                
            # 收集结果
            result_files = []
            for file in deepseek_dir.glob("*.txt"):
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                result_files.append({
                    "filename": file.name,
                    "content": content,
                    "source": "deepseek"
                })
            
            return TaskStatus(
                status="completed",
                output_dir=str(output_dir),
                results=result_files,
                message="处理完成"
            )
            
        except Exception as e:
            return TaskStatus(
                status="failed",
                error=str(e),
                message="处理失败"
            )

    def fetch_url(self, url: str) -> tuple[Optional[str], Optional[str], Optional[int]]:
        render_method = RENDER_METHOD_PLAYWRIGHT
        if not has_playwright and has_selenium:
            render_method = RENDER_METHOD_SELENIUM
        elif not has_playwright and not has_selenium:
            render_method = RENDER_METHOD_REQUESTS
        
        fetcher = UrlFetcher(render_method=render_method, wait_time=5)
        html_content, _, title, status_code = fetcher.fetch_url(url)
        
        return html_content, title, status_code
