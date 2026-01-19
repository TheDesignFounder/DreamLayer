"""
Composition Metrics for DreamLayer
Combines YOLO object detection (prompt accuracy) with visual composition analysis
"""

import os
import re
import statistics
from typing import List, Dict, Any, Optional
import logging

import cv2
import numpy as np
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lazy imports for YOLO and NLTK (heavy dependencies)
_yolo_model = None
_yolo_loaded = False
_nltk_loaded = False
_lemmatizer = None


def _ensure_nltk():
    """Lazy load NLTK and required data"""
    global _nltk_loaded, _lemmatizer
    if _nltk_loaded:
        return True

    try:
        import nltk
        from nltk.stem import WordNetLemmatizer

        # Download required NLTK data
        required_data = [
            ('tokenizers/punkt', 'punkt'),
            ('tokenizers/punkt_tab', 'punkt_tab'),
            ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger'),
            ('taggers/averaged_perceptron_tagger_eng', 'averaged_perceptron_tagger_eng'),
            ('corpora/wordnet', 'wordnet')
        ]

        for resource_path, download_name in required_data:
            try:
                nltk.data.find(resource_path)
            except LookupError:
                try:
                    nltk.download(download_name, quiet=True)
                except Exception as e:
                    logger.warning(f"Failed to download NLTK resource {download_name}: {e}")

        _lemmatizer = WordNetLemmatizer()
        _nltk_loaded = True
        return True
    except Exception as e:
        logger.error(f"Failed to load NLTK: {e}")
        return False


def _ensure_yolo(config: Dict) -> bool:
    """Lazy load YOLO model"""
    global _yolo_model, _yolo_loaded
    if _yolo_loaded:
        return _yolo_model is not None

    try:
        from ultralytics import YOLO

        model_name = config.get("yolo", {}).get("model", "yolov8n.pt")
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(scripts_dir, model_name)

        logger.info(f"Loading YOLO model: {model_name}")

        if os.path.exists(model_path):
            _yolo_model = YOLO(model_path)
        else:
            # Download to scripts folder
            original_cwd = os.getcwd()
            try:
                os.chdir(scripts_dir)
                _yolo_model = YOLO(model_name)
                logger.info(f"YOLO model downloaded to {scripts_dir}")
            finally:
                os.chdir(original_cwd)

        _yolo_loaded = True
        logger.info("YOLO model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load YOLO model: {e}")
        _yolo_loaded = True  # Mark as attempted
        return False


class CompositionMetricsCalculator:
    """Calculate both object detection and visual composition metrics"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if config_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, '..', 'config', 'composition_config.yaml')

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")

        # Default config
        return {
            "yolo": {"model": "yolov8n.pt", "conf_threshold": 0.25, "iou_threshold": 0.5, "max_detections": 100},
            "synonyms": {},
            "coco_classes": []
        }

    # ==================== YOLO OBJECT DETECTION ====================

    def extract_target_objects(self, prompt: str) -> Dict[str, Any]:
        """Extract target objects from prompt using NLTK"""
        if not _ensure_nltk():
            return {"target_objects": {}, "mapped_objects": {}}

        try:
            from nltk.tokenize import word_tokenize
            from nltk.tag import pos_tag

            tokens = word_tokenize(prompt.lower())
            pos_tags = pos_tag(tokens)

            # Extract nouns
            nouns = []
            for word, pos in pos_tags:
                if pos.startswith('NN'):
                    lemmatized = _lemmatizer.lemmatize(word)
                    nouns.append(lemmatized)

            # Extract counts and objects
            target_objects = {}
            count_patterns = [
                (r'(\d+)\s+(\w+)', lambda m: (int(m.group(1)), m.group(2))),
                (r'(two|three|four|five|six|seven|eight|nine|ten)\s+(\w+)',
                 lambda m: (self._word_to_number(m.group(1)), m.group(2))),
                (r'a\s+(\w+)', lambda m: (1, m.group(1)))
            ]

            prompt_lower = prompt.lower()
            for pattern, extractor in count_patterns:
                for match in re.finditer(pattern, prompt_lower):
                    count, obj = extractor(match)
                    obj_lemmatized = _lemmatizer.lemmatize(obj)
                    if obj_lemmatized in nouns:
                        target_objects[obj_lemmatized] = target_objects.get(obj_lemmatized, 0) + count

            # Add remaining nouns with count 1
            for noun in nouns:
                if noun not in target_objects:
                    target_objects[noun] = 1

            # Map to COCO classes
            mapped_objects = {}
            for obj, count in target_objects.items():
                mapped_obj = self._map_to_coco_class(obj)
                if mapped_obj:
                    mapped_objects[mapped_obj] = mapped_objects.get(mapped_obj, 0) + count

            return {"target_objects": target_objects, "mapped_objects": mapped_objects}
        except Exception as e:
            logger.error(f"Error extracting target objects: {e}")
            return {"target_objects": {}, "mapped_objects": {}}

    def _word_to_number(self, word: str) -> int:
        """Convert word numbers to integers"""
        mapping = {"two": 2, "three": 3, "four": 4, "five": 5,
                   "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
        return mapping.get(word.lower(), 1)

    def _map_to_coco_class(self, obj: str) -> Optional[str]:
        """Map object to COCO class using synonyms"""
        coco_classes = self.config.get("coco_classes", [])
        if obj in coco_classes:
            return obj

        for coco_class, synonyms in self.config.get("synonyms", {}).items():
            if obj in synonyms or obj == coco_class:
                return coco_class
        return None

    def detect_objects(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect objects in image using YOLO"""
        if not _ensure_yolo(self.config):
            return []

        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return []

        try:
            results = _yolo_model(
                image_path,
                conf=self.config["yolo"]["conf_threshold"],
                iou=self.config["yolo"]["iou_threshold"],
                max_det=self.config["yolo"]["max_detections"],
                verbose=False
            )

            detections = []
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        class_name = _yolo_model.names[class_id]
                        bbox = box.xyxy[0].tolist()

                        detections.append({
                            "class_name": class_name,
                            "confidence": confidence,
                            "class_id": class_id,
                            "bbox": bbox
                        })

            return detections
        except Exception as e:
            logger.error(f"Error detecting objects: {e}")
            return []

    def calculate_object_metrics(self, prompt: str, image_path: str) -> Dict[str, Any]:
        """Calculate object detection accuracy metrics"""
        target_data = self.extract_target_objects(prompt)
        target_objects = target_data["mapped_objects"]

        if not target_objects:
            return {
                "object_precision": None,
                "object_recall": None,
                "object_f1": None,
                "detected_objects": {},
                "missing_objects": {},
                "target_objects": {}
            }

        detections = self.detect_objects(image_path)

        # Count detected objects
        detected_counts = {}
        for detection in detections:
            class_name = detection["class_name"]
            detected_counts[class_name] = detected_counts.get(class_name, 0) + 1

        # Calculate per-class metrics
        per_class_metrics = {}
        all_classes = set(target_objects.keys()) | set(detected_counts.keys())

        for class_name in all_classes:
            target_count = target_objects.get(class_name, 0)
            detected_count = detected_counts.get(class_name, 0)

            if detected_count > 0:
                precision = min(target_count, detected_count) / detected_count
            else:
                precision = 1.0 if target_count == 0 else 0.0

            if target_count > 0:
                recall = min(target_count, detected_count) / target_count
            else:
                recall = 1.0 if detected_count == 0 else 0.0

            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            per_class_metrics[class_name] = {
                "precision": precision, "recall": recall, "f1": f1,
                "target": target_count, "detected": detected_count
            }

        # Macro metrics
        if per_class_metrics:
            macro_precision = statistics.mean([m["precision"] for m in per_class_metrics.values()])
            macro_recall = statistics.mean([m["recall"] for m in per_class_metrics.values()])
            macro_f1 = statistics.mean([m["f1"] for m in per_class_metrics.values()])
        else:
            macro_precision = macro_recall = macro_f1 = 0.0

        missing = {k: v for k, v in target_objects.items() if k not in detected_counts}

        return {
            "object_precision": macro_precision,
            "object_recall": macro_recall,
            "object_f1": macro_f1,
            "detected_objects": detected_counts,
            "missing_objects": missing,
            "target_objects": target_objects,
            "per_class_metrics": per_class_metrics
        }

    # ==================== VISUAL COMPOSITION ANALYSIS ====================

    def calculate_rule_of_thirds(self, image: np.ndarray) -> Dict[str, float]:
        """
        Analyze how well the image follows the rule of thirds.
        Returns score 0-1 (higher = better adherence to rule of thirds)
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            height, width = gray.shape

            # Define rule of thirds lines (1/3 and 2/3 positions)
            h_lines = [height // 3, 2 * height // 3]
            v_lines = [width // 3, 2 * width // 3]

            # Power points (intersections)
            power_points = [(v, h) for h in h_lines for v in v_lines]

            # Detect edges to find areas of interest
            edges = cv2.Canny(gray, 50, 150)

            # Calculate edge density near power points and thirds lines
            margin = min(width, height) // 10

            total_score = 0.0

            # Score power points
            for x, y in power_points:
                y1, y2 = max(0, y - margin), min(height, y + margin)
                x1, x2 = max(0, x - margin), min(width, x + margin)
                region = edges[y1:y2, x1:x2]
                if region.size > 0:
                    density = np.mean(region) / 255.0
                    total_score += density

            # Normalize (4 power points)
            power_point_score = total_score / 4.0

            # Score edge alignment with thirds lines
            line_score = 0.0
            line_margin = margin // 2

            # Horizontal lines
            for h in h_lines:
                y1, y2 = max(0, h - line_margin), min(height, h + line_margin)
                region = edges[y1:y2, :]
                if region.size > 0:
                    line_score += np.mean(region) / 255.0

            # Vertical lines
            for v in v_lines:
                x1, x2 = max(0, v - line_margin), min(width, v + line_margin)
                region = edges[:, x1:x2]
                if region.size > 0:
                    line_score += np.mean(region) / 255.0

            line_score = line_score / 4.0  # 4 lines total

            # Combined score (weight power points more)
            final_score = 0.6 * power_point_score + 0.4 * line_score

            return {
                "rule_of_thirds_score": min(1.0, final_score * 3),  # Scale up for interpretability
                "power_point_score": min(1.0, power_point_score * 3),
                "line_alignment_score": min(1.0, line_score * 3)
            }
        except Exception as e:
            logger.error(f"Error calculating rule of thirds: {e}")
            return {"rule_of_thirds_score": None, "power_point_score": None, "line_alignment_score": None}

    def calculate_symmetry(self, image: np.ndarray) -> Dict[str, float]:
        """
        Analyze horizontal and vertical symmetry.
        Returns score 0-1 (higher = more symmetrical)
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            gray = gray.astype(np.float32)
            height, width = gray.shape

            # Horizontal symmetry (flip left-right)
            left_half = gray[:, :width // 2]
            right_half = cv2.flip(gray[:, width - width // 2:], 1)

            # Ensure same size
            min_w = min(left_half.shape[1], right_half.shape[1])
            left_half = left_half[:, :min_w]
            right_half = right_half[:, :min_w]

            h_diff = np.abs(left_half - right_half)
            h_symmetry = 1.0 - (np.mean(h_diff) / 255.0)

            # Vertical symmetry (flip top-bottom)
            top_half = gray[:height // 2, :]
            bottom_half = cv2.flip(gray[height - height // 2:, :], 0)

            min_h = min(top_half.shape[0], bottom_half.shape[0])
            top_half = top_half[:min_h, :]
            bottom_half = bottom_half[:min_h, :]

            v_diff = np.abs(top_half - bottom_half)
            v_symmetry = 1.0 - (np.mean(v_diff) / 255.0)

            # Overall symmetry (max of both - images usually have one dominant axis)
            overall = max(h_symmetry, v_symmetry)

            return {
                "symmetry_score": overall,
                "horizontal_symmetry": h_symmetry,
                "vertical_symmetry": v_symmetry
            }
        except Exception as e:
            logger.error(f"Error calculating symmetry: {e}")
            return {"symmetry_score": None, "horizontal_symmetry": None, "vertical_symmetry": None}

    def calculate_visual_balance(self, image: np.ndarray) -> Dict[str, float]:
        """
        Analyze visual weight distribution across quadrants.
        Returns score 0-1 (higher = better balanced)
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            height, width = gray.shape

            # Split into quadrants
            mid_h, mid_w = height // 2, width // 2
            quadrants = [
                gray[:mid_h, :mid_w],      # Top-left
                gray[:mid_h, mid_w:],      # Top-right
                gray[mid_h:, :mid_w],      # Bottom-left
                gray[mid_h:, mid_w:]       # Bottom-right
            ]

            # Calculate "visual weight" (intensity + edge density)
            weights = []
            for q in quadrants:
                intensity = np.mean(q) / 255.0
                edges = cv2.Canny(q.astype(np.uint8), 50, 150)
                edge_density = np.mean(edges) / 255.0
                weights.append(0.5 * intensity + 0.5 * edge_density)

            # Calculate balance (lower variance = better balance)
            variance = np.var(weights)
            balance_score = 1.0 - min(1.0, variance * 10)  # Scale variance

            return {
                "balance_score": balance_score,
                "quadrant_weights": weights
            }
        except Exception as e:
            logger.error(f"Error calculating visual balance: {e}")
            return {"balance_score": None, "quadrant_weights": None}

    def calculate_edge_distribution(self, image: np.ndarray) -> Dict[str, float]:
        """
        Analyze edge distribution - good images often have edges leading to focal points.
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            height, width = gray.shape

            edges = cv2.Canny(gray, 50, 150)

            # Calculate edge density in center vs periphery
            center_margin = min(width, height) // 4
            center = edges[center_margin:height-center_margin, center_margin:width-center_margin]

            total_edges = np.sum(edges > 0)
            center_edges = np.sum(center > 0)

            if total_edges > 0:
                center_ratio = center_edges / total_edges
            else:
                center_ratio = 0.5

            # Good composition often has moderate center focus (not too much, not too little)
            # Optimal is around 0.3-0.5 (some center focus but not all)
            optimal_ratio = 0.4
            focus_score = 1.0 - abs(center_ratio - optimal_ratio) * 2
            focus_score = max(0, min(1, focus_score))

            return {
                "edge_focus_score": focus_score,
                "center_edge_ratio": center_ratio,
                "total_edge_density": np.mean(edges) / 255.0
            }
        except Exception as e:
            logger.error(f"Error calculating edge distribution: {e}")
            return {"edge_focus_score": None, "center_edge_ratio": None, "total_edge_density": None}

    def calculate_visual_composition(self, image_path: str) -> Dict[str, Any]:
        """Calculate all visual composition metrics for an image"""
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return self._empty_visual_metrics()

        try:
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return self._empty_visual_metrics()

            thirds = self.calculate_rule_of_thirds(image)
            symmetry = self.calculate_symmetry(image)
            balance = self.calculate_visual_balance(image)
            edges = self.calculate_edge_distribution(image)

            # Calculate overall composition score (weighted average)
            scores = []
            weights = []

            if thirds["rule_of_thirds_score"] is not None:
                scores.append(thirds["rule_of_thirds_score"])
                weights.append(0.3)
            if symmetry["symmetry_score"] is not None:
                scores.append(symmetry["symmetry_score"])
                weights.append(0.2)
            if balance["balance_score"] is not None:
                scores.append(balance["balance_score"])
                weights.append(0.25)
            if edges["edge_focus_score"] is not None:
                scores.append(edges["edge_focus_score"])
                weights.append(0.25)

            if scores and weights:
                total_weight = sum(weights)
                overall = sum(s * w for s, w in zip(scores, weights)) / total_weight
            else:
                overall = None

            return {
                "composition_score": overall,
                **thirds,
                **symmetry,
                **balance,
                **edges
            }
        except Exception as e:
            logger.error(f"Error calculating visual composition: {e}")
            return self._empty_visual_metrics()

    def _empty_visual_metrics(self) -> Dict[str, Any]:
        """Return empty visual metrics structure"""
        return {
            "composition_score": None,
            "rule_of_thirds_score": None,
            "power_point_score": None,
            "line_alignment_score": None,
            "symmetry_score": None,
            "horizontal_symmetry": None,
            "vertical_symmetry": None,
            "balance_score": None,
            "quadrant_weights": None,
            "edge_focus_score": None,
            "center_edge_ratio": None,
            "total_edge_density": None
        }

    # ==================== COMBINED METRICS ====================

    def calculate_all_metrics(self, prompt: str, image_path: str) -> Dict[str, Any]:
        """Calculate both object detection and visual composition metrics"""
        object_metrics = self.calculate_object_metrics(prompt, image_path)
        visual_metrics = self.calculate_visual_composition(image_path)

        return {
            **object_metrics,
            **visual_metrics
        }


# Singleton instance
_calculator = None

def get_composition_calculator() -> CompositionMetricsCalculator:
    """Get or create singleton calculator instance"""
    global _calculator
    if _calculator is None:
        _calculator = CompositionMetricsCalculator()
    return _calculator


def calculate_composition_metrics(prompt: str, image_path: str) -> Dict[str, Any]:
    """Convenience function to calculate all composition metrics"""
    calculator = get_composition_calculator()
    return calculator.calculate_all_metrics(prompt, image_path)
