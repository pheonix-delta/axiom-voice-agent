import numpy as np
import onnxruntime as ort
import os
import logging
from typing import Tuple, Optional
from config import VAD_MODEL_PATH

logger = logging.getLogger(__name__)

class VadHandler:
    """
    Silero VAD (Voice Activity Detection) Handler
    Processes float32 audio at 16kHz and returns speech probability.
    """
    
    def __init__(self, model_path=None, threshold=0.5, sample_rate=16000):
        """
        Initialize Silero VAD model.
        
        Args:
            model_path: Path to silero_vad.onnx model
            threshold: Speech detection threshold (0.0-1.0)
            sample_rate: Audio sample rate (must be 16000 for Silero)
        """
        if model_path is None:
            model_path = str(VAD_MODEL_PATH)
        
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.initialized = False
        
        # Check if model exists
        if not os.path.exists(model_path):
            logger.warning(f"[VAD] Model not found at: {model_path}")
            logger.warning("[VAD] VAD will be disabled (model not downloaded)")
            self.session = None
            return
        
        # Load ONNX model
        try:
            self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
            logger.info(f"[VAD] Loaded Silero VAD model from {model_path}")
            self.initialized = True
        except Exception as e:
            logger.warning(f"[VAD] Failed to load model: {e}")
            self.session = None
            return
            
        # Initialize state for stateful model
        self._reset_states()
        
        # Speech state tracking
        self.is_speech = False
        self.speech_frames = 0
        self.silence_frames = 0
        
        # Hysteresis parameters (prevent flickering)
        self.min_speech_frames = 3  # Need 3 consecutive frames to trigger speech
        self.min_silence_frames = 10  # Need 10 frames to end speech
        
    def _reset_states(self):
        """Reset model internal states (h, c)"""
        self.h = np.zeros((2, 1, 64), dtype=np.float32)
        self.c = np.zeros((2, 1, 64), dtype=np.float32)
        self.sr = np.array([self.sample_rate], dtype=np.int64)
        
    def process_chunk(self, audio_chunk: np.ndarray) -> Tuple[float, bool]:
        """
        Process audio chunk and return speech probability.
        
        Args:
            audio_chunk: Float32 numpy array (normalized -1.0 to 1.0)
                        Must be exactly 512 samples (32ms at 16kHz) for Silero VAD
        
        Returns:
            Tuple of (probability, is_speech):
                - probability: Float 0.0-1.0 indicating speech likelihood
                - is_speech: Boolean indicating current speech state
        """
        # If VAD not initialized, always return "speech detected"
        if not self.initialized or self.session is None:
            return 1.0, True
        
        try:
            # Validate input
            if not isinstance(audio_chunk, np.ndarray):
                raise ValueError("Audio chunk must be numpy array")
            
            if audio_chunk.dtype != np.float32:
                logger.warning(f"[VAD] Converting audio from {audio_chunk.dtype} to float32")
                audio_chunk = audio_chunk.astype(np.float32)
            
            # Silero VAD requires exactly 512 samples
            if len(audio_chunk) != 512:
                # If chunk is too large, process in 512-sample windows
                if len(audio_chunk) > 512:
                    # Take first 512 samples for this iteration
                    audio_chunk = audio_chunk[:512]
                else:
                    # Pad if too small
                    audio_chunk = np.pad(audio_chunk, (0, 512 - len(audio_chunk)), mode='constant')
            
            # Ensure correct shape (batch=1, samples=512)
            audio_chunk = audio_chunk.reshape(1, 512)
            
            # Run inference with correct input/output names
            ort_inputs = {
                'x': audio_chunk,
                'h': self.h,
                'c': self.c
            }
            
            ort_outs = self.session.run(None, ort_inputs)
            probability = float(ort_outs[0][0][0])  # Extract scalar from 'prob' output
            
            # Update states for next iteration (new_h, new_c)
            self.h = ort_outs[1]
            self.c = ort_outs[2]
            
            # Update speech state with hysteresis
            if probability >= self.threshold:
                self.speech_frames += 1
                self.silence_frames = 0
                
                if self.speech_frames >= self.min_speech_frames:
                    if not self.is_speech:
                        logger.info(f"[VAD] 🎤 Speech STARTED (prob: {probability:.3f})")
                    self.is_speech = True
            else:
                self.silence_frames += 1
                self.speech_frames = 0
                
                if self.silence_frames >= self.min_silence_frames:
                    if self.is_speech:
                        logger.info(f"[VAD] 🔇 Speech ENDED (prob: {probability:.3f})")
                    self.is_speech = False
            
            return probability, self.is_speech
            
        except Exception as e:
            logger.error(f"[VAD] Processing error: {e}")
            return 0.0, False
    
    def validate_audio_format(self, audio_int16: np.ndarray) -> None:
        """
        Validate int16 audio format and log conversion details.
        
        Args:
            audio_int16: Audio in int16 format (for validation logging)
        """
        logger.debug(f"[VAD FORMAT CHECK]")
        logger.debug(f"  Input dtype: {audio_int16.dtype}")
        logger.debug(f"  Input shape: {audio_int16.shape}")
        logger.debug(f"  Input range: [{audio_int16.min()}, {audio_int16.max()}]")
        
        # Convert to float32
        audio_float32 = audio_int16.astype(np.float32) / 32768.0
        
        logger.debug(f"  Output dtype: {audio_float32.dtype}")
        logger.debug(f"  Output range: [{audio_float32.min():.4f}, {audio_float32.max():.4f}]")
        logger.debug(f"  ✓ Conversion: int16 → float32 successful")
    
    def reset(self):
        """Reset VAD state (call when starting new audio stream)"""
        if self.initialized and self.session is not None:
            self._reset_states()
        self.is_speech = False
        self.speech_frames = 0
        self.silence_frames = 0
        if self.initialized:
            logger.info("[VAD] State reset")
        else:
            logger.debug("[VAD] Not initialized, skipping reset")
