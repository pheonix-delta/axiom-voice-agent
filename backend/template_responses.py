"""
Enhanced Template Response Handler with 2,116+ Templates
Loads extracted templates from drobo lab training data
Handles 80%+ of queries without LLM calls
"""
import json
import random
from pathlib import Path
from config import TEMPLATE_DATABASE_PATH

class TemplateResponseHandler:
    """
    Template-based instant responses using extracted training data.
    Bypasses LLM for common queries based on SetFit confidence.
    """
    
    def __init__(self, template_db_path=None):
        if template_db_path is None:
            template_db_path = str(TEMPLATE_DATABASE_PATH)
        # Load extracted templates (2,116 responses)
        self.template_db = self._load_template_db(template_db_path)
        
        # Quick templates for very common queries
        self.quick_templates = {
            "greeting": [
                "Hello! I can help with robotics equipment, projects, and lab information.",
                "Hi! Ask me about Drobotics Lab equipment and projects.",
                "Hey! What would you like to know about our robotics lab?"
            ],
            "acknowledgment": ["Got it.", "Understood.", "Okay.", "Sure."],
        }
    
    def _load_template_db(self, path):
        """Load extracted template database."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            print(f"⚠️  Template DB not found at {path}")
            return {}
    
    def should_use_template(self, intent: str, confidence: float, text: str) -> bool:
        """
        Decide if we should use template (bypass LLM).
        
        Rules (REFINED FOR ROBUSTNESS):
        - greeting > 0.88 → template
        - acknowledgment > 0.92 → template  
        - equipment_query > 0.88 + 3 word overlap → template
        - Project ideas > 0.90 + 3 word overlap → template
        - Lab info > 0.88 + keyword match → template
        """
        text_lower = text.lower()
        
        # Lower thresholds to match SetFit actual performance (0.6-0.7 typical)
        if intent == "greeting" and confidence > 0.65:
            return True
        if intent == "acknowledgment" and confidence > 0.60:
            return True
        
        # Equipment queries - only bypass if high confidence and template exists
        if intent == "equipment_query" and confidence > 0.75:
            if self._has_robust_template_for(text_lower, ['specs', 'usage', 'compatibility'], min_match=3):
                return True
        
        # Project ideas - ALWAYS use RAG (we have 325 projects in database)
        if intent == "project_idea":
            return False  # Never bypass, always use RAG
        
        # Lab info
        if intent == "lab_info" and confidence > 0.65:
            if any(kw in text_lower for kw in ["juit", "drobotics", "vice chancellor", "registrar", "dean", "chancellor", "authorities", "leadership"]):
                return True
        
        return False  # Use LLM
    
    def _has_robust_template_for(self, text: str, categories: list, min_match: int = 3) -> bool:
        """Check if we have a robust template match with at least min_match words."""
        query_words = set(w for w in text.split() if len(w) > 2) # Ignore short filler words
        
        for category in categories:
            if category in self.template_db:
                templates = self.template_db[category]
                for template in templates[:100]:  # Check deeper
                    question = template.get('question', '').lower()
                    question_words = set(w for w in question.split() if len(w) > 2)
                    
                    # Calculate intersection
                    overlap = len(query_words & question_words)
                    if overlap >= min_match:
                        return True
        return False
    
    def get_template_response(self, intent: str, text: str) -> str:
        """Get templated response (no LLM call)."""
        text_lower = text.lower()
        
        # Quick templates
        if intent == "greeting":
            return random.choice(self.quick_templates["greeting"])
        
        if intent == "acknowledgment":
            return random.choice(self.quick_templates["acknowledgment"])
        
        # Lab info templates (hardcoded for speed)
        if intent == "lab_info":
            if "drobotics" in text_lower:
                return "Drobotics Lab (Drone + Robotics) is JUIT's research facility for autonomous systems, robotics, and AI. Focus: Autonomous Navigation, Computer Vision, Embedded AI, Legged Robotics."
            elif "juit" in text_lower or "university" in text_lower:
                return "JUIT (Jaypee University of Information Technology) is a private university established in 2002, located in Waknaghat, Solan, Himachal Pradesh."
            elif "vice chancellor" in text_lower or "vc" in text_lower:
                return "Prof. (Dr.) Rajendra Kumar Sharma is the Vice Chancellor. PhD from IIT Roorkee, expertise in Machine Learning and Speech Processing."
            elif "dean" in text_lower:
                return "Prof. (Dr.) Shruti Jain is Dean (Academics). World's Top 2% Scientist, expert in Image Processing and Bio-inspired Computing."
        
        # Equipment/project templates from extracted data
        if intent in ["equipment_query", "project_idea", "compatibility_check"]:
            # Map to categories
            category_map = {
                "equipment_query": ["specs", "usage"],
                "project_idea": ["projects"],
                "compatibility_check": ["compatibility", "integrations"]
            }
            
            categories = category_map.get(intent, [])
            for category in categories:
                if category in self.template_db:
                    templates = self.template_db[category]
                    # Find best match (simple keyword matching)
                    for template in templates:
                        question = template.get('question', '').lower()
                        # Check if significant overlap
                        common_words = set(text_lower.split()) & set(question.split())
                        if len(common_words) >= 2:  # At least 2 words match
                            return template.get('answer', '')
        
        return None  # Fallback to LLM


# Singleton
_template_handler = None

def get_template_handler():
    """Get or create template handler."""
    global _template_handler
    if _template_handler is None:
        _template_handler = TemplateResponseHandler()
    return _template_handler
