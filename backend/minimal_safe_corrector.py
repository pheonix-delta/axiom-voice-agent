"""
Minimal Safe Corrector - Only fixes formatting, NOT content
Principle: If unsure, don't touch it. Better wrong word than changing user's meaning.
"""
import re
import logging

logger = logging.getLogger(__name__)


class MinimalSafeCorrector:
    """
    Ultra-conservative correction: ONLY fix obvious formatting issues.
    
    NEVER changes:
    - User's words (even if they sound wrong)
    - Contractions (I'm, you're, etc.)
    - Names or proper nouns
    
    ONLY fixes:
    - Markdown artifacts (**bold**, `code`)
    - Unit abbreviations (5m → 5 meters, 10gb → 10GB)
    - Noise tags ([Music], [Applause])
    """
    
    def __init__(self):
        # Only critical technical abbreviations
        self.unit_fixes = {
            r'\b(\d+)\s*m\b': r'\1 meters',  # 5m → 5 meters
            r'\b(\d+)\s*km\b': r'\1 kilometers',
            r'\b(\d+)\s*cm\b': r'\1 centimeters',
            r'\b(\d+)\s*mm\b': r'\1 millimeters',
            r'\b(\d+)\s*gb\b': r'\1 GB',  # Capitalize
            r'\b(\d+)\s*mb\b': r'\1 MB',
            r'\b(\d+)\s*kb\b': r'\1 KB',
            r'\b(\d+)\s*hz\b': r'\1 Hz',
            r'\b(\d+)\s*mhz\b': r'\1 MHz',
            r'\b(\d+)\s*ghz\b': r'\1 GHz',
            r'\b(\d+)\s*fps\b': r'\1 FPS',
            r'\b(\d+)\s*tops\b': r'\1 TOPS',
        }
    
    def correct_stt(self, text: str) -> str:
        """
        Minimal STT correction: ONLY remove noise tags.
        Do NOT change any words - let semantic search handle it.
        """
        if not text:
            return text
        
        original = text
        
        # Remove noise tags only
        text = re.sub(r'\[.*?\]', '', text)  # [Music], [Noise], etc.
        text = text.strip()
        
        if text != original:
            logger.info(f"[Minimal STT] Removed noise: '{original}' → '{text}'")
        
        return text
    
    def correct_response(self, text: str) -> str:
        """
        Minimal response correction for TTS:
        1. Remove markdown
        2. Fix unit abbreviations
        3. Clean spacing
        
        Do NOT touch contractions or word content.
        """
        if not text:
            return text
        
        original = text
        
        # 1. Remove markdown (interferes with TTS)
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # **bold**
        text = re.sub(r'\*(.+?)\*', r'\1', text)      # *italic*
        text = re.sub(r'`(.+?)`', r'\1', text)         # `code`
        text = re.sub(r'#{1,6}\s+', '', text)          # # Headers
        
        # 2. Fix units (case-insensitive)
        for pattern, replacement in self.unit_fixes.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # 3. Clean excessive spaces
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        if text != original:
            logger.info(f"[Minimal Response] '{original}' → '{text}'")
        
        return text


# Singleton
_safe_corrector = None

def get_safe_corrector():
    """Get minimal safe corrector."""
    global _safe_corrector
    if _safe_corrector is None:
        _safe_corrector = MinimalSafeCorrector()
    return _safe_corrector


if __name__ == "__main__":
    corrector = MinimalSafeCorrector()
    
    print("="*80)
    print("MINIMAL SAFE CORRECTOR TEST")
    print("="*80)
    
    # STT tests (should barely change anything)
    stt_tests = [
        "[Music] Tell me about the chancellor",  # Remove tag only
        "What is the arduino giga",              # Keep as-is
        "Tell me about jetson orin nano",        # Keep as-is
    ]
    
    print("\nSTT Correction (minimal):")
    for test in stt_tests:
        result = corrector.correct_stt(test)
        print(f"  IN:  {test}")
        print(f"  OUT: {result}")
        print()
    
    # Response tests (only formatting)
    response_tests = [
        "The Jetson has **40 TOPS** of power",   # Remove markdown
        "It weighs 5m and costs $100",           # Fix units
        "I'm working on it",                     # Keep contraction
        "The Arduino Giga is great",             # Keep as-is
    ]
    
    print("\nResponse Correction (formatting only):")
    for test in response_tests:
        result = corrector.correct_response(test)
        print(f"  IN:  {test}")
        print(f"  OUT: {result}")
        print()
    
    print("="*80)
