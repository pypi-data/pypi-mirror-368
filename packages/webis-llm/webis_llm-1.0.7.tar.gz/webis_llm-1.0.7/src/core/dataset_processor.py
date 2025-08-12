import json
import os
import re

risk_thresholds = {
    'H': 0.7,
    'M': 0.3,
    'L': 0.3   
}

tag_pattern = re.compile(r"<([a-zA-Z0-9_.]+)(?:\s|>)")
depth_pattern = re.compile(r"<([^>]+)")

tag_pattern = re.compile(r"<([a-zA-Z0-9_.]+)(?:\s|>)")
depth_pattern = re.compile(r"<([^>]+)")

def _get_last_tag(tags,tag_probs):
    if not tags:
        return None
    last_tag = tags[-1]
    return {
        "tag": last_tag,
        "probability": tag_probs.get(last_tag, {}).get('probability', 0.5),
        "risk_level": _get_risk_level(last_tag,tag_probs)
    }

def analyze_html(html,tag_probs):
    tags = _parse_tags(html)
    return {
        "content": _clean_content(html),
        "last_tag": _get_last_tag(tags,tag_probs),
        "risk_tags": _detect_risk_tags(tags,tag_probs),
        "depth": _calculate_depth(html),
        "confidence": _calculate_confidence(tags, _calculate_depth(html),tag_probs)
    }

def _get_risk_level(tag,tag_probs):
    prob = tag_probs.get(tag, {}).get('probability', 0.5)
    
    if prob >= risk_thresholds['H']:
        return 'H'
    elif prob >= risk_thresholds['L']:
        return 'M'
    elif prob < risk_thresholds['L']:
        return 'L'

def _parse_tags(html):
    return [tag.lower() for tag in tag_pattern.findall(html)]

def _clean_content(html):
    text = re.sub(r'<[^>]+>', '', html)
    return text.replace('<>', '').strip()[:100]

def _detect_risk_tags(tags,tag_probs):
    risk_tags = []
    for tag in set(tags):
        prob = tag_probs.get(tag, {}).get('probability', 0.5)
        level = _get_risk_level(tag,tag_probs)
        if level in ['H', 'L']:
            risk_tags.append({
                "tag": tag,
                "probability": prob,
                "risk_level": level
            })
    return sorted(risk_tags, key=lambda x: x['probability'], reverse=True)

def _calculate_depth(html):
    depth_pattern = re.compile(r'<[^/][^>]*>')
    return len(depth_pattern.findall(html))

def _calculate_confidence(tags, depth,tag_probs):
    WEIGHT_CONFIG = {
        'last_tag': {'H': 0.5, 'M': 0.3, 'L': 0.5},
        'other_risk': 0.4,
        'depth_base': 0.05,
        'depth_decay': 0.8,
        'single_tag_penalty': 0.5,
        'diversity_penalty': 0.1
    }

    total_weight = 0.0
    weighted_sum = 0.0
    risk_levels = set()
    num_risk_tags = 0

    last_tag_info = _get_last_tag(tags,tag_probs)
    if last_tag_info and last_tag_info.get('risk_level'):
        level = last_tag_info['risk_level']
        weight = WEIGHT_CONFIG['last_tag'].get(level, 0)
        if weight > 0:
            contribution = last_tag_info['probability'] * weight
            weighted_sum += contribution
            total_weight += weight
            risk_levels.add(level)
            num_risk_tags += 1

    other_risk_processed = 0
    for tag_info in _detect_risk_tags(tags,tag_probs):
        if tag_info['tag'] == tags[-1]:
            continue
        contribution = tag_info['probability'] * WEIGHT_CONFIG['other_risk']
        weighted_sum += contribution
        total_weight += WEIGHT_CONFIG['other_risk']
        other_risk_processed += 1
        if tag_info.get('risk_level'):
            risk_levels.add(tag_info['risk_level'])
    
    num_risk_tags += other_risk_processed

    effective_depth = min(depth, 50)
    depth_impact = WEIGHT_CONFIG['depth_base'] * (
        WEIGHT_CONFIG['depth_decay'] ** (effective_depth/5))
    weighted_sum += depth_impact
    total_weight += WEIGHT_CONFIG['depth_base']

    if num_risk_tags == 1:
        penalty = WEIGHT_CONFIG['single_tag_penalty']
        weighted_sum += 0.5 * penalty
        total_weight += penalty

    if len(risk_levels) == 2:
        diversity_penalty = WEIGHT_CONFIG['diversity_penalty']
        weighted_sum += 0.5 * diversity_penalty
        total_weight += diversity_penalty

    if total_weight == 0:
        return 0.5

    final_confidence = weighted_sum / total_weight
    return min(max(round(final_confidence, 2), 0.0), 1.0)

def format_features(features):
    components = [
        f"content: '{features['content']}'",
        f"last_tag: <{features['last_tag']['tag']}>[{features['last_tag']['risk_level']}]",
        f"risk_tags: {', '.join([f'''{rt['tag']}[{rt['risk_level']}]''' for rt in features['risk_tags']])}",
        f"depth: {features['depth']}",
        f"confidence: {features['confidence']:.2f}"
    ]
    return " | ".join(components)

def path_to_html(text,path):
    tags = path.split(' > ')
    html_structure = "<><html><body>"
    
    for tag in tags[2:]:
        tag_name = tag.split('[')[0]
        html_structure += f"<{tag_name}>"
    
    html_structure += text
    
    for tag in reversed(tags[2:]):
        tag_name = tag.split('[')[0]
        html_structure += f"</{tag_name}>"
    
    html_structure += "</body></html></>"
    return html_structure

def process_json_folder(folder_path: str, output_json_path: str,tag_probs_path: str):
    output_dir = os.path.dirname(output_json_path)
    os.makedirs(output_dir, exist_ok=True)
    with open(tag_probs_path, 'r', encoding='utf-8') as f:
        tag_probs = json.load(f)
    result = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            full_path = os.path.join(folder_path, file_name)
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            text_paths = data.get("text_paths", {})
            entries = []
            for text_key, path_val in text_paths.items():
                features = analyze_html(path_to_html(text_key,path_val),tag_probs)
                entries.append({
                    "text": text_key,
                    "path": path_val,
                    "input": format_features(features)
                })
            result[file_name] = entries
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

def main():
    folder_path = r"F:\deepLearning\llm_color\html_test\test_output2"
    input_path = os.path.join(folder_path, "content_output")
    output_json_path = os.path.join(folder_path, "dataset", "extra_datasets.json")
    tag_probs_path = r"F:\deepLearning\llm_color\config\tag_probs.json"
    process_json_folder(input_path, output_json_path, tag_probs_path)

if __name__ == "__main__":
    main()