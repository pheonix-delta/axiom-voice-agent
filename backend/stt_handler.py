import sherpa_onnx
import os
import logging
from config import STT_MODEL_PATH

logger = logging.getLogger(__name__)

class STTHandler:
    def __init__(self, model_dir=None):
        if model_dir is None:
            # Use config-based path
            model_dir = str(STT_MODEL_PATH)
        
        # Check if model directory exists (handles symlinks)
        model_path_obj = os.path.exists(model_dir) or os.path.islink(model_dir)
        if not model_path_obj:
            logger.warning(f"⚠️  STT Model directory not found: {model_dir}")
            logger.warning("⚠️  STT will be disabled (model not downloaded)")
            self.recognizer = None
            self.initialized = False
            return
        
        try:
            self.recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
                encoder=os.path.join(model_dir, "encoder.int8.onnx"),
                decoder=os.path.join(model_dir, "decoder.int8.onnx"),
                joiner=os.path.join(model_dir, "joiner.int8.onnx"),
                tokens=os.path.join(model_dir, "tokens.txt"),
                num_threads=2,
                sample_rate=16000,
                feature_dim=80,
                decoding_method="greedy_search",
                debug=False,
                provider="cpu",
                model_type="nemo_transducer" # Critical fix
            )
            self.initialized = True
            logger.info("✅ STT handler initialized")
        except Exception as e:
            logger.warning(f"⚠️  STT initialization failed: {e}")
            self.recognizer = None
            self.initialized = False
        
    def transcribe(self, audio_samples):
        """
        Transcribes a numpy array of samples (float32, 16kHz).
        Returns empty string if model is not initialized.
        """
        if not self.initialized or self.recognizer is None:
            logger.warning("STT model not initialized, returning empty transcription")
            return ""
        
        stream = self.recognizer.create_stream()
        stream.accept_waveform(16000, audio_samples)
        self.recognizer.decode_stream(stream)
        return stream.result.text.strip()
