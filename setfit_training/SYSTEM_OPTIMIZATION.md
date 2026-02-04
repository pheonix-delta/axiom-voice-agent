# 🚀 AXIOM System Optimization & OOM Prevention Guide

> Practical strategies to prevent Out-of-Memory (OOM) crashes and maximize AXIOM performance on resource-constrained systems.

---

## 🎯 Overview

AXIOM was designed to run efficiently on consumer hardware, but voice AI systems with multiple ML models can still hit memory limits. This guide documents the optimization tricks, model selection rationale, and system tuning techniques used to prevent OOM crashes and ensure smooth operation.

---

## 📊 Memory Profile

### Typical Memory Footprint (Without Optimization)

```
Component                Memory      VRAM
─────────────────────────────────────────
STT (Sherpa-ONNX)        150MB      200MB
Intent (SetFit)          80MB       100MB
Template Handler         50MB       —
RAG (Embeddings)         200MB      500MB
TTS (Kokoro)             120MB      300MB
LLM (Ollama)             Variable   1-3GB
Conversation History     ~50MB      —
Python Runtime           ~100MB     —
─────────────────────────────────────────
BASELINE TOTAL:          ~750MB     ~3.6GB

Peak During Inference:   1.2-1.5GB  4-5GB
```

### With Zero-Copy Optimization

```
Component                Memory      Reduction
───────────────────────────────────────────────
Inference Memory         0.5MB      -8MB (94%)
Peak Total Memory        ~1GB       -500MB
Concurrent Users         100+       10x improvement
```

---

## 🛠️ Model Selection Rationale

### Why Sherpa-ONNX for STT?

**Decision Process**:
```
Evaluated Options:
1. Whisper (OpenAI)
   ❌ 1.5GB+ VRAM requirement
   ❌ 300-500ms latency
   ✅ High accuracy
   → Rejected: Too resource-heavy

2. Vosk
   ✅ Lightweight (~100MB)
   ❌ Lower accuracy (80-85%)
   ❌ Limited phonetic correction
   → Rejected: Accuracy issues

3. Sherpa-ONNX (Parakeet-TDT 0.6B)
   ✅ 200MB model size
   ✅ <100ms latency
   ✅ 90%+ accuracy
   ✅ ONNX format (cross-platform)
   ✅ Quantized INT8 version available
   → SELECTED ✓

4. Mozilla DeepSpeech
   ❌ Deprecated
   → Not considered
```

**Key Sherpa-ONNX Advantages**:
- **ONNX Runtime**: Optimized inference engine with hardware acceleration
- **Model Variants**: Multiple size/accuracy tradeoffs available
- **Quantization**: INT8 quantized version for 4x memory reduction
- **Cross-Platform**: Works on Linux, Windows, Mac, ARM
- **Active Development**: Regular updates and model improvements

**Python Wrapper Strategy**:
```python
# backend/stt_handler.py
from sherpa_onnx import OnlineRecognizer, OnlineRecognizerConfig

# Why Python wrapper?
# 1. Native library is C++ (fast inference)
# 2. Python bindings via pybind11 (zero-copy possible)
# 3. Integration with FastAPI ecosystem
# 4. NumPy interop for zero-copy tensor flow
```

---

### Why Kokoro for TTS?

**Decision Process**:
```
Evaluated Options:
1. Google TTS API
   ❌ Requires internet
   ❌ API costs
   ❌ Privacy concerns
   → Rejected: Not self-hosted

2. Piper TTS
   ✅ Lightweight
   ❌ Voice quality issues
   ❌ Limited voice selection
   → Rejected: Quality not meeting standards

3. Coqui TTS
   ❌ 500MB+ models
   ❌ Slow inference (500ms+)
   ✅ High quality
   → Rejected: Too slow

4. Kokoro-EN (Sherpa-ONNX based)
   ✅ 150MB model size
   ✅ <200ms latency
   ✅ Natural voice quality
   ✅ ONNX format (consistent with STT)
   ✅ Offline operation
   → SELECTED ✓
```

**Key Kokoro Advantages**:
- **Consistent Stack**: Same ONNX runtime as STT
- **Low Latency**: Sub-200ms synthesis (crucial for real-time)
- **Natural Voice**: High-quality English pronunciation
- **Sequential Queue**: Prevents audio overlap/echo
- **Memory Efficient**: Shares ONNX runtime with STT

**Implementation**:
```python
# backend/sequential_tts_handler.py
from kokoro import KokoroTTS

class SequentialTTSHandler:
    """
    Why sequential queue?
    - Prevents audio overlap when multiple responses generated
    - Memory-safe: Only one synthesis at a time
    - User experience: No jarring audio artifacts
    """
```

---

### Why Tried llama.cpp (and What We Learned)

**llama.cpp Experiment** (See `_ARCHIVED_LLAMA_CPP_20260122_172645/`):

```
Initial Attempt:
- Direct llama.cpp integration
- GGUF model loading
- C++ library with Python bindings

Issues Encountered:
1. Memory Management Complexity
   - Manual buffer management
   - GC pressure from Python↔C++ boundary
   - Harder to implement zero-copy

2. Integration Friction
   - Less mature Python bindings
   - Debugging challenges (segfaults)
   - Breaking changes across versions

3. Ecosystem Mismatch
   - Not compatible with ONNX runtime
   - Different quantization formats
   - Separate model conversion pipeline

Decision: Switched to Ollama
- Better Python integration
- Consistent with zero-copy approach
- More stable API
- Easier model management
```

**Archived Implementation**:
- `_ARCHIVED_LLAMA_CPP_20260122_172645/axiom_brain_llamacpp_backup.py`
- `_ARCHIVED_LLAMA_CPP_20260122_172645/PERFORMANCE_FIX.md`

**What We Kept**:
- Zero-copy principles still apply
- Memory optimization techniques
- Model quantization understanding

---

## 💾 OOM Prevention Strategies

### 1. zram Configuration (Compressed Swap in RAM)

**What is zram?**
- Creates compressed block device in RAM
- Acts as swap space (but faster than disk swap)
- Compresses inactive memory pages on-the-fly

**Setup zram** (Ubuntu/Debian):

```bash
# Install zram tools
sudo apt-get update
sudo apt-get install zram-config

# Check if zram is enabled
zramctl

# Manual configuration (if not using zram-config)
sudo modprobe zram
echo lz4 | sudo tee /sys/block/zram0/comp_algorithm
echo 4G | sudo tee /sys/block/zram0/disksize
sudo mkswap /dev/zram0
sudo swapon /dev/zram0 -p 10

# Verify
swapon --show
```

**Recommended zram Size**:
```
System RAM    zram Size    Rationale
──────────────────────────────────────
8GB           2-4GB        25-50% of RAM
16GB          4-8GB        25-50% of RAM
32GB+         8-16GB       Keep under 50%
```

**Why zram Helps AXIOM**:
- **Peak Load Handling**: LLM inference spikes get compressed
- **Faster than Disk Swap**: 10-100x faster access
- **No SSD Wear**: Reduces disk write cycles
- **Transparent**: OS manages automatically

**Impact on AXIOM**:
```
Without zram:
- OOM kill at ~90% RAM usage
- System freeze during peak inference
- Forced model unloading

With 4GB zram:
- Smooth operation to ~120% "effective" RAM
- Graceful degradation under load
- Background models stay loaded
```

---

### 2. System Cache Management

#### Monitoring Cache Usage

```bash
# Check current memory state
free -h

# Breakdown by cache types
cat /proc/meminfo | grep -i cache

# Per-process memory
ps aux --sort=-%mem | head -20

# AXIOM-specific check
ps aux | grep python | grep main_agent_web
```

#### Clearing Caches (When Needed)

```bash
# Drop page cache only (safe, automatic rebuild)
sudo sync && sudo sh -c 'echo 1 > /proc/sys/vm/drop_caches'

# Drop dentries and inodes (more aggressive)
sudo sync && sudo sh -c 'echo 2 > /proc/sys/vm/drop_caches'

# Drop everything (use sparingly)
sudo sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'

# AXIOM pre-start cache clear (recommended)
echo "Clearing caches before AXIOM startup..."
sudo sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
cd /home/user/Desktop/voice\ agent/axiom-voice-agent/backend
python3 main_agent_web.py
```

**When to Clear Caches**:
- ✅ Before starting AXIOM (clean slate)
- ✅ After OOM recovery
- ✅ When testing memory usage
- ❌ During active operation (causes slowdown)
- ❌ Automatically via cron (unnecessary)

---

### 3. Swap Configuration

#### Check Current Swap

```bash
swapon --show
free -h
```

#### Add Swap File (if needed)

```bash
# Create 8GB swap file
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent (edit /etc/fstab)
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Verify
swapon --show
```

#### Swap Tuning for AXIOM

```bash
# Reduce swappiness (prefer RAM over swap)
sudo sysctl vm.swappiness=10

# Make permanent
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf

# Cache pressure (balance between reclaiming page cache vs swap)
sudo sysctl vm.vfs_cache_pressure=50
echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf
```

**Recommended Settings**:
```
vm.swappiness=10           # Use swap only when necessary
vm.vfs_cache_pressure=50   # Retain directory/inode cache
vm.dirty_ratio=15          # Start background writeback at 15%
vm.dirty_background_ratio=5 # Async writeback at 5%
```

---

### 4. Model Memory Management

#### Lazy Model Loading

```python
# backend/intent_classifier.py - Example pattern
class IntentClassifier:
    def __init__(self):
        self.model = None  # Don't load on init
    
    def classify(self, text):
        if self.model is None:
            self._load_model()  # Load on first use
        return self.model.predict(text)
    
    def unload(self):
        """Free memory when not needed"""
        if self.model is not None:
            del self.model
            gc.collect()
            self.model = None
```

#### Model Unloading Strategy

```python
# Unload models during idle periods
import gc
import torch

def cleanup_memory():
    """Aggressive memory cleanup"""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
```

---

### 5. Python Garbage Collection Tuning

```python
# backend/main_agent_web.py additions
import gc

# Tune GC thresholds for AXIOM workload
gc.set_threshold(700, 10, 10)  # More aggressive collection

# Force collection after heavy operations
async def process_speech(audio):
    # ... inference code ...
    gc.collect()  # Clean up after each request
```

**Why This Helps**:
- Default Python GC is tuned for general workloads
- ML inference creates many temporary objects
- Aggressive GC prevents memory fragmentation

---

### 6. Linux OOM Killer Configuration

#### Protect AXIOM from OOM Killer

```bash
# Find AXIOM process PID
PID=$(pgrep -f "python.*main_agent_web")

# Set OOM score (lower = less likely to be killed)
echo -1000 | sudo tee /proc/$PID/oom_score_adj

# Make automatic (add to systemd service or startup script)
```

#### Monitor OOM Events

```bash
# Check OOM logs
sudo dmesg | grep -i oom
journalctl -k | grep -i oom

# Set up OOM notification
sudo apt-get install earlyoom
sudo systemctl enable --now earlyoom
```

---

## 🎛️ AXIOM-Specific Optimizations

### 1. Model Loading Order

**Optimal Startup Sequence**:
```python
# backend/main_agent_web.py - Order matters!

# 1. Load lightweight models first (fast failure)
self.intent = IntentClassifier()  # 30MB

# 2. Load STT (medium, essential)
self.stt = STTHandler()  # 200MB

# 3. Load TTS (medium, can be lazy)
self.tts = get_tts_handler()  # 150MB

# 4. Load heavy models last (optional, can skip if OOM risk)
try:
    self.llm = get_axiom_brain()  # 1-3GB
except MemoryError:
    logger.warning("LLM not loaded - using templates only")
    self.llm = None
```

---

### 2. Template-First Strategy

**Why Templates Prevent OOM**:
```
High confidence query (>0.88):
  ↓
Template lookup (50MB memory)
  ↓
NO LLM INFERENCE NEEDED
  ↓
Response in <10ms

Result: 80% of queries never load heavy LLM
```

---

### 3. Request-Level Memory Management

```python
# backend/main_agent_web.py
async def process_speech_request(audio):
    try:
        # Inference
        response = await generate_response(audio)
        return response
    finally:
        # ALWAYS cleanup, even on error
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
```

---

### 4. Conversation History Limits

```python
# backend/conversation_manager.py
class ConversationManager:
    MAX_HISTORY = 5  # FIFO limit
    
    def add_interaction(self, interaction):
        # Automatic pruning prevents unbounded growth
        if len(self.history) >= self.MAX_HISTORY:
            self.history.popleft()  # Remove oldest
        self.history.append(interaction)
```

---

## 📈 Monitoring & Alerts

### Real-Time Memory Monitoring

```bash
# Watch AXIOM memory usage
watch -n 1 'ps aux | grep python | grep main_agent_web'

# Continuous logging
while true; do
    date >> axiom_memory.log
    ps aux | grep python | grep main_agent_web >> axiom_memory.log
    sleep 5
done
```

### Memory Threshold Alerts

```python
# backend/main_agent_web.py additions
import psutil

def check_memory_threshold():
    """Alert if memory usage high"""
    mem = psutil.virtual_memory()
    if mem.percent > 85:
        logger.warning(f"High memory usage: {mem.percent}%")
        # Trigger cleanup
        gc.collect()
        torch.cuda.empty_cache()
```

---

## 🚨 Emergency OOM Recovery

### If AXIOM Crashes with OOM

```bash
# 1. Check OOM logs
sudo dmesg | tail -50 | grep -i oom

# 2. Clear caches
sudo sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'

# 3. Restart with reduced model
cd /home/user/Desktop/voice\ agent/axiom-voice-agent/backend
python3 main_agent_web.py --skip-llm  # Use templates only

# 4. Or reduce LLM context
export AXIOM_CONTEXT_LENGTH=1024  # Instead of 2048
python3 main_agent_web.py
```

### Gradual Resource Increase

```bash
# Start with minimal config
python3 main_agent_web.py --template-only

# If stable, add STT + Intent
python3 main_agent_web.py --skip-llm

# If stable, add LLM
python3 main_agent_web.py  # Full stack
```

---

## 📋 Pre-Start Checklist

**Before Starting AXIOM**:

```bash
# 1. Check available memory
free -h
# Goal: At least 2GB free

# 2. Clear caches
sudo sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'

# 3. Verify zram active
zramctl
# Goal: zram0 present with 2-4GB

# 4. Check swap
swapon --show
# Goal: At least 4GB swap available

# 5. Close unnecessary apps
# Close browsers, IDEs, etc.

# 6. Start AXIOM
cd /home/user/Desktop/voice\ agent/axiom-voice-agent/backend
python3 main_agent_web.py
```

---

## 🎓 Key Takeaways

### What We Did to Prevent OOM

1. **Zero-Copy Inference**: 94% memory reduction per request
2. **zram**: 4GB compressed swap for peak handling
3. **Template-First**: 80% queries bypass heavy LLM
4. **Lazy Loading**: Models load only when needed
5. **Aggressive GC**: Tuned garbage collection
6. **FIFO Limits**: Conversation history capped at 5
7. **Smart Model Selection**: Chose lightweight Sherpa-ONNX over Whisper
8. **Request Cleanup**: Memory freed after each inference

### Model Selection Philosophy

- **STT**: Sherpa-ONNX (balance of speed/accuracy/memory)
- **TTS**: Kokoro (consistent ONNX stack)
- **Intent**: SetFit (30MB, lightning fast)
- **LLM**: Ollama (better Python integration than llama.cpp)

### Memory Budget

```
Target System: 8GB RAM
─────────────────────────────
OS + Services:     2GB
AXIOM Baseline:    1GB
Peak Inference:    1.5GB
zram Buffer:       4GB (compressed)
─────────────────────────────
Total Effective:   ~10GB

Result: Smooth operation on consumer hardware ✓
```

---

## 🔗 Related Documentation

- [QUICK_START.md](QUICK_START.md) - Installation & basic usage
- [FEATURES.md - Zero-Copy Inference](FEATURES.md#-zero-copy-inference-direct-tensor-streaming) - Memory optimization details
- [PATH_FIX_SUMMARY.md](PATH_FIX_SUMMARY.md) - Path configurations

---

**Next Steps**: Start AXIOM with optimizations applied → [QUICK_START.md](QUICK_START.md)
