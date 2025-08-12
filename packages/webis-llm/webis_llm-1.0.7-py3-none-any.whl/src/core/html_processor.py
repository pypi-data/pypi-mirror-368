import os
import json
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup, Comment, Doctype, NavigableString
import nltk

nltk_data_path = os.path.join(Path(__file__).resolve().parent.parent / 'config'/ "nltk_data")
nltk.data.path.append(nltk_data_path)

class HtmlProcessor:
    def __init__(self, input_folder_path, project_data_folder):
        self.input_folder_path = input_folder_path
        self.content_output_folder = os.path.join(project_data_folder, "content_output")

        os.makedirs(self.content_output_folder, exist_ok=True)

    @staticmethod
    def normalize_text(text):
        return ' '.join(text.split()).lower()

    def traverse_dom_tree(self, node, text_paths, base_path='[document][0]'):
        if isinstance(node, (Doctype, Comment)):
            return

        if isinstance(node, NavigableString):
            parent = node.parent
            if parent and parent.name not in ['script', 'style', 'meta', 'noscript', 'head']:
                text = node.strip()
                if text and not text.startswith('<!--'):
                    path = []
                    current_node = parent
                    valid_structure = True
                    
                    while current_node and current_node.name:
                        if current_node.name in ['meta', 'link']:
                            valid_structure = False
                            break
                        parent_index = self.get_node_index(current_node)
                        path.insert(0, f"{current_node.name}[{parent_index}]")
                        current_node = current_node.parent
                    
                    if valid_structure and path:
                        path_str = ' > '.join(path)
                        if text not in text_paths or path_str not in text_paths.values():
                            text_paths[text] = path_str
            return

        if node.name in ['script', 'style', 'meta', 'noscript', 'head']:
            return

        for child in node.children:
            self.traverse_dom_tree(child, text_paths, base_path)

    @staticmethod
    def get_node_index(node):
        if node.parent:
            return list(filter(lambda x: not isinstance(x, NavigableString), node.parent.children)).index(node)
        return 0

    @staticmethod
    def get_all_texts(node):
        texts = []
        if isinstance(node, NavigableString):
            texts.append(node.strip())
        elif node.name is not None:
            for child in node.children:
                texts.extend(HtmlProcessor.get_all_texts(child))
        return texts

    def parse_path_string(self, path):
        parts = path.replace('[document] > ', '').split(' > ')
        parsed = []
        for part in parts:
            if '[' in part and ']' in part:
                tag, index = part.rsplit('[', 1)
                index = int(index[:-1])
            else:
                tag, index = part, 0
            parsed.append((tag, index))
        return parsed

    def extract_and_save_content(self, soup, filename):
        try:
            text_paths = {}
            self.traverse_dom_tree(soup, text_paths)
            
            sorted_text_paths = dict(sorted(text_paths.items(), key=lambda item: self.parse_path_string(item[1])))

            result_data = {
                "title": None,
                "meta_description": None,
                "text_paths": sorted_text_paths,
                "top_image": None
            }
            
            content_path = os.path.join(self.content_output_folder, f"{filename}.json")
            with open(content_path, "w", encoding="utf-8") as file:
                json.dump(result_data, file, ensure_ascii=False, indent=4)

            print(f"{filename} has been saved to the output folder")
        except Exception as e:
            print(f"Failed to extract content. Error: {e}")
            
    def process_html_file(self, html_file_path):
        try:
            try:
                with open(html_file_path, 'r', encoding='utf-8') as file:
                    html_content = file.read()
            except UnicodeDecodeError:
                with open(html_file_path, 'rb') as file:
                    html_content_bytes = file.read()
                
                try:
                    import chardet
                    detected = chardet.detect(html_content_bytes)
                    if detected['encoding']:
                        html_content = html_content_bytes.decode(detected['encoding'], errors='replace')
                    else:
                        html_content = html_content_bytes.decode('utf-8', errors='replace')
                except ImportError:
                    html_content = html_content_bytes.decode('utf-8', errors='replace')
            
            url_hash = hashlib.md5(html_content.encode('utf-8')).hexdigest()
            base_filename = os.path.splitext(os.path.basename(html_file_path))[0]
            output_filename = f"{base_filename}_{url_hash}"
            
            soup = BeautifulSoup(html_content, 'html.parser')

            self.extract_and_save_content(soup, output_filename)
        except Exception as e:
            print(f"Failed to process HTML file {html_file_path}. Error: {e}")
            
    def process_html_folder(self):
        for filename in os.listdir(self.input_folder_path):
            if filename.endswith(".html"):
                html_file_path = os.path.join(self.input_folder_path, filename)
                self.process_html_file(html_file_path)

if __name__ == "__main__":
    input_folder_path = r"F:\data\html"
    project_data_folder = r"F:\data\output"
    
    processor = HtmlProcessor(input_folder_path, project_data_folder)
    processor.process_html_folder()