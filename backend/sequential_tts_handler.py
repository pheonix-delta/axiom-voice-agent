"""
Sequential TTS Handler - Fixes Parallel Echo Issue
Ensures only ONE voice plays at a time (blocking queue)
"""
from queue import Queue
from threading import Thread, Lock
import sherpa_onnx
import os
import sounddevice as sd
import numpy as np
import logging
from config import TTS_MODEL_PATH

logger = logging.getLogger(__name__)


class SequentialTTSHandler:
    """
    TTS with sequential playback queue.
    Prevents parallel voice overlap (echo).
    
    CRITICAL FIX: User reported voices playing in parallel.
    This ensures BLOCKING playback - one at a time.
    """
    
    def __init__(self, model_dir=None):
        if model_dir is None:
            model_dir = str(TTS_MODEL_PATH)
        
        # Check if model directory exists (handles symlinks)
        model_path_obj = os.path.exists(model_dir) or os.path.islink(model_dir)
        if not model_path_obj:
            logger.warning(f"⚠️  TTS Model directory not found: {model_dir}")
            logger.warning("⚠️  TTS will be disabled (model not downloaded)")
            self.tts = None
            self.initialized = False
            self.queue = Queue()
            self.is_playing = False
            self.play_lock = Lock()
            self.worker = Thread(target=self._process_queue, daemon=True)
            self.worker.start()
            return
        
        try:
            # Initialize Kokoro TTS
            config = sherpa_onnx.OfflineTtsConfig()
            config.model.kokoro.model = os.path.join(model_dir, "model.onnx")
            config.model.kokoro.voices = os.path.join(model_dir, "voices.bin")
            config.model.kokoro.tokens = os.path.join(model_dir, "tokens.txt")
            config.model.kokoro.data_dir = os.path.join(model_dir, "espeak-ng-data")
            config.model.num_threads = 2
            config.model.debug = False
            config.model.provider = "cpu"
            
            self.tts = sherpa_onnx.OfflineTts(config)
            self.initialized = True
            logger.info("✅ TTS handler initialized")
        except Exception as e:
            logger.warning(f"⚠️  TTS initialization failed: {e}")
            self.tts = None
            self.initialized = False
        
        self.voice_id = 0
        
        # Sequential queue
        self.queue = Queue()
        self.is_playing = False
        self.play_lock = Lock()
        
        # Start worker thread
        self.worker = Thread(target=self._process_queue, daemon=True)
        self.worker.start()
    
    def speak(self, text: str, blocking: bool = False):
        """
        Add text to speech queue.
        
        Args:
            text: Text to speak
            blocking: If True, wait for this utterance to finish
        """
        if not text or len(text.strip()) == 0:
            return
        
        if not self.initialized:
            logger.warning("TTS not initialized, text will not be spoken")
            return
        
        logger.info(f"🔊 Queued: {text[:50]}...")
        self.queue.put(text)
        
        if blocking:
            # Wait for queue to empty
            self.queue.join()
    
    def _process_queue(self):
        """Worker thread - processes speech queue sequentially."""
        while True:
            text = self.queue.get()
            
            try:
                if self.initialized and self.tts is not None:
                    with self.play_lock:
                        self.is_playing = True
                        self._generate_and_play(text)
                        self.is_playing = False
                else:
                    logger.warning("TTS not initialized, skipping audio generation")
            except Exception as e:
                logger.error(f"❌ TTS Error: {e}")
            finally:
                self.queue.task_done()
    
    def _generate_and_play(self, text):
        """
        Generate audio and play it (BLOCKING).
        Critical: This must complete before next utterance.
        """
        if not self.initialized or self.tts is None:
            logger.warning("TTS not initialized, cannot generate audio")
            return
        
        logger.info(f"🗣️  Speaking: {text[:50]}...")
        
        try:
            # Generate audio
            audio = self.tts.generate(text, sid=self.voice_id, speed=1.0)
            
            if audio and len(audio.samples) > 0:
                samples = np.array(audio.samples)
                
                # BLOCKING playback - wait for finish
                sd.play(samples, audio.sample_rate)
                sd.wait()  # CRITICAL: Wait for playback to finish
                
                logger.info(f"✅ Finished speaking")
            else:
                logger.warning(f"⚠️  No audio generated for: {text[:50]}")
        except Exception as e:
            logger.error(f"Error generating/playing audio: {e}")
    
    def stop(self):
        """Immediately stop current playback and clear queue."""
        sd.stop()
        
        # Clear queue
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except:
                break
        
        print("🛑 TTS stopped and queue cleared")
    
    def is_busy(self) -> bool:
        """Check if TTS is currently speaking."""
        return self.is_playing or not self.queue.empty()
    
    def wait_until_done(self):
        """Block until all queued speech finishes."""
        self.queue.join()


# Singleton
_tts_handler = None

def get_tts_handler():
    """Get or create sequential TTS handler."""
    global _tts_handler
    if _tts_handler is None:
        _tts_handler = SequentialTTSHandler()
    return _tts_handler
