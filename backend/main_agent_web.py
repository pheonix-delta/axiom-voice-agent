
import sys
import asyncio
import numpy as np
import warnings
import json
import logging
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Suppress FutureWarnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")
warnings.filterwarnings("ignore", message=".*torch.utils._pytree.*")

# Import handlers
from stt_handler import STTHandler
from intent_classifier import IntentClassifier
from sequential_tts_handler import get_tts_handler  # NEW: Sequential TTS
from vocabulary_handler import VocabularyHandler
from vad_handler import VadHandler
from keyword_mapper import KeywordMapper
from model_3d_mapper import Model3DMapper
from axiom_brain import get_axiom_brain  # NEW: Direct GGUF inference (no Ollama)
from conversation_orchestrator import ConversationOrchestrator
# Minimal safe corrector - only formatting, no content changes
from minimal_safe_corrector import get_safe_corrector
from template_responses import get_template_handler  # NEW: Template-based bypass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Suppress Warnings
warnings.filterwarnings("ignore")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import config paths
from config import ASSETS_3D_PATH, ASSETS_DIR, FRONTEND_HTML, FRONTEND_JS

# Serve 3D assets
app.mount("/3d v2", StaticFiles(directory=str(ASSETS_3D_PATH)), name="3d_models")
# Serve general assets (images, etc)
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

@app.get("/")
async def get():
    return FileResponse(str(FRONTEND_HTML))

@app.get("/audio-capture-processor.js")
async def get_audio_processor():
    return FileResponse(str(FRONTEND_JS), media_type='application/javascript')

# Agent Class
class AxiomWebAgent:
    def __init__(self):
        logger.info("=" * 80)
        logger.info("🚀 AXIOM WEB AGENT - Initializing with Semantic RAG")
        logger.info("=" * 80)
        
        # Initialize all handlers
        self.stt = STTHandler()
        self.intent = IntentClassifier()
        self.tts = get_tts_handler()  # NEW: Sequential TTS queue
        self.vocab = VocabularyHandler()
        self.vad = VadHandler(threshold=0.5)
        self.keyword_mapper = KeywordMapper()
        self.model_3d_mapper = Model3DMapper(models_dir="3d")
        
        # NEW: Direct GGUF inference (replaces Ollama)
        self.llm = get_axiom_brain()
        self.orchestrator = ConversationOrchestrator()
        # Minimal safe corrector for both STT and responses
        self.safe_corrector = get_safe_corrector()
        self.template_handler = get_template_handler()  # NEW: 2,116 templates
        
        logger.info("✅ All modules initialized (llama-cpp-python loaded)")
        logger.info("✅ Template handler: 2,116 instant responses")
        logger.info("=" * 80)

    async def query_llm(self, user_text, intent):
        """
        Direct GGUF inference in async context.
        Replaces Ollama HTTP calls.
        """
        try:
            # Run blocking LLM call in thread to avoid blocking event loop
            response = await asyncio.to_thread(
                self.orchestrator.query_with_context,
                intent=intent,
                text=user_text
            )
            return response
        except Exception as e:
            logger.error(f"[LLM] Error: {e}")
            return "System error."

    def process_audio_chunk(self, audio_bytes):
        """
        Convert raw Int16 bytes from WebSocket to Float32 for processing.
        Ensures exactly 512 samples for VAD compatibility.
        """
        # Convert bytes to int16 numpy array
        audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
        
        # Silero VAD requires exactly 512 samples
        if len(audio_int16) != 512:
            if len(audio_int16) > 512:
                audio_int16 = audio_int16[:512]
            else:
                audio_int16 = np.pad(audio_int16, (0, 512 - len(audio_int16)), mode='constant')
        
        # Convert to float32 (normalize to -1.0 to 1.0)
        audio_float32 = audio_int16.astype(np.float32) / 32768.0
        
        return audio_float32, audio_int16

agent = AxiomWebAgent()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔌 Client Connected")
    
    # Session State
    audio_buffer = []
    vad_audio_chunks = []
    is_speaking = False
    processing_lock = False  # NEW: Prevents audio processing during thinking/speaking
    
    # Reset VAD state for new connection
    agent.vad.reset()
    
    try:
        while True:
            message = await websocket.receive()
            
            if "bytes" in message:
                # ============================================
                # STREAMING AUDIO CHUNKS - VAD PROCESSING
                # ============================================
                
                # CRITICAL FIX: Ignore audio if backend is processing
                if processing_lock:
                    # Silently drop audio chunks while backend is busy
                    continue
                
                data = message["bytes"]
                
                # Convert to float32 for VAD
                audio_float32, audio_int16 = agent.process_audio_chunk(data)
                
                # Process through VAD
                probability, vad_is_speech = agent.vad.process_chunk(audio_float32)
                
                # Speech started
                if vad_is_speech and not is_speaking:
                    is_speaking = True
                    audio_buffer = []
                    await websocket.send_json({"event": "speech_start"})
                    logger.info(f"[VAD] 🎤 Speech START detected")
                
                # Accumulate audio during speech
                if is_speaking:
                    audio_buffer.append(data)
                
                # Speech ended
                if not vad_is_speech and is_speaking:
                    is_speaking = False
                    processing_lock = True  # LOCK: Prevent new audio until we're done
                    await websocket.send_json({"event": "speech_end"})
                    logger.info(f"[VAD] 🔇 Speech END detected - LOCKING audio input")
                    
                    # Process accumulated audio
                    if audio_buffer:
                        await process_speech(websocket, audio_buffer)
                        audio_buffer = []
                        
                        # UNLOCK: Tell frontend we're ready to listen again
                        processing_lock = False
                        await websocket.send_json({"event": "ready_to_listen", "state": "idle"})
                        logger.info(f"[VAD] 🎤 UNLOCKED - Ready for new input")
                
            elif "text" in message:
                # Handle text events from client
                data = json.loads(message["text"])
                event = data.get("event")
                
                if event == "client_ready":
                    logger.info("[Client] Ready signal received")
                    await websocket.send_json({"state": "idle"})

    except WebSocketDisconnect:
        logger.info("🔌 Client Disconnected")
    except Exception as e:
        logger.error(f"[WebSocket] Error: {e}", exc_info=True)
        await websocket.close()

async def process_speech(websocket: WebSocket, audio_buffer):
    """
    Process complete speech segment through the full pipeline:
    1. STT (Parakeet) - ASYNC wrapped
    2. Hallucination filter
    3. Phonetic correction
    4. Intent classification (SetFit) - ASYNC wrapped
    5. Keyword detection → Card triggering
    6. 3D model topic detection
    7. LLM response (llama-cpp-python) - ASYNC wrapped
    8. TTS (Kokoro) - SEQUENTIAL queue
    """
    try:
        logger.info("\n" + "="*80)
        logger.info("🧠 PROCESSING SPEECH SEGMENT")
        logger.info("="*80)
        
        await websocket.send_json({"state": "thinking"})
        
        # Combine all audio chunks (int16 bytes)
        full_audio_bytes = b"".join(audio_buffer)
        
        # Convert entire buffer to float32 for STT
        full_audio_int16 = np.frombuffer(full_audio_bytes, dtype=np.int16)
        full_audio_float32 = full_audio_int16.astype(np.float32) / 32768.0
        
        logger.info(f"[Audio Buffer] Collected {len(full_audio_int16)} samples ({len(full_audio_int16)/16000:.2f}s)")
        
        # ============================================
        # STEP 1: STT (Speech-to-Text) - ASYNC
        # ============================================
        text = await asyncio.to_thread(agent.stt.transcribe, full_audio_float32)
        logger.info(f"[📝 Parakeet STT] Raw: \"{text}\"")
        
        # Filter out filler sounds (uh, um, ah) and very short utterances
        text = text.strip()
        filler_words = {'uh', 'um', 'ah', 'eh', 'hmm', 'oh', 'ok', 'okay', 'yeah', 'yep', 'nope', 'mm'}
        word_count = len(text.split())
        
        if not text:
            logger.warning("[STT] Empty transcription")
            await websocket.send_json({"state": "idle"})
            return
        
        if word_count == 1 and text.lower() in filler_words:
            logger.warning(f"[STT] Filler sound ignored: '{text}'")
            await websocket.send_json({"state": "idle"})
            return
        
        # ============================================
        # STEP 2: Hallucination Filter (before correction)
        # ============================================
        if agent.vocab.is_hallucination(text):
            logger.warning(f"[❌ Hallucination] Ignored: \"{text}\"")
            await websocket.send_json({"state": "idle"})
            return
        
        # ============================================
        # STEP 3: Intent Classification (SetFit) - ASYNC (do this BEFORE correction)
        # ============================================
        intent_res = await asyncio.to_thread(agent.intent.predict, text)
        logger.info(f"[🎯 SetFit] Intent: {intent_res['intent']} (confidence: {intent_res.get('confidence', 0):.2f})")
        
        # ============================================
        # STEP 4: Minimal STT Correction (noise removal only)
        # Do NOT change user's words - semantic search handles variations
        # ============================================
        corrected_text = agent.safe_corrector.correct_stt(text)
        if corrected_text != text:
            logger.info(f"[🔧 Minimal STT] \"{text}\" → \"{corrected_text}\"")
        text = corrected_text
        
        # ============================================
        # STEP 5: Vocabulary Normalization
        # ============================================
        normalized_text = agent.vocab.normalize(text)
        
        # ============================================
        # STEP 6nfo(f"[🎯 SetFit] Intent: {intent_res['intent']} (confidence: {intent_res.get('confidence', 0):.2f})")
        
        # ============================================
        # STEP 5: Keyword Detection → Card Trigger
        # ============================================
        keyword_match = agent.keyword_mapper.detect_keyword(normalized_text)
        if keyword_match:
            card_idx, matched_keyword = keyword_match
            product_name = agent.keyword_mapper.get_product_name(card_idx)
            logger.info(f"[🎯 KEYWORD TRIGGER] Card {card_idx}: {product_name}")
            
            # Send card trigger event to frontend
            await websocket.send_json({
                "event": "trigger_card",
                "card_index": card_idx,
                "keyword": matched_keyword,
                "product_name": product_name
            })
        
        # ============================================
        # STEP 6: 3D Model Topic Detection
        # ============================================
        model_info = agent.model_3d_mapper.process_text(normalized_text)
        if model_info:
            logger.info(f"[🎨 3D Model] Loading: {model_info['model_name']}")
            
            # Send 3D model event to frontend
            await websocket.send_json({
                "event": "load_3d_model",
                "model_path": model_info['model_path'],
                "model_name": model_info['model_name']
            })
        
        # ============================================
        # STEP 6.5: Template Response Bypass (NEW!)
        # ============================================
        # Try template response first (saves GPU, <10ms)
        confidence = intent_res.get('confidence', 0)
        use_template = agent.template_handler.should_use_template(
            intent_res['intent'],
            confidence,
            normalized_text
        )
        
        response_text = None
        if use_template:
            response_text = agent.template_handler.get_template_response(
                intent_res['intent'],
                normalized_text
            )
            if response_text:
                logger.info(f"[⚡ TEMPLATE] Bypassed LLM (confidence: {confidence:.2f})")
                logger.info(f"[⚡ Response] {response_text}")
        
        # ============================================
        # STEP 7: LLM Response (llama-cpp-python) - ASYNC
        # ============================================
        if not response_text:
            response_text = await agent.query_llm(normalized_text, intent_res['intent'])
            logger.info(f"[🤖 LLM Response] {response_text}")
        
        # ============================================
        # STEP 7.5: Minimal Response Correction (formatting only)
        # ============================================
        # Clean up markdown and units for TTS - do NOT change words
        corrected_response = agent.safe_corrector.correct_response(response_text)
        if corrected_response != response_text:
            logger.info(f"[🔧 Minimal Response] \"{response_text}\" → \"{corrected_response}\"")
        response_text = corrected_response
        
        # ============================================
        # STEP 8: TTS (Text-to-Speech) - GENERATE FIRST, THEN SPEAK
        # ============================================
        # Generate TTS audio BEFORE changing state to 'speaking'
        audio_bytes = await asyncio.to_thread(
            agent.tts.tts.generate,
            response_text,
            sid=0,
            speed=1.0
        )
        
        if audio_bytes and len(audio_bytes.samples) > 0:
            # Convert to WAV for browser
            import io
            import wave
            samples_int16 = (np.array(audio_bytes.samples, dtype=np.float32) * 32767).astype(np.int16)
            
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(audio_bytes.sample_rate)
                wav_file.writeframes(samples_int16.tobytes())
            
            # NOW switch to speaking state RIGHT BEFORE sending audio
            # This ensures animation and audio start together
            await websocket.send_json({
                "state": "speaking",
                "text": response_text,
                "intent": intent_res['intent']
            })
            
            # Send WAV bytes to browser immediately after state change
            try:
                await websocket.send_bytes(wav_buffer.getvalue())
            except Exception as e:
                logger.error(f"[TTS] Failed to send audio: {e}")
        
        logger.info("="*80)
        logger.info("✅ PROCESSING COMPLETE\n")
        
        # DON'T send idle here - frontend will handle it after TTS playback finishes
        # This prevents microphone from being re-enabled while TTS is still playing
        
        
    except Exception as e:
        logger.error(f"[Processing] Error: {e}", exc_info=True)
        try:
            await websocket.send_json({"state": "idle", "error": str(e)})
        except:
            pass  # Connection already closed

if __name__ == "__main__":
    import uvicorn
    # Debug: Print all registered routes
    logger.info("📍 Registered routes:")
    for route in app.routes:
        logger.info(f"   {route.path} - {type(route).__name__}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
