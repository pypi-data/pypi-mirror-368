# Webis - HTML Content Extraction Tool  
![Python Version](https://img.shields.io/badge/Python-3.10-blue)  
![Bui1ld Status](https://img.shields.io/badge/Build-Passed-green)  

Webis is an intelligent web data extraction tool that uses AI technology to automatically identify valuable information on web pages, filter out noise, and provide high-quality input for downstream AI training and knowledge base construction.  

## Table of Contents  

- [Installation](#installation)  
- [Usage](#usage)  
  - [API Usage Example](#api-usage-example)  
  - [CLI Usage Example](#cli-usage-example)  
- [About the Model](#about-the-model)  
- [Project Structure](#project-structure)  
- [Troubleshooting](#troubleshooting)  
- [Contributing](#contributing)  

## Installation  

### Prerequisites  

- **Python 3.10**  
- **Conda** (recommended for environment management)  
- **NVIDIA GPU** (optional, for CUDA support)  

### Installing Webis
#### Method 1: Install via pip (Recommended)
```bash
conda create -n webis python=3.10 -y

conda activate webis

pip install webis-llm
```
#### Method 2: Install from Source
```bash
git clone https://github.com/TheBinKing/Webis.git  

cd Webis  

pip install -e .  

# Add the bin directory to PATH  
export PATH="$PATH:$(pwd)/bin"  
echo 'export PATH="$PATH:$(pwd)/bin"' >> ~/.bashrc  
source ~/.bashrc  
```

## Usage
Webis supports both CLI and API service modes. **Always start the model server first!**  

### Step 1: Start the Servers
+ **Model Server** (port 8000):  

```bash
python scripts/start_model_server.py  
```

+ **Web API Server** (port 8002):  

```bash
python scripts/start_web_server.py  
```

> **Note**: The default model (`Easonnoway/Web_info_extra_1.5b`) will be automatically downloaded from HuggingFace. The first run may take some time.  
>

### API Usage Example
The `api_usage.py` script demonstrates how to process HTML files via the API interface, supporting both synchronous and asynchronous modes, suitable for familiarizing clients with operations.  

#### Synchronous Processing Mode
Ideal for small numbers of files, where the client waits for the server to complete processing:  

```python
# Send an HTML file for synchronous processing  
response = requests.post(  
    "http://localhost:8002/extract/process-html",  
    files=files,  
    data=data  
)  

# Download the processed results  
response = requests.get(f"http://localhost:8002/tasks/{task_id}/download", stream=True)  
```

#### Asynchronous Processing Mode
Ideal for large numbers of files or long processing times; submit the task and periodically check its status:  

```python
# Submit an asynchronous processing task  
response = requests.post(  
    "http://localhost:8002/extract/process-async",  
    files=files,  
    data=data  
)  

# Monitor task status  
response = requests.get(f"http://localhost:8002/tasks/{async_task_id}")  

# Download results after task completion  
download_response = requests.get(f"http://localhost:8002/tasks/{async_task_id}/download", stream=True)  
```

#### Running the API Example
```bash
# Basic usage  
python samples/api_usage.py  

# Enhance processing results using the DeepSeek API (requires an API key)  
python samples/api_usage.py --use-deepseek --api-key YOUR_API_KEY_HERE  
```

> **Tip**: Ensure there are HTML files in the `input_html/` directory. Results will be saved as `{task_id}_results.zip` (synchronous) and `{async_task_id}_async_results.zip` (asynchronous).  
>

### CLI Usage Example
The `cli_usage.sh` script provides quick examples of command-line interface usage, suitable for batch processing or script integration.  

#### Basic Usage
```bash
# Process HTML files  
./samples/cli_usage.sh  
```

> **Note**: The script calls the `webis extract` command and requires a valid `YOUR_API_KEY_HERE`. Results are saved to the `output_basic/` directory.  
>

#### Other Commands
```bash
# View version information  
$PROJECT_ROOT/bin/webis version  

# Check API connection  
$PROJECT_ROOT/bin/webis check-api --api-key YOUR_API_KEY  

# View help  
$PROJECT_ROOT/bin/webis --help  
$PROJECT_ROOT/bin/webis extract --help  
```

## About the Model
### Model Details
+ **Name**: Web_info_extra_1.5b  
+ **HuggingFace**: [Easonnoway/Web_info_extra_1.5b](https://huggingface.co/Easonnoway/Web_info_extra_1.5b)  
+ **Parameters**: 1.5B  
+ **Function**: DOM tree node classification

### Usage Instructions
+ Downloaded by default to `~/.cache/huggingface/hub`.  
+ Use `--model-path` to specify a local path.  
+ Cache management: Set `HF_HOME` or `TRANSFORMERS_CACHE` to customize the location; use `huggingface-cli delete-cache` to clear the cache.

## Project Structure
+ `bin/` - Command-line tools  
+ `src/` - Source code  
    - `cli/` - CLI implementation  
    - `core/` - Core logic  
    - `server/` - API server
+ `scripts/` - Startup scripts  
+ `samples/` - Usage examples (including `api_usage.py` and `cli_usage.sh`)  
    - `input_html/` - Sample HTML files  
    - `output_basic/` - CLI output results
+ `config/` - Configuration files

## Contributing
Contributions are welcome! Please submit issues or pull requests on [GitHub](https://github.com/TheBinKing/Webis). For support, contact the maintainers or join the community discussion.  
