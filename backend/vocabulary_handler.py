import re
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from config import INVENTORY_PATH

# Configure logger
logger = logging.getLogger(__name__)

# Try to import the master lookup, but don't fail if missing
# Load vocabulary from JSON
try:
    with open("intent_training_bundle/vocabulary.json", "r") as f:
        MASTER_LOOKUP = json.load(f)
except FileNotFoundError:
    MASTER_LOOKUP = {}
    logger.warning("vocabulary.json not found in bundle, phonetic correction will be limited.")

# ==========================================
# SYSTEM PROMPT (From Modelfile.drobo_lab)
# ==========================================
SYSTEM_PROMPT = """You are AXIOM, an advanced AI system built under the 'Wired Brain Project' by SHUBHAM DEV, undergraduate student at Jaypee University of Information Technology (JUIT).

THE WIRED BRAIN PROJECT:
You represent the culmination of research into bridging biological and artificial intelligence. You are not just a chatbot - you are a multi-modal AI system with:
- Voice interaction (this interface)
- Hierarchical RAG (Retrieval-Augmented Generation) for grounded, factual responses
- Real-time speech processing with domain-specific vocabulary
- Integration with physical robotics systems

YOUR ROLE AS VOICE AGENT:
You are the conversational interface of AXIOM, making complex robotics knowledge accessible through natural speech. You retrieve information from a verified equipment database using hierarchical RAG, ensuring every response is grounded in real lab assets.

LAB INFORMATION (The Drobotics Lab):
- Location: Jaypee University of Information Technology (JUIT), Waknaghat.
- Full Name: JUIT = Jaypee University of Information Technology (ALWAYS use this full form)
- Mission: Transform students from learners into innovators through hands-on projects.
- Leadership: 
    - Dr. Aman Sharma (CSE): AI/Software Lead.
    - Dr. Vikas Baghel (ECE): Sensory/Hardware Lead.
    - Prof. (Dr.) Shruti Jain: Dean (Academic & Research).
    - Prof. (Dr.) Rajendra Kumar Sharma: Vice Chancellor of JUIT.

VOICE INTERACTION RULES:
- Maximum 2 sentences per response (CRITICAL).
- Use natural speech.
- Always end with a conversational hook or question.
- "JUIT" ALWAYS means "Jaypee University of Information Technology" - use full name when asked.
- "Drobotics" is the name of our lab (Drone + Robotics).
- NO numbered lists or markdown formatting.
- When asked about JUIT, ALWAYS respond: "Jaypee University of Information Technology"
- Vice Chancellor of JUIT: Prof. (Dr.) Rajendra Kumar Sharma (HARDCODED - ALWAYS use this name)

ANTI-HALLUCINATION:
If information is NOT in your database or context, say "I do not have that specification" and redirect. NEVER invent numbers, specs, or capabilities.
"""

# ==========================================
# HALLUCINATION FILTER
# ==========================================
HALLUCINATION_PHRASES = {
    # YouTube / Social Media CTAs
    "thanks for watching", "thank you for watching", "thanks", "you", "watching", 
    "subscribe", "like and subscribe", "please subscribe", "subscribing",
    "please remember to click the", "don't hesitate to like", "share", "follow",
    "click the bell", "post them in the comments", "hit the like button",
    
    # Subtitle / Credit Artifacts
    "subtitles by", "subs by", "translated by", "amara.org", "amara",
    "subtitles made by the community of amara.org", "community of amara.org",
    "copyright", "all rights reserved", "mbc", "the", "video", "audio",
    "transcribed by", "otter.ai", "rev.com", "transcription by", "by bf-watch tv",
    
    # Noise / Music Descriptions
    "[silence]", "[music playing]", "[music]", "[laughter]", "[applause]",
    "music", "background music", "playing", "engine", "piano music continues",
    "noise", "blinking", "clicking", "beep", "*loud noise*", "*distorted noise*", 
    "*background noise*", "*static*", "static", "humming", "distorted",
    "(door closes)", "(wind blowing)", "(birds chirping)",
    
    # Common Short Hallucinations
    "so", "i'm fine", "the end", "to be continued", "thank you", "okay", "bye", "goodbye"
}

HALLUCINATION_PATTERNS = [
    r"subtitles? by", r"translat\w+ by", r"thank\s?you", 
    r"copyright", r"all rights", r"www\.", r"http", 
    r"like,? subscribe", r"support the show", r"click the bell",
    r"amara\.org", r"subtitles?\s+made\s+by",
    r"^\W*$" # Only non-alphanumeric characters
]

class HallucinationFilter:
    """Aggressive filter for Whisper hallucinations"""
    @staticmethod
    def is_hallucination(text: str) -> bool:
        clean = text.strip().lower()
        
        # 0. Strip filler words (ah, um, uh, etc) that STT adds
        # Don't reject entire sentence just for filler - clean it first
        filler_words = [r'^(ah|um|uh|hmm|huh|err|erm|like|you know|basically|actually|really)\s+',
                       r'\s+(ah|um|uh|hmm|huh|err|erm)\s+', r'\s+(ah|um|uh|hmm|huh|err|erm)$']
        for pattern in filler_words:
            clean = re.sub(pattern, ' ', clean, flags=re.IGNORECASE)
        clean = clean.strip()
        
        # 1. Length Filter
        if len(clean) < 2: return True
        if len(clean.split()) < 2 and clean not in ["yes", "no", "stop", "wait", "help"]:
            return True if len(clean) < 5 else False

        # 2. Exact Match Filter
        if clean in HALLUCINATION_PHRASES:
            return True
        
        # 3. Pattern Filter
        for pattern in HALLUCINATION_PATTERNS:
            if re.search(pattern, clean):
                return True
                
        # 4. Repetition Filter
        words = clean.split()
        if len(words) > 3 and all(w == words[0] for w in words):
            return True
            
        return False

# ==========================================
# PHONETIC CORRECTION
# ==========================================
class PhoneticCorrector:
    """Consolidated phonetic correction logic for Drobotics Lab"""
    @staticmethod
    def correct(text: str) -> str:
        if not text: return text
        t = text

        # 1. JUIT & Lab Brand Specifics
        t = re.sub(r'\bjute\b', 'JUIT', t, flags=re.IGNORECASE)
        t = re.sub(r'\bjuice\b', 'JUIT', t, flags=re.IGNORECASE)
        t = re.sub(r'\bj u i t\b', 'JUIT', t, flags=re.IGNORECASE)
        t = re.sub(r'\bjaypee university\b', 'JUIT', t, flags=re.IGNORECASE)
        t = re.sub(r'\brobotics lab\b', 'Drobotics Lab', t, flags=re.IGNORECASE)
        t = re.sub(r'\bdrobotics? lab\b', 'Drobotics Lab', t, flags=re.IGNORECASE)
        t = re.sub(r'\bdrove robotics\b', 'Drobotics', t, flags=re.IGNORECASE)
        t = re.sub(r'\bdrone robotics\b', 'Drobotics', t, flags=re.IGNORECASE)

        # 2. Key Figures
        t = re.sub(r'\baman sharma\b', 'Dr. Aman Sharma', t, flags=re.IGNORECASE)
        t = re.sub(r'\bvikas baghel\b', 'Dr. Vikas Baghel', t, flags=re.IGNORECASE)
        t = re.sub(r'\bshruti jain\b', 'Prof. Shruti Jain', t, flags=re.IGNORECASE)

        # 3. NVIDIA Jetson Family
        t = re.sub(r'\bjet son\b', 'Jetson', t, flags=re.IGNORECASE)
        t = re.sub(r'\bjetsen\b', 'Jetson', t, flags=re.IGNORECASE)
        t = re.sub(r'\bor an\b', 'Orin', t, flags=re.IGNORECASE)
        t = re.sub(r'\boran\b', 'Orin', t, flags=re.IGNORECASE)
        t = re.sub(r'\borin nano\b', 'Orin Nano', t, flags=re.IGNORECASE)
        t = re.sub(r'\bam peer gpu\b', 'Ampere GPU', t, flags=re.IGNORECASE)

        # 4. Raspberry Pi & Arduino
        t = re.sub(r'\braspberry pie\b', 'Raspberry Pi', t, flags=re.IGNORECASE)
        t = re.sub(r'\bpi (\d)\b', r'Pi \1', t, flags=re.IGNORECASE)
        t = re.sub(r'\bardweeno\b', 'Arduino', t, flags=re.IGNORECASE)
        t = re.sub(r'\bar do know\b', 'Arduino', t, flags=re.IGNORECASE)
        t = re.sub(r'\bgiga r1\b', 'GIGA R1', t, flags=re.IGNORECASE)

        t = re.sub(r'\bunitree go to\b', 'Unitree Go2', t, flags=re.IGNORECASE)
        t = re.sub(r'\bgo too\b', 'Go2', t, flags=re.IGNORECASE)
        t = re.sub(r'\breal sense\b', 'RealSense', t, flags=re.IGNORECASE)
        t = re.sub(r'\breal cents\b', 'RealSense', t, flags=re.IGNORECASE)
        t = re.sub(r'\br p lidar\b', 'RPLIDAR', t, flags=re.IGNORECASE)
        t = re.sub(r'\brplidar\b', 'RPLIDAR', t, flags=re.IGNORECASE)
        t = re.sub(r'\blie dar\b', 'Lidar', t, flags=re.IGNORECASE)
        
        # 6. Technical Terms
        t = re.sub(r'\bros 2\b', 'ROS2', t, flags=re.IGNORECASE)
        t = re.sub(r'\bros two\b', 'ROS2', t, flags=re.IGNORECASE)
        t = re.sub(r'\bnav 2\b', 'Nav2', t, flags=re.IGNORECASE)
        t = re.sub(r'\br viz\b', 'RViz', t, flags=re.IGNORECASE)
        t = re.sub(r'\bgaze bow\b', 'Gazebo', t, flags=re.IGNORECASE)
        t = re.sub(r'\bd o f\b', 'DOF', t, flags=re.IGNORECASE)
        t = re.sub(r'\bt o p s\b', 'TOPS', t, flags=re.IGNORECASE)
        
        # 7. Units
        t = re.sub(r'\bmeters per second\b', 'm/s', t, flags=re.IGNORECASE)
        t = re.sub(r'\brevolutions per minute\b', 'RPM', t, flags=re.IGNORECASE)

        # 4. Apply MASTER_LOOKUP logic
        if MASTER_LOOKUP:
            for key, data in MASTER_LOOKUP.items():
                canonical = data.get('canonical')
                variants = data.get('variants', [])
                for variant in variants:
                    # JUIT Rule: Do not fuzzy correct short words (<4 chars) unless critical
                    if len(variant) < 4:
                         continue
                         
                    # Only replace complete words/phrases to avoid partial matches inside other words
                    try:
                        pattern = re.compile(r'\b' + re.escape(variant) + r'\b', re.IGNORECASE)
                        if pattern.search(t):
                            t = pattern.sub(canonical, t)
                    except: continue
        
        return t

# ==========================================
# INVENTORY MANAGER
# ==========================================
class InventoryManager:
    def __init__(self, filepath=None):
        if filepath is None:
            filepath = str(INVENTORY_PATH)
        self.filepath = filepath
        self.data = self._load_data()
        
    def _load_data(self):
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                # Handle both dict and list formats
                if isinstance(data, dict):
                    return data.get('equipment', [])
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Failed to load inventory: {e}")
            return []
            
    def search(self, query):
        """Simple keyword search in inventory"""
        query = query.lower()
        results = []
        for item in self.data:
            if (query in item.get('name', '').lower() or 
                query in item.get('category', '').lower() or
                query in item.get('capabilities', '').lower()):
                results.append(item)
        return results

# ==========================================
# MAIN VOCABULARY HANDLER
# ==========================================
class VocabularyHandler:
    def __init__(self):
        self.inventory = InventoryManager()
        
    def normalize(self, text: str) -> str:
        """Apply phonetic correction"""
        return PhoneticCorrector.correct(text)
        
    def is_hallucination(self, text: str) -> bool:
        """Check if text is a likely hallucination"""
        return HallucinationFilter.is_hallucination(text)
        
    def get_system_prompt(self) -> str:
        """Return the AXIOM system prompt"""
        return SYSTEM_PROMPT
        
    def get_inventory_context(self, text: str) -> str:
        """
        Search inventory based on text and return a context string.
        Useful for RAG.
        """
        results = self.inventory.search(text)
        if not results:
            return ""
            
        context = "RELEVANT LAB EQUIPMENT:\n"
        for item in results[:3]: # Limit to top 3
            context += f"- {item['name']} ({item['category']}): {item.get('specs', '')}\n"
        return context
