import json
import os
import logging
from setfit import SetFitModel
from rapidfuzz import process, fuzz
from config import INTENT_CLASSIFIER_PATH

logger = logging.getLogger(__name__)

class IntentClassifier:
    def __init__(self, model_path=None):
        if model_path is None:
            # Use config-based path
            model_path = str(INTENT_CLASSIFIER_PATH)
        
        # Check if model exists
        if not os.path.exists(model_path):
            logger.warning(f"⚠️  Intent classifier model not found at: {model_path}")
            self.model = None
            self.labels = []
            self.initialized = False
            return
        
        try:
            # Load with local_files_only to prevent HuggingFace lookup
            self.model = SetFitModel.from_pretrained(model_path, local_files_only=True)
            # Use labels directly from the model
            self.labels = self.model.labels
            self.initialized = True
            logger.info(f"✅ Intent classifier initialized with {len(self.labels)} intent labels")
        except Exception as e:
            logger.warning(f"⚠️  Intent classifier initialization failed: {e}")
            self.model = None
            self.labels = []
            self.initialized = False
        
    def predict(self, text):
        # Text is assumed to be normalized by VocabularyHandler before reaching here
        if not self.initialized or self.model is None:
            logger.warning("Intent classifier not initialized, returning default intent")
            return {
                "intent": "unknown",
                "confidence": 0.0
            }
        
        probs = self.model.predict_proba([text])[0]
        max_prob = max(probs)
        label_id = probs.argmax().item()
        label = self.labels[label_id]
        
        return {
            "intent": label,
            "confidence": float(max_prob)
        }
