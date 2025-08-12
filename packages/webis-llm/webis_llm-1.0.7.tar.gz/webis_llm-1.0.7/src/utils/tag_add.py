## Detect risk tags and calculate confidence scores for HTML datasets based on tag probability data, output enhanced dataset
import re
import json
import os
import math
from collections import defaultdict

class AutoRiskClassifier:
    def __init__(self, tag_probs_path):
        with open(tag_probs_path, 'r', encoding='utf-8') as f:
            self.tag_probs = json.load(f)
        
        # Modified risk level thresholds
        self.risk_thresholds = {
            'H': 0.7,  # High noise probability tags (≥0.7)
            'M': 0.3,  # Medium noise probability tags (0.3~0.7)
            'L': 0.3   # Low noise probability tags (<0.3)
        }
        
        # Regular expressions
        self.tag_pattern = re.compile(r"<([a-zA-Z0-9_.]+)(?:\s|>)")
        self.depth_pattern = re.compile(r"<([^>]+)")
        
        # Regular expressions
        self.tag_pattern = re.compile(r"<([a-zA-Z0-9_.]+)(?:\s|>)")
        self.depth_pattern = re.compile(r"<([^>]+)")

    def process_dataset(self, input_path, output_path):
        """Process dataset main flow"""
        with open(input_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)

        processed = []
        for item in dataset:
            features = self.analyze_html(item['input'])
            formatted_input = self.format_features(features)
            processed.append({
                "instruction": item["instruction"],
                "input": formatted_input,
                "output": item["output"]
            })

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed, f, ensure_ascii=False, indent=2)

    def analyze_html(self, html):
        """Parse HTML and extract features"""
        tags = self._parse_tags(html)
        return {
            "content": self._clean_content(html),
            "last_tag": self._get_last_tag(tags),
            "risk_tags": self._detect_risk_tags(tags),
            "depth": self._calculate_depth(html),
            "confidence": self._calculate_confidence(tags, self._calculate_depth(html))
        }

    def _parse_tags(self, html):
        """Parse all HTML tags"""
        return [tag.lower() for tag in self.tag_pattern.findall(html)]

    def _calculate_depth(self, html):
        """Calculate nesting depth"""
        return len(self.depth_pattern.findall(html))

    def _clean_content(self, html):
        """Clean text content"""
        text = re.sub(r'<[^>]+>', '', html)
        return text.replace('<>', '').strip()[:100]  # Limit length

    def _get_last_tag(self, tags):
        """Get details of the last tag"""
        if not tags:
            return None
        last_tag = tags[-1]
        return {
            "tag": last_tag,
            "probability": self.tag_probs.get(last_tag, {}).get('probability', 0.5),
            "risk_level": self._get_risk_level(last_tag)
        }

    def _detect_risk_tags(self, tags):
        """Risk tag detection (exclude M tags)"""
        risk_tags = []
        for tag in set(tags):
            prob = self.tag_probs.get(tag, {}).get('probability', 0.5)
            level = self._get_risk_level(tag)
            # Only keep H and L tags
            if level in ['H', 'L']:
                risk_tags.append({
                    "tag": tag,
                    "probability": prob,
                    "risk_level": level
                })
        return sorted(risk_tags, key=lambda x: x['probability'], reverse=True)

    def _get_risk_level(self, tag):
        """Modified risk level determination logic"""
        prob = self.tag_probs.get(tag, {}).get('probability', 0.5)
        
        if prob >= self.risk_thresholds['H']:
            return 'H'
        elif prob >= self.risk_thresholds['L']:
            return 'M'
        elif prob < self.risk_thresholds['L']:
            return 'L'

    def _calculate_confidence(self, tags, depth):
        """Optimized confidence calculation with tag count and diversity factors"""
        WEIGHT_CONFIG = {
            'last_tag': {'H': 0.5, 'M': 0.3, 'L': 0.5},
            'other_risk': 0.4,
            'depth_base': 0.05,
            'depth_decay': 0.8,
            'single_tag_penalty': 0.5,    # Single tag penalty weight
            'diversity_penalty': 0.1      # Diversity penalty weight
        }

        total_weight = 0.0
        weighted_sum = 0.0
        risk_levels = set()
        num_risk_tags = 0

        # Process last tag
        last_tag_info = self._get_last_tag(tags)
        if last_tag_info and last_tag_info.get('risk_level'):
            level = last_tag_info['risk_level']
            weight = WEIGHT_CONFIG['last_tag'].get(level, 0)
            if weight > 0:
                contribution = last_tag_info['probability'] * weight
                weighted_sum += contribution
                total_weight += weight
                risk_levels.add(level)
                num_risk_tags += 1

        # Process other risk tags
        other_risk_processed = 0
        for tag_info in self._detect_risk_tags(tags):
            if tag_info['tag'] == tags[-1]:
                continue
            # Add contribution of other risk tags
            contribution = tag_info['probability'] * WEIGHT_CONFIG['other_risk']
            weighted_sum += contribution
            total_weight += WEIGHT_CONFIG['other_risk']
            other_risk_processed += 1
            # Record risk level
            if tag_info.get('risk_level'):
                risk_levels.add(tag_info['risk_level'])
        
        num_risk_tags += other_risk_processed

        # Depth impact (with decay)
        effective_depth = min(depth, 50)
        depth_impact = WEIGHT_CONFIG['depth_base'] * (
            WEIGHT_CONFIG['depth_decay'] ** (effective_depth/5))
        weighted_sum += depth_impact
        total_weight += WEIGHT_CONFIG['depth_base']

        # Apply single tag penalty (only when 1 risk tag exists)
        if num_risk_tags == 1:
            penalty = WEIGHT_CONFIG['single_tag_penalty']
            weighted_sum += 0.5 * penalty  # Move towards neutral value 0.5
            total_weight += penalty

        # Apply diversity penalty (when single risk level exists)
        if len(risk_levels) == 2:
            diversity_penalty = WEIGHT_CONFIG['diversity_penalty']
            weighted_sum += 0.5 * diversity_penalty  # Move towards neutral value 0.5
            total_weight += diversity_penalty

        # Handle case with no valid features
        if total_weight == 0:
            return 0.5

        # Calculate and limit confidence range
        final_confidence = weighted_sum / total_weight
        return min(max(round(final_confidence, 2), 0.0), 1.0)

    def format_features(self, features):
        """Format output"""
        components = [
            f"content: '{features['content']}'",
            f"last_tag: <{features['last_tag']['tag']}>[{features['last_tag']['risk_level']}]",
            f"risk_tags: {', '.join([f'''{rt['tag']}[{rt['risk_level']}]''' for rt in features['risk_tags']])}",
            f"depth: {features['depth']}",
            f"confidence: {features['confidence']:.2f}"
        ]
        return " | ".join(components)

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tag_probs_path = "./tag_probs.json"
    classifier = AutoRiskClassifier(tag_probs_path)
    classifier.process_dataset(
        "./web_noise_test_dataset_new.json",
        "./new_enhanced_test_dataset_new.json"
    )
    print("Test dataset enhancement completed!")
    classifier.process_dataset(
        "./web_noise_train_dataset_new.json",
        "./new_enhanced_train_dataset_new.json"
    )
    print("Training dataset enhancement completed!")