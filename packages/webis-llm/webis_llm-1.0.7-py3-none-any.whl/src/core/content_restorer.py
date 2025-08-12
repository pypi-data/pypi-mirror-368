## Text restoration after pruning

import json
import os
from src.core.color_tree_new import process_tree

def path_to_tuple(path):
    """Convert DOM path to tuple"""
    return tuple(path.replace('[document][0] > ', '').split(' > '))

def sort_dom_paths(content_dict):
    """Sort content dict by DOM path"""
    return sorted(content_dict.items(), key=lambda item: path_to_tuple(item[1]))

def format_process(content_dict):
    """Format text content"""
    formatted_dict = {}
    for item in content_dict:
        text = item["text"]
        path = item["path"]
        prediction = item["prediction"]
        formatted_dict[text] = {
            "path": path,
            "prediction": prediction
        }
    return formatted_dict

def restore_text_from_json(json_file_path, output_dir):
    """Restore text from JSON and save in order"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print(f"Loaded JSON data from {json_file_path}")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for filename, content_dict in data.items():
            content_dict = process_tree(format_process(content_dict))
            sorted_content = sort_dom_paths(content_dict)

            combined_text = []
            for text, path in sorted_content:
                combined_text.append(text)

            base_name = filename.rsplit('_', 1)[0]
            txt_filename = os.path.join(output_dir, base_name + '.txt')
            with open(txt_filename, 'w', encoding='utf-8') as txt_file:
                txt_file.write('\n'.join(combined_text))

        print(f"Text files saved to {output_dir}")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    json_filter_file_path = r'F:\data\pred_results.json'
    output_dir = r'F:\data\new_find_sftllm_noColor_predicted_texts'
    restore_text_from_json(json_filter_file_path, output_dir)

if __name__ == "__main__":
    main()
