import logging
import re
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class Model3DMapper:
    """
    Maps conversation topics/keywords to 3D model files.
    Detects topic changes and returns appropriate 3D model paths.
    """
    
    def __init__(self, models_dir="3d v2"):
        """
        Initialize 3D model mapper.
        
        Args:
            models_dir: Directory containing 3D model files
        """
        self.models_dir = models_dir
        self.current_topic = None
        self.current_model = None
        
        # Define topic -> 3D model mappings
        self.topic_mappings = {
            "quadruped": {
                "keywords": ["unitree", "go2", "quadruped", "robot dog", "legged robot", "four legged"],
                "model_path": "3d v2/robot_dog_unitree_go2.glb",
                "model_name": "Unitree Go2 Robot Dog"
            },
            "depth_camera": {
                "keywords": ["realsense", "d435i", "depth camera", "intel", "stereo camera", "3d camera"],
                "model_path": "3d v2/source/model.glb",  # Intel RealSense model
                "model_name": "Intel RealSense D435i"
            },
            "drone": {
                "keywords": ["drone", "quadcopter", "aerial", "uav", "flying", "flight"],
                "model_path": "3d v2/animated-icon-2-optimize.glb",  # Lightweight preview model
                "model_name": "Quadcopter Drone (Preview)"
            },
            "prototyping": {
                "keywords": ["breadboard", "arduino", "prototype", "circuit", "electronics"],
                "model_path": "3d v2/source/Board.glb",  # Arduino breadboard
                "model_name": "Arduino & Breadboard Kit"
            },
        }
        
        logger.info(f"[3D Mapper] Initialized with {len(self.topic_mappings)} topic mappings")
    
    def detect_topic(self, text: str) -> Optional[str]:
        """
        Detect topic from text based on keywords.
        
        Args:
            text: User input or conversation text
            
        Returns:
            Topic name if detected, None otherwise
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Check each topic's keywords
        for topic, data in self.topic_mappings.items():
            for keyword in data["keywords"]:
                # Word boundary match for single words, substring for phrases
                if ' ' in keyword:
                    if keyword in text_lower:
                        logger.debug(f"[3D Mapper] Detected topic '{topic}' from keyword '{keyword}'")
                        return topic
                else:
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    if re.search(pattern, text_lower):
                        logger.debug(f"[3D Mapper] Detected topic '{topic}' from keyword '{keyword}'")
                        return topic
        
        return None
    
    def get_model_for_topic(self, topic: str) -> Optional[Dict[str, str]]:
        """
        Get 3D model information for a topic.
        
        Args:
            topic: Topic name
            
        Returns:
            Dictionary with model_path and model_name, or None if not found
        """
        if topic in self.topic_mappings:
            data = self.topic_mappings[topic]
            return {
                "model_path": data["model_path"],
                "model_name": data["model_name"]
            }
        return None
    
    def process_text(self, text: str) -> Optional[Dict[str, str]]:
        """
        Process text and return 3D model info if topic changed.
        
        Args:
            text: User input text
            
        Returns:
            Dictionary with model info if topic changed, None otherwise
        """
        detected_topic = self.detect_topic(text)
        
        # No topic detected
        if detected_topic is None:
            return None
        
        # Topic changed
        if detected_topic != self.current_topic:
            model_info = self.get_model_for_topic(detected_topic)
            if model_info:
                self.current_topic = detected_topic
                self.current_model = model_info["model_path"]
                logger.info(f"[🎨 3D MODEL CHANGE] Topic: '{detected_topic}' → Model: {model_info['model_name']}")
                return model_info
        
        # Same topic, no change
        return None
    
    def reset(self):
        """Reset current topic tracking"""
        self.current_topic = None
        self.current_model = None
        logger.debug("[3D Mapper] State reset")
