import json
import os
import sys
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from dotenv import load_dotenv

def extract_main_info(html_content, api_key):
    """
    提取网页的主要信息，使用DeepSeek API过滤掉网页噪音。

    :param html_content: 网页的HTML内容
    :param api_key: DeepSeek API密钥
    :return: 提取的主要信息
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    text = ' '.join(p.get_text() for p in soup.find_all('p'))

    # 使用DeepSeek API
    base_url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    model_name = "deepseek-ai/DeepSeek-V3"
    prompt = f"""
    Act as a prudent text refinement assistant. Carefully read the entire text to grasp its core themes and logical structure. Remove only obvious fragmentary noise elements such as advertising snippets, repetitive promotional phrases, and platform-generated system messages. Preserve all potentially meaningful content including examples, technical details, and domain-specific terminology. When in doubt about content relevance, prioritize retention over deletion. Return the refined text strictly following these rules:
    1.No explanations - Provide only the cleaned text without any analysis.
    2.​Format integrity - Strictly preserve the original formatting and syntactic flow.
    3.​Minimal intervention - Limit changes to unquestionably non-essential elements.Now, please analyze and filter the following text:'{text}''
    """

    data = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "max_tokens": 4096,
        "stop": None,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"}
    }

    try:
        response = requests.post(base_url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        main_info = result["choices"][0]["message"]["content"]
        return main_info
    except Exception as e:
        print(f"Error calling DeepSeek API: {e}")
        return text

def process_all_html(input_folder, output_folder, api_key):
    """
    处理文件夹中的所有HTML文件，提取主要信息，并将其保存为TXT文件。
    
    :param input_folder: 包含HTML文件的文件夹路径
    :param output_folder: 保存TXT文件的文件夹路径
    :param api_key: DeepSeek API密钥
    """
    # 确保输入输出路径是Path对象
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    
    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)

    processed_count = 0
    error_count = 0
    
    for file_path in input_folder.glob('**/*.html'):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                html_content = file.read()
            
            main_info = extract_main_info(html_content, api_key)
            
            # 保持相对路径结构
            rel_path = file_path.relative_to(input_folder)
            output_path = output_folder / f"{rel_path.stem}.txt"
            
            # 确保父目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(main_info)
                
            processed_count += 1
            if processed_count % 10 == 0:
                print(f"已处理: {processed_count}个文件")
                
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            error_count += 1
    
    print(f"处理完成。成功: {processed_count}个文件, 失败: {error_count}个文件")


# 加载环境变量的函数
def load_api_key_from_env():
    """从.env文件或环境变量中加载API密钥"""
    # 尝试加载.env文件（首先尝试当前目录，然后尝试项目根目录）
    dotenv_paths = [
        Path('.env'),  # 当前工作目录
        Path(__file__).resolve().parent.parent.parent / '.env'  # 项目根目录
    ]
    
    for path in dotenv_paths:
        if path.exists():
            load_dotenv(dotenv_path=path)
            break
    
    # 尝试获取API密钥
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    
    if not api_key or api_key == 'your_deepseek_api_key_here':
        return None
    
    return api_key

# 如果直接运行此脚本
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='使用DeepSeek提取网页主要内容')
    parser.add_argument('--input', '-i', required=True, help='HTML文件夹路径')
    parser.add_argument('--output', '-o', required=True, help='输出TXT文件夹路径')
    parser.add_argument('--api-key', '-k', default=None, help='DeepSeek API密钥（可选，默认从.env文件读取）')
    
    args = parser.parse_args()
    
    # 如果命令行未提供API密钥，则从环境变量获取
    api_key = args.api_key or load_api_key_from_env()
    
    if not api_key:
        print("错误：未提供DeepSeek API密钥，也未在环境变量中找到有效的密钥")
        print("请使用--api-key选项提供密钥，或在.env文件中设置DEEPSEEK_API_KEY")
        sys.exit(1)
    
    process_all_html(args.input, args.output, api_key)