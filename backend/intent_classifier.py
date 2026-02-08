import json
import os
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from safetensors.torch import load_file
from config import INTENT_CLASSIFIER_PATH

logger = logging.getLogger(__name__)

class ManualLogisticHead:
    """Manual implementation of Logistic Regression inference using tensors."""
    def __init__(self, weights, intercept, classes):
        self.weights = weights
        self.intercept = intercept
        self.classes = classes

    def predict_proba(self, embeddings):
        # embeddings shape: (n_samples, n_features)
        # weights shape: (n_classes, n_features)
        # intercept shape: (n_classes,)
        
        # Linear part: XW^T + b
        logits = np.dot(embeddings, self.weights.T) + self.intercept
        
        # Softmax for multi-class probability
        exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
        return probs

class IntentClassifier:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = str(INTENT_CLASSIFIER_PATH)
        
        if not os.path.exists(model_path):
            logger.warning(f"⚠️  Intent classifier model not found at: {model_path}")
            self.model = None
            self.head = None
            self.labels = []
            self.initialized = False
            return
        
        try:
            # 1. Load labels from config_setfit.json
            config_path = os.path.join(model_path, "config_setfit.json")
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.labels = config.get("labels", [])
            
            # 2. Load the transformer body (SentenceTransformer)
            # This part already uses model.safetensors internally
            self.model = SentenceTransformer(model_path)
            
            # 3. Load the head (Safetensors primary, Pickle fallback)
            safetensors_head = os.path.join(model_path, "model_head.safetensors")
            pickle_head = os.path.join(model_path, "model_head.pkl")
            
            if os.path.exists(safetensors_head):
                logger.info(f"🛡️  Loading secure safetensors head: {safetensors_head}")
                data = load_file(safetensors_head)
                self.head = ManualLogisticHead(
                    weights=data["weights"].numpy(),
                    intercept=data["intercept"].numpy(),
                    classes=data["classes"].numpy()
                )
            elif os.path.exists(pickle_head):
                logger.warning(f"⚠️  Loading legacy pickle head: {pickle_head}")
                import joblib
                legacy_model = joblib.load(pickle_head)
                self.head = ManualLogisticHead(
                    weights=legacy_model.coef_,
                    intercept=legacy_model.intercept_,
                    classes=legacy_model.classes_
                )
            else:
                raise FileNotFoundError("No model head found (neither .safetensors nor .pkl)")

            self.initialized = True
            logger.info(f"✅ Intent classifier initialized with {len(self.labels)} labels using Manual Safetensors Head")
        except Exception as e:
            logger.error(f"❌ Intent classifier initialization failed: {e}")
            self.model = None
            self.head = None
            self.labels = []
            self.initialized = False
        
    def predict(self, text):
        if not self.initialized or self.model is None or self.head is None:
            logger.warning("Intent classifier not initialized, returning default intent")
            return {"intent": "unknown", "confidence": 0.0}
        
        # Get embeddings from SentenceTransformer body
        embeddings = self.model.encode([text], show_progress_bar=False)
        
        # Get probabilities from manual head
        probs = self.head.predict_proba(embeddings)[0]
        
        max_prob = max(probs)
        label_id = probs.argmax().item()
        label = self.labels[label_id]
        
        return {
            "intent": label,
            "confidence": float(max_prob)
        }
