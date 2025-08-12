import json
import os
import requests
from tqdm import tqdm

def call_llm_api(text_input: str) -> str:
    return call_node_model_api(text_input)

def call_node_model_api(text_input: str) -> str:
    url = "http://localhost:8000/generate"
    headers = {
        "Content-Type": "application/json"
    }
    prompt_content = f"Perform three-step noise detection:1.Content analysis (whether it is irrelevant text),2.Tag risk analysis (last_tag and risk_tags),3.Structural verification (depth and confidence),Only return 0 or 1. : \n{text_input}"
    payload = {
        "prompt": prompt_content,
        "max_tokens": 10,
        "temperature": 0.1,
        "top_p": 0.9,
        "top_k": 50,
        "n": 1
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        resp_json = response.json()
        if "text" in resp_json and resp_json["text"]:
            result_text = resp_json["text"][0].strip()
            for char in result_text:
                if char in ["0", "1"]:
                    return int(char)
            print(f"Invalid response format: {result_text}")
            return "error"
        else:
            print(f"Invalid response format: {resp_json}")
            return "error"
    except requests.RequestException as e:
        print(f"API request error: {e}")
        return "error"
    except (ValueError, KeyError) as e:
        print(f"Error parsing response: {e}")
        return "error"

def process_predictions(input_json_path: str, output_json_path: str):
    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if os.path.exists(output_json_path):
        with open(output_json_path, "r", encoding="utf-8") as f:
            results = json.load(f)
    else:
        results = {}
    for file_name, entries in tqdm(data.items(), desc="Processing files"):
        if file_name in results:
            print(f"Skipping {file_name} as it has already been processed.")
            continue
        updated_entries = []
        for item in tqdm(entries, desc=f"Processing entries in {file_name}", leave=False):
            content_input = item.get("input", "")
            text = item.get("text", "")
            path = item.get("path", "")
            llm_result = call_llm_api(content_input)
            updated_entries.append({
                "text": text,
                "path": path,
                "prediction": llm_result
            })
        results[file_name] = updated_entries
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

def main():
    folder_path = r"/data0/ziyan_full/llm_extra/webflow_github/Webis/samples/output_basic"
    input_json = os.path.join(folder_path, "dataset","extra_datasets.json")
    output_json = os.path.join(folder_path,"dataset","pred_results.json")
    process_predictions(input_json, output_json)

if __name__ == "__main__":
    main()