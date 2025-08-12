import click
from pathlib import Path
import os
import sys
from tqdm import tqdm
import time
from dotenv import load_dotenv
import subprocess
import webbrowser

# 添加core目录到Python路径
current_dir = Path(__file__).resolve().parent
core_dir = current_dir.parent / "core"
sys.path.insert(0, str(core_dir))

# 现在可以导入core模块
from html_processor import HtmlProcessor
from dataset_processor import process_json_folder
from llm_predictor import process_predictions
from content_restorer import restore_text_from_json
from gpt_extaractor import process_all_html


# CLI主命令组
@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli_app():
    """
    Webis内容提取工具 - 从HTML文件中提取和清洗有价值的内容

    这个工具可以处理HTML文件，提取有价值的内容，过滤掉无关的噪声文本，
    并可以使用DeepSeek API进行额外的优化。

    使用示例:

      # 基本用法，处理input_folder中的HTML文件
      webis extract --input ./input_folder

      # 使用DeepSeek API进行优化
      webis extract --input ./input_folder --use-deepseek --api-key YOUR_API_KEY

      # 指定输出目录和标签概率文件
      webis extract --input ./input_folder --output ./results --tag-probs ./my_tags.json
    """
    pass


# 加载环境变量中的API密钥
def load_env_api_key():
    """从.env文件或环境变量中加载DeepSeek API密钥"""
    # 尝试加载.env文件
    # 首先尝试当前工作目录
    if Path(".env").exists():
        load_dotenv()
    else:
        # 然后尝试项目根目录
        dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
        if dotenv_path.exists():
            load_dotenv(dotenv_path=dotenv_path)

    # 尝试获取API密钥
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if api_key and api_key != "your_deepseek_api_key_here":
        return api_key
    return None


@cli_app.command("extract")
@click.option("--input", "-i", required=True, help="包含HTML文件的输入目录路径")
@click.option("--output", "-o", default="./output", help="处理结果的输出目录路径")
@click.option("--tag-probs", "-t", default=None, help="HTML标签概率配置文件的路径")
@click.option(
    "--api-key",
    "-k",
    default=None,
    help="用于内容优化的DeepSeek API密钥（可选，默认从.env文件读取）",
)
@click.option(
    "--use-deepseek", "-d", is_flag=True, help="是否使用DeepSeek API进行最终内容优化"
)
@click.option("--verbose", "-v", is_flag=True, help="显示详细的处理进度和信息")
def extract(input, output, tag_probs, api_key, use_deepseek, verbose):
    """从HTML文件中提取和清洗有价值的内容"""
    start_time = time.time()
    input_path = Path(input)
    output_path = Path(output)

    # 检查输入目录是否存在
    if not input_path.exists():
        click.secho(f"错误: 输入目录 '{input_path}' 不存在", fg="red")
        return

    # 检查是否有HTML文件
    html_files = list(input_path.glob("**/*.html"))
    if not html_files:
        click.secho(f"警告: 在输入目录中没有找到HTML文件", fg="yellow")
        return

    click.secho(f"找到 {len(html_files)} 个HTML文件", fg="green")

    # 如果没有指定tag_probs，则使用默认值
    if tag_probs is None:
        # 尝试多个位置查找配置文件
        possible_paths = [
            # 1. 当前工作目录下的 config 目录
            Path.cwd() / "config" / "tag_probs.json",
            # 2. 项目根目录（开发环境）
            Path(__file__).resolve().parent.parent.parent / "config" / "tag_probs.json",
            # 3. 包安装目录
            Path(__file__).resolve().parent.parent / "config" / "tag_probs.json",
        ]

        for path in possible_paths:
            if path.exists():
                tag_probs = path
                if verbose:
                    click.echo(f"使用配置文件: {tag_probs}")
                break
        else:
            click.secho(
                f"错误: 未找到标签概率文件。请使用 --tag-probs 参数指定文件路径",
                fg="red",
            )
            if verbose:
                click.echo("尝试过以下路径:")
                for path in possible_paths:
                    click.echo(f"- {path}")
            return

    # 确保输出目录存在
    output_path.mkdir(parents=True, exist_ok=True)

    # 数据预处理
    click.echo("步骤 1/4: HTML预处理...")
    processor = HtmlProcessor(input_path, output_path)
    processor.process_html_folder()

    # 数据集生成
    click.echo("步骤 2/4: 生成数据集...")
    dataset_output = output_path / "dataset"
    dataset_output.mkdir(parents=True, exist_ok=True)
    process_json_folder(
        output_path / "content_output",
        dataset_output / "extra_datasets.json",
        tag_probs,
    )

    # 模型预测
    click.echo("步骤 3/4: 执行模型预测...")
    process_predictions(
        dataset_output / "extra_datasets.json", dataset_output / "pred_results.json"
    )

    # 结果恢复
    click.echo("步骤 4/4: 恢复处理文本...")
    predicted_texts_dir = output_path / "predicted_texts"
    predicted_texts_dir.mkdir(parents=True, exist_ok=True)
    restore_text_from_json(dataset_output / "pred_results.json", predicted_texts_dir)
    click.secho(
        f"节点及局部处理处理完成! 结果保存在: {predicted_texts_dir}", fg="green"
    )

    # DeepSeek提取（如果启用）
    if use_deepseek:
        # 如果命令行未提供API密钥，尝试从环境变量获取
        if api_key is None:
            api_key = load_env_api_key()
            if api_key and verbose:
                click.secho(f"使用环境变量中的DeepSeek API密钥", fg="blue")

        # 检查最终是否有有效的API密钥
        if api_key is None:
            click.secho("错误: 使用DeepSeek提取功能需要提供API密钥", fg="red")
            click.echo("可以通过以下方式提供API密钥:")
            click.echo("1. 使用命令行参数 --api-key")
            click.echo("2. 在.env文件中设置 DEEPSEEK_API_KEY")
            click.echo("3. 设置环境变量 DEEPSEEK_API_KEY")
            return

        click.secho("正在进行大模型清洗...", fg="blue")
        deepseek_output_path = output_path / "deepseek_predicted_texts"
        deepseek_output_path.mkdir(parents=True, exist_ok=True)

        with tqdm(total=len(html_files), desc="优化文件") as pbar:

            def progress_callback(completed, total):
                pbar.update(1)

            process_all_html(input_path, deepseek_output_path, api_key)

        click.secho(f"DeepSeek优化完成! 结果保存在: {deepseek_output_path}", fg="green")

    # 显示处理统计信息
    elapsed_time = time.time() - start_time
    click.echo(f"\n处理统计:")
    click.echo(f"- 处理的HTML文件数量: {len(html_files)}")
    click.echo(f"- 总处理时间: {elapsed_time:.2f} 秒")
    if use_deepseek:
        deepseek_files = list(deepseek_output_path.glob("*.txt"))
        click.echo(f"- DeepSeek优化后的文件数量: {len(deepseek_files)}")

    click.secho("\n处理完成!", fg="green", bold=True)


# 添加其他实用命令


@cli_app.command("version")
def version():
    """显示版本信息"""
    try:
        import tomli

        pyproject_path = (
            Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
        )
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                pyproject = tomli.load(f)
                version = pyproject.get("project", {}).get("version", "未知")
        else:
            version = "未知"
    except Exception:
        version = "未知"

    click.echo(f"Webis内容提取工具 v{version}")
    click.echo("© 2025 Webis团队")


@cli_app.command("check-api")
@click.option("--api-key", "-k", required=True, help="DeepSeek API密钥")
def check_api(api_key):
    """测试DeepSeek API连接状态"""
    click.echo("正在检查DeepSeek API连接...")
    try:
        # 导入requests以检查连接
        import requests

        url = "https://api.siliconflow.cn/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        # 发送一个简单请求测试API
        data = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 5,
        }

        response = requests.post(url, headers=headers, json=data, timeout=10)

        if response.status_code == 200:
            click.secho("✓ API连接正常!", fg="green")
        else:
            click.secho(f"× API连接失败: 状态码 {response.status_code}", fg="red")
            click.echo(f"响应: {response.text}")

    except Exception as e:
        click.secho(f"× API连接错误: {str(e)}", fg="red")


@cli_app.command("gui")
def gui():
    """启动Webis可视化界面服务器"""
    import http.server
    import socketserver
    import socket
    from functools import partial

    # 获取前端目录路径
    # 首先尝试从项目目录寻找
    frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"

    # 如果项目目录不存在，则检查包安装路径
    if not frontend_dir.exists():
        import site

        site_packages = site.getsitepackages()[0]
        frontend_dir = Path(site_packages) / "frontend"

    # 检查前端目录是否存在
    if not frontend_dir.exists():
        click.secho(f"错误: 前端目录不存在: {frontend_dir}", fg="red")
        return

    # 检查index.html是否存在
    if not (frontend_dir / "index.html").exists():
        click.secho(f"错误: index.html不存在: {frontend_dir / 'index.html'}", fg="red")
        return

    # 设置端口（默认8080，如果被占用则尝试其他端口）
    port = 8001
    while port < 8021:  # 尝试20个端口
        try:
            # 创建自定义的请求处理器
            class Handler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=str(frontend_dir), **kwargs)

                def end_headers(self):
                    # 添加CORS头
                    self.send_header("Access-Control-Allow-Origin", "*")
                    super().end_headers()

                def log_message(self, format, *args):
                    # 打印请求日志
                    click.echo(f"[{self.log_date_time_string()}] {format % args}")

                def do_GET(self):
                    # 如果请求根路径，确保返回 index.html
                    if self.path == "/":
                        self.path = "/index.html"
                    elif not Path(frontend_dir / self.path.lstrip("/")).exists():
                        # 如果文件不存在，返回 index.html（用于处理前端路由）
                        self.path = "/index.html"
                    return super().do_GET()

            # 创建服务器
            with socketserver.TCPServer(("", port), Handler) as httpd:
                url = f"http://localhost:{port}/"
                click.echo(f"启动服务器于: {url}")
                click.echo("按 Ctrl+C 停止服务器")

                # 在浏览器中打开
                webbrowser.open(url)

                # 启动服务器
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    click.echo("\n正在关闭服务器...")
                    httpd.shutdown()
                    httpd.server_close()
                    click.echo("服务器已关闭")
            break
        except socket.error:
            port += 1
    else:
        click.secho(f"错误: 无法找到可用端口（尝试了8001-8021）", fg="red")


if __name__ == "__main__":
    cli_app()
