"""
Composition Correctness Metrics Integration with Database
Follows the clip_integration.py pattern for DreamLayer AI
"""

import os
import re
import json
import statistics
from typing import List, Dict, Any, Optional, Tuple
import logging

# Core dependencies
import cv2
import numpy as np
import nltk
from ultralytics import YOLO
import yaml

# Database integration
from queries import DreamLayerQueries

# Download required NLTK data
required_nltk_data = [
    ('tokenizers/punkt', 'punkt'),
    ('tokenizers/punkt_tab', 'punkt_tab'),
    ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger'),
    ('taggers/averaged_perceptron_tagger_eng', 'averaged_perceptron_tagger_eng'),
    ('corpora/wordnet', 'wordnet')
]

for resource_path, download_name in required_nltk_data:
    try:
        nltk.data.find(resource_path)
    except LookupError:
        try:
            nltk.download(download_name, quiet=True)
        except Exception as e:
            logger.warning(f"Failed to download NLTK resource {download_name}: {e}")

from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.stem import WordNetLemmatizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompositionMetricsCalculator:
    """Calculate composition correctness metrics for image-prompt pairs"""
    
    # Class-level model cache for reuse across instances
    _shared_model = None
    _shared_model_loaded = False
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.lemmatizer = WordNetLemmatizer()
        
        # Use shared model instance
        self.model = CompositionMetricsCalculator._shared_model
        self._model_loaded = CompositionMetricsCalculator._shared_model_loaded
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from YAML file using absolute paths"""
        if config_path is None:
            # Find DreamLayer project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = current_dir
            
            # Navigate up to find DreamLayer root
            while project_root != os.path.dirname(project_root):
                if os.path.exists(os.path.join(project_root, 'Dream_Layer_Resources')):
                    break
                project_root = os.path.dirname(project_root)
            
            config_path = os.path.join(project_root, 'dream_layer_backend', 'config', 'composition_config.yaml')
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {config_path}")
                return config
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            raise
    
    def _load_model(self):
        """Lazy load YOLO model with shared instance and automatic download to scripts folder"""
        if CompositionMetricsCalculator._shared_model_loaded:
            self.model = CompositionMetricsCalculator._shared_model
            self._model_loaded = True
            return
        
        try:
            model_name = self.config["yolo"]["model"]
            
            # Define the model path in the scripts folder
            scripts_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(scripts_dir, model_name)
            
            logger.info(f"Loading YOLO model: {model_name}")
            logger.info(f"Model path: {model_path}")
            
            # Check if model file exists in scripts folder
            if os.path.exists(model_path):
                logger.info(f"Model file found at {model_path}")
                # Load from existing file
                CompositionMetricsCalculator._shared_model = YOLO(model_path)
            else:
                logger.info(f"Model file {model_name} not found in scripts folder. Downloading to {model_path}...")
                # Download to scripts folder by temporarily changing working directory
                original_cwd = os.getcwd()
                try:
                    os.chdir(scripts_dir)
                    CompositionMetricsCalculator._shared_model = YOLO(model_name)
                    logger.info(f"YOLO model {model_name} downloaded to {scripts_dir}")
                finally:
                    os.chdir(original_cwd)
            
            CompositionMetricsCalculator._shared_model_loaded = True
            
            # Update instance references
            self.model = CompositionMetricsCalculator._shared_model
            self._model_loaded = True
            
            logger.info(f"YOLO model {model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load YOLO model {model_name}: {e}")
            logger.error("This could be due to network connectivity issues during model download.")
            logger.error("Please ensure you have internet access for the initial model download.")
            CompositionMetricsCalculator._shared_model = None
            CompositionMetricsCalculator._shared_model_loaded = False
            self.model = None
            self._model_loaded = False
    
    def extract_target_objects(self, prompt: str) -> Dict[str, Any]:
        """Extract target objects and counts from prompt using NLTK"""
        try:
            # Tokenize and POS tag
            tokens = word_tokenize(prompt.lower())
            pos_tags = pos_tag(tokens)
            
            # Extract nouns
            nouns = []
            for word, pos in pos_tags:
                if pos.startswith('NN'):  # Noun tags
                    lemmatized = self.lemmatizer.lemmatize(word)
                    nouns.append(lemmatized)
            
            # Extract counts and objects
            target_objects = {}
            
            # Simple count extraction patterns
            count_patterns = [
                (r'(\d+)\s+(\w+)', lambda m: (int(m.group(1)), m.group(2))),
                (r'(two|three|four|five)\s+(\w+)', lambda m: (self._word_to_number(m.group(1)), m.group(2))),
                (r'a\s+(\w+)', lambda m: (1, m.group(1)))
            ]
            
            prompt_lower = prompt.lower()
            for pattern, extractor in count_patterns:
                matches = re.finditer(pattern, prompt_lower)
                for match in matches:
                    count, obj = extractor(match)
                    obj_lemmatized = self.lemmatizer.lemmatize(obj)
                    if obj_lemmatized in nouns:
                        target_objects[obj_lemmatized] = target_objects.get(obj_lemmatized, 0) + count
            
            # Add remaining nouns with count 1 if not already counted
            for noun in nouns:
                if noun not in target_objects:
                    target_objects[noun] = 1
            
            # Map synonyms to COCO classes
            mapped_objects = {}
            for obj, count in target_objects.items():
                mapped_obj = self._map_to_coco_class(obj)
                if mapped_obj:
                    mapped_objects[mapped_obj] = mapped_objects.get(mapped_obj, 0) + count
            
            return {
                "target_objects": target_objects,
                "mapped_objects": mapped_objects
            }
            
        except Exception as e:
            logger.error(f"Error extracting target objects: {e}")
            return {"target_objects": {}, "mapped_objects": {}}
    
    def _word_to_number(self, word: str) -> int:
        """Convert word numbers to integers"""
        word_to_num = {"two": 2, "three": 3, "four": 4, "five": 5}
        return word_to_num.get(word.lower(), 1)
    
    def _map_to_coco_class(self, obj: str) -> Optional[str]:
        """Map object to COCO class using synonyms from config"""
        # Get COCO classes from config
        coco_classes = self.config.get("coco_classes", [])
        
        # Direct match
        if obj in coco_classes:
            return obj
        
        # Check synonyms
        for coco_class, synonyms in self.config["synonyms"].items():
            if obj in synonyms or obj == coco_class:
                return coco_class
        
        return None
    
    def detect_objects(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect objects in image using YOLO - expects full resolved path"""
        self._load_model()
        
        if self.model is None:
            logger.warning("YOLO model not available")
            return []
        
        try:
            # image_path should already be resolved by get_image_path_for_clip_score
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return []
            
            # Run YOLO detection
            results = self.model(
                image_path,
                conf=self.config["yolo"]["conf_threshold"],
                iou=self.config["yolo"]["iou_threshold"],
                max_det=self.config["yolo"]["max_detections"]
            )
            
            detections = []
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        class_name = self.model.names[class_id]
                        
                        detections.append({
                            "class_name": class_name,
                            "confidence": confidence,
                            "class_id": class_id
                        })
            
            logger.debug(f"Detected {len(detections)} objects in {image_path}")
            return detections
            
        except Exception as e:
            logger.error(f"Error detecting objects in {image_path}: {e}")
            return []
    
    def calculate_metrics(self, prompt: str, image_path: str) -> Dict[str, Any]:
        """Calculate composition correctness metrics for a single image-prompt pair"""
        try:
            # Extract target objects from prompt
            target_data = self.extract_target_objects(prompt)
            target_objects = target_data["mapped_objects"]
            
            if not target_objects:
                return self._empty_metrics()
            
            # Detect objects in image
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
                
                # Calculate precision, recall, F1 for this class
                if detected_count > 0:
                    precision = min(target_count, detected_count) / detected_count
                else:
                    precision = 1.0 if target_count == 0 else 0.0
                
                if target_count > 0:
                    recall = min(target_count, detected_count) / target_count
                else:
                    recall = 1.0 if detected_count == 0 else 0.0
                
                if precision + recall > 0:
                    f1 = 2 * (precision * recall) / (precision + recall)
                else:
                    f1 = 0.0
                
                per_class_metrics[class_name] = {
                    "precision": precision,
                    "recall": recall,
                    "f1": f1,
                    "target_count": target_count,
                    "detected_count": detected_count
                }
            
            # Calculate macro metrics
            if per_class_metrics:
                macro_precision = statistics.mean([m["precision"] for m in per_class_metrics.values()])
                macro_recall = statistics.mean([m["recall"] for m in per_class_metrics.values()])
                macro_f1 = statistics.mean([m["f1"] for m in per_class_metrics.values()])
            else:
                macro_precision = macro_recall = macro_f1 = 0.0
            
            # Identify missing objects
            missing_objects = {k: v for k, v in target_objects.items() if k not in detected_counts}
            
            return {
                "macro_precision": macro_precision,
                "macro_recall": macro_recall,
                "macro_f1": macro_f1,
                "per_class_metrics": per_class_metrics,
                "detected_objects": detected_counts,
                "missing_objects": missing_objects,
                "target_objects": target_objects
            }
            
        except Exception as e:
            logger.error(f"Error calculating composition metrics: {e}")
            return self._empty_metrics()
    
    def _empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure"""
        return {
            "macro_precision": 0.0,
            "macro_recall": 0.0,
            "macro_f1": 0.0,
            "per_class_metrics": {},
            "detected_objects": {},
            "missing_objects": {},
            "target_objects": {}
        }


class DatabaseCompositionCalculator:
    """Composition metrics calculator that uses database for path resolution (follows ClipScore pattern)"""
    
    def __init__(self):
        self.queries = DreamLayerQueries()
        self.composition_calculator = CompositionMetricsCalculator()
    
    def calculate_for_run(self, run_id: str, image_index: int = 0) -> Optional[Dict[str, Any]]:
        """Calculate composition metrics for a specific run and image"""
        try:
            # Get run data
            run = self.queries.db.get_run(run_id)
            if not run:
                logger.error(f"Run {run_id} not found in database")
                return None
            
            # Reuse the working ClipScore image path method
            image_path = self.queries.get_image_path_for_clip_score(run_id, image_index)
            if not image_path:
                logger.error(f"No image path found for run {run_id}")
                return None
            
            # Get prompt
            prompt = run.get('prompt', '')
            if not prompt:
                logger.error(f"No prompt found for run {run_id}")
                return None
            
            # Calculate composition metrics using the working image path
            metrics = self.composition_calculator.calculate_metrics(prompt, image_path)
            
            # Save to database
            if self.queries.save_composition_metrics(run_id, run['timestamp'], prompt, image_path, metrics):
                logger.info(f"Calculated and saved composition metrics for run {run_id}")
                return metrics
            else:
                logger.error(f"Failed to save composition metrics for run {run_id}")
                return metrics  # Return value even if save failed
            
        except Exception as e:
            logger.error(f"Error calculating composition metrics for run {run_id}: {e}")
            return None
    
    def calculate_batch(self, limit: int = 50) -> Dict[str, Any]:
        """Calculate composition metrics for multiple runs that don't have it"""
        # Get runs without composition metrics
        runs_without_composition = self.queries.get_runs_without_composition_metrics(limit)
        
        stats = {
            "total": len(runs_without_composition),
            "success": 0,
            "failed": 0,
            "results": []
        }
        
        logger.info(f"Calculating composition metrics for {stats['total']} runs...")
        
        for run in runs_without_composition:
            run_id = run['run_id']
            metrics = self.calculate_for_run(run_id)
            
            if metrics is not None:
                stats["success"] += 1
                stats["results"].append({
                    "run_id": run_id,
                    "macro_f1": metrics["macro_f1"],
                    "macro_precision": metrics["macro_precision"],
                    "macro_recall": metrics["macro_recall"],
                    "prompt": run.get('prompt', '')[:50] + "..."
                })
            else:
                stats["failed"] += 1
        
        logger.info(f"Batch calculation complete: {stats['success']} success, {stats['failed']} failed")
        return stats


def calculate_missing_composition_metrics(limit: int = 50) -> Dict[str, Any]:
    """Convenience function to calculate missing composition metrics"""
    calculator = DatabaseCompositionCalculator()
    return calculator.calculate_batch(limit)

def compute_composition_metrics_for_run(run_id: str) -> Optional[Dict[str, Any]]:
    """Convenience function to calculate composition metrics for a single run"""
    calculator = DatabaseCompositionCalculator()
    return calculator.calculate_for_run(run_id)


if __name__ == "__main__":
    # Test composition metrics calculation
    calculator = DatabaseCompositionCalculator()
    
    # Calculate for runs without composition metrics
    stats = calculator.calculate_batch(limit=5)
    print(f"Calculated composition metrics for {stats['success']}/{stats['total']} runs")
    
    # Show results
    for result in stats['results'][:3]:
        print(f"Run {result['run_id']}: F1 {result['macro_f1']:.4f}, P {result['macro_precision']:.4f}, R {result['macro_recall']:.4f}")
