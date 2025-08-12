import json
import re
from collections import defaultdict

class TreeNode:
    def __init__(self, name, index=None):
        self.name = name
        self.index = index
        self.is_noise = False
        self.noise_count = 0
        self.total_count = 0
        self.text = ""
        self.children = {}

    def add_child(self, name, index):
        key = (name, index)
        if key not in self.children:
            self.children[key] = TreeNode(name, index)
        return self.children[key]

    def to_dict(self):
        return {
            "name": self.name + (f"[{self.index}]" if self.index is not None else ""),
            "is_noise": self.is_noise,
            "noise_count": self.noise_count,
            "total_count": self.total_count,
            "text": self.text,
            "children": {f"{k[0]}[{k[1]}]": v.to_dict() for k, v in self.children.items()}
        }

def insert_path(root, text, path, prediction):
    nodes = path.split(" > ")
    current = root
    for node in nodes:
        match = re.match(r"([^\[]+)\[(\d+)\]", node.strip())
        if match:
            name, index = match.groups()
            index = int(index)
            current = current.add_child(name, index)
    if prediction == 0:
        current.is_noise = True
    current.text = text

def count_noise_and_total(node):
    if not node.children:
        node.noise_count = 1 if node.is_noise else 0
        node.total_count = 1
        return node.noise_count, node.total_count
    
    total_noise = 0
    total_count = 0
    for child in node.children.values():
        child_noise, child_total = count_noise_and_total(child)
        total_noise += child_noise
        total_count += child_total
    
    node.noise_count = total_noise
    node.total_count = total_count
    return node.noise_count, node.total_count

def calculate_max_depth(node, depth=0):
    if not node.children:
        return depth
    return max(calculate_max_depth(child, depth + 1) for child in node.children.values())

def get_dynamic_threshold(current_depth, max_depth, baseline, increment):
    depth_ratio = current_depth / max_depth
    return baseline + increment * depth_ratio

def prune_tree_by_percentage(node, current_depth, max_depth):
    if not node.children:
        return node.is_noise
    
    prune_list = []
    for key, child in list(node.children.items()):
        if prune_tree_by_percentage(child, current_depth + 1, max_depth):
            prune_list.append(key)
    
    for key in prune_list:
        del node.children[key]
    
    threshold = get_dynamic_threshold(current_depth, max_depth, 1, 0)
    if node.total_count == 0:
        return False
    
    noise_ratio = node.noise_count / node.total_count
    return noise_ratio > threshold

def set_noise_false_recursively(node):
    node.is_noise = False
    for child in node.children.values():
        set_noise_false_recursively(child)
        
def color_tree_by_percentage(node, current_depth, max_depth):
    if not node.children:
        return
    
    for child in node.children.values():
        color_tree_by_percentage(child, current_depth + 1, max_depth)
    
    threshold = get_dynamic_threshold(current_depth, max_depth, 0, 0)
    if node.total_count == 0:
        return
    
    noise_ratio = node.noise_count / node.total_count
    
    if noise_ratio < threshold:
        for child in node.children.values():
            child.is_noise = False
            def clear_noise(node):
                node.is_noise = False
                for c in node.children.values():
                    clear_noise(c)
            clear_noise(child)
        
def extract_paths(node, path_prefix="[document][0]"):
    paths = {}
    if node.text:
        formatted_path = path_prefix
        paths[node.text] = formatted_path
    for key, child in node.children.items():
        name, index = key
        new_prefix = f"{path_prefix} > {name}[{index}]"
        paths.update(extract_paths(child, new_prefix))
    return paths

def preprocess_json_data(raw_data):
    path_counter = {}
    parent_registry = defaultdict(set)
    
    processed = {}
    for text, details in raw_data.items():
        original_path = details['path']
        nodes = original_path.split(" > ")
        parent_path = " > ".join(nodes[:-1]) if len(nodes)>1 else ""
        last_node = nodes[-1]
        
        match = re.match(r"([^\[]+)\[(\d+)\]", last_node)
        if not match:
            print(f"Skipping invalid end node format: {last_node}")
            continue
        node_name, node_index = match.groups()
        node_index = int(node_index)
        
        used_indices = parent_registry[parent_path]
        while f"{node_name}[{node_index}]" in used_indices:
            node_index += 1
        
        adjusted_node = f"{node_name}[{node_index}]"
        used_indices.add(adjusted_node)
        parent_registry[parent_path] = used_indices
        
        new_path = f"{parent_path} > {adjusted_node}" if parent_path else adjusted_node
        processed[text] = {
            'path': new_path,
            'prediction': details['prediction']
        }
        
    return processed

def process_tree(json_data):    
    json_data = preprocess_json_data(json_data)
    root = TreeNode('root')

    for text, details in json_data.items():
        insert_path(root, text, details['path'], details['prediction'])

    count_noise_and_total(root)

    max_depth = calculate_max_depth(root)
    print(f"Max Depth: {max_depth}")
        
    color_tree_by_percentage(root, current_depth=0, max_depth=max_depth)
    
    prune_tree_by_percentage(root, current_depth=0, max_depth=max_depth)

    extracted_paths = extract_paths(root)

    return extracted_paths

def main():
    data = """
    
    
    """
    json_data = json.loads(data)
    process_tree(json_data)
    
if __name__ == "__main__":
    main()
