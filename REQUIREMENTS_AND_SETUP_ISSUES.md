# Requirements & Setup Guide

> **New Users Start Here!** This guide will get you up and running in 5 minutes.

---

## 🚀 Quick Setup (Complete Installation)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/axiom-voice-agent.git
cd axiom-voice-agent
```

### Step 2: Create Virtual Environment

**Option A: Fresh Virtual Environment (Recommended)**
```bash
# Create new venv
python3 -m venv axiomvenv

# Activate it
source axiomvenv/bin/activate  # Linux/Mac
# OR
axiomvenv\Scripts\activate  # Windows

# Verify activation (should show venv path)
which python
```

**Option B: Using Existing Virtual Environment**
```bash
# If you already have a venv, activate it
source /path/to/your/existing/venv/bin/activate  # Linux/Mac

# Verify you're in the venv
which python  # Should show path to your venv python
```

**Troubleshooting venv:**
```bash
# If python3 -m venv doesn't work, install venv:
sudo apt-get install python3-venv  # Ubuntu/Debian
# OR
yum install python3-venv  # CentOS/RHEL
# OR
brew install python  # macOS (includes venv)
```

### Step 3: Install Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements (avoid --break-system-packages; use the venv)
pip install -r requirements.txt

# Verify core packages installed
python -c "import torch, setfit, fastapi; print('✅ Core packages installed!')"
```

**If you see "ModuleNotFoundError":**
Some dependencies might be missing from requirements.txt. Install them manually:
```bash
pip install torch transformers huggingface-hub rapidfuzz librosa scipy pydub
```

### Step 4: Configure Ollama (LLM Backend)

AXIOM uses **Ollama** for serving the fine-tuned LLM. Follow these steps:

```bash
# 1. Install Ollama (if not already installed)
# Visit: https://ollama.ai/download
# Or use quick install:
curl -fsSL https://ollama.ai/install.sh | sh  # Linux

# 2. Start Ollama service
ollama serve  # Keep this running in a separate terminal

# 3. Pull base model OR create your fine-tuned model
# Option A: Use base Mistral
ollama pull mistral

# Option B: If you have drobotics_test.gguf fine-tuned model
# Place Modelfile in project root, then:
ollama create drobotics_test -f Modelfile

# 4. Set environment variable (optional)
export AXIOM_MODEL=drobotics_test  # Or "mistral" if using base
```

### Step 5: Run the System
```bash
cd backend
python main_agent_web.py
```

You should see:
```
✅ Using Ollama model: drobotics_test
✅ Intent Classifier loaded
✅ VAD model loaded  
✅ TTS model ready
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 6: Open Browser
```
http://localhost:8000
```

**Success! 🎉** You should see the voice interface with the 3D equipment carousel.

---

## 📦 Pre-trained Models (Already Included!)

**Good news!** All AI models are **pre-included** in the repository:

```
models/
├── intent_model/
│   └── setfit_intent_classifier/    # ✅ Intent detection (87 MB, 94% accuracy)
├── silero_vad.onnx                  # ✅ Voice Activity Detection (40 MB)
├── kokoro-en-v0_19/                 # ✅ Text-to-Speech (150 MB)
├── sherpa-onnx-nemo-parakeet.../    # ✅ Speech-to-Text (200 MB)
└── drobotics_test.gguf              # ✅ Fine-tuned LLM (~4.5 GB, served via Ollama)
```

**No downloads during runtime!** Everything loads from local files.

---

## 🔧 Dependency Reference

All packages should be in `requirements.txt`. If you encounter errors, here's what each does:

| Package                | Purpose                  | Critical? |
| :--------------------- | :----------------------- | :-------- |
| `torch`                | Deep learning backend    | **YES**   |
| `transformers`         | HuggingFace models       | **YES**   |
| `huggingface-hub`      | Model loading            | **YES**   |
| `setfit`               | Intent classification    | **YES**   |
| `sentence-transformers`| Embeddings               | **YES**   |
| `fastapi`              | Web framework            | **YES**   |
| `uvicorn`              | ASGI server              | **YES**   |
| `websockets`           | Real-time communication  | **YES**   |
| `ollama`               | LLM serving              | **YES**   |
| `sherpa-onnx`          | Speech-to-text           | **YES**   |
| `onnxruntime`          | Model inference          | **YES**   |
| `rapidfuzz`            | Fuzzy matching           | **YES**   |
| `librosa`              | Audio processing         | **YES**   |
| `scipy`                | Audio signal processing  | **YES**   |
| `pydub`                | Audio format conversion  | **YES**   |
| `sounddevice`          | Audio I/O                | Optional  |
| `pygame`               | Audio playback fallback  | Optional  |
| `pyaudio`              | Mic input fallback       | Optional  |

---

## ⚠️ Common Issues & Solutions

### Issue 1: "torch not found" or "CUDA errors"
```bash
# Reinstall PyTorch with proper CUDA support
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu121  # CUDA 12.1

# OR for CPU only:
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Issue 2: "Ollama connection refused"
```bash
# Ensure Ollama is running
ollama serve  # Keep running in separate terminal

# Verify it's accessible
curl http://localhost:11434/api/tags

# Check if model exists
ollama list
```

### Issue 3: "Port 8000 already in use"
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9  # Linux/Mac

# OR on Windows:
netstat -ano | findstr :8000  # Find PID, then:
taskkill /PID <PID> /F
```

### Issue 4: "Permission denied" on model files
```bash
# Fix model file permissions
chmod -R 755 models/
```

### Issue 5: Virtual environment not activating
```bash
# Recreate venv from scratch
rm -rf axiomvenv
python3 -m venv axiomvenv
source axiomvenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt  # Avoid --break-system-packages; use the venv
```

### Issue 6: "SetFit model not found"
```bash
# Ensure you're in the right directory
cd axiom-voice-agent/backend
python main_agent_web.py

# Check model exists
ls -lh ../models/intent_model/setfit_intent_classifier/model.safetensors
```

### Issue 7: Import errors after installation
```bash
# Sometimes pip cache causes issues, clear it:
pip cache purge
pip install --no-cache-dir -r requirements.txt
```

---

## 🔍 Pre-launch Verification Checklist

Before reporting issues, verify:

- [ ] Virtual environment is activated (`which python` shows axiomvenv path)
- [ ] Python version ≥ 3.10 (`python --version`)
- [ ] All packages installed (`pip list | grep -E "torch|setfit|fastapi|ollama"`)
- [ ] Ollama is running (`ollama list` shows models)
- [ ] Models exist (`ls models/intent_model/setfit_intent_classifier/`)
- [ ] Port 8000 is free (`lsof -i :8000` shows nothing)
- [ ] Backend directory accessible (`cd backend && ls main_agent_web.py`)

---

## 🎯 What Gets Loaded at Runtime

When you run `python main_agent_web.py`, the system loads:

### 1. Intent Classifier (SetFit)
- **Location:** `models/intent_model/setfit_intent_classifier/`
- **Size:** 87 MB
- **Accuracy:** 94% on 9 intent classes
- **Load time:** ~2-3 seconds
- **Code:** `backend/intent_classifier.py`

### 2. Speech-to-Text (Sherpa-ONNX)
- **Location:** `models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8/`
- **Size:** 200 MB
- **Latency:** 20-30ms per chunk
- **Code:** `backend/stt_handler.py`

### 3. Text-to-Speech (Kokoro)
- **Location:** `models/kokoro-en-v0_19/`
- **Size:** 150 MB
- **Latency:** 30-40ms per sentence
- **Code:** `backend/sequential_tts_handler.py`

### 4. Voice Activity Detection (Silero VAD)
- **Location:** `models/silero_vad.onnx`
- **Size:** 40 MB
- **Purpose:** Detect when user stops speaking
- **Code:** `backend/vad_handler.py`

### 5. LLM Brain (Ollama + Fine-tuned Mistral)
- **Model:** `drobotics_test` (or `mistral`)
- **Served by:** Ollama (separate process)
- **Load time:** ~5-10 seconds
- **Code:** `backend/axiom_brain.py`

### 6. Response Correctors (🎯 UNIQUE FEATURE!)
- **Phonetic Corrector:** `backend/vocabulary_handler.py`
  - Fixes: "5m" → "5 meters", "jetson nano" → "Jetson Nano"
- **Minimal Safe Corrector:** `backend/minimal_safe_corrector.py`
  - Cleans markdown, noise tags, formatting for TTS

---

## 📊 System Resource Usage

**Expected resource consumption:**

| Component         | CPU     | RAM    | GPU VRAM      |
| :---------------- | :------ | :----- | :------------ |
| Intent Classifier | 5-10%   | 100 MB | 0 MB (CPU)    |
| STT Handler       | 15-20%  | 200 MB | 0 MB          |
| TTS Handler       | 10-15%  | 150 MB | 0 MB          |
| VAD               | 2-5%    | 40 MB  | 0 MB          |
| Ollama LLM        | 20-40%  | 4.5 GB | 4 GB (if GPU) |
| **Total**         | **30-60%** | **~5 GB** | **~4 GB**   |

**Minimum Requirements:**
- CPU: 4 cores, 2.5 GHz+
- RAM: 8 GB (16 GB recommended)
- GPU: Optional (CUDA 12.1+ recommended for faster LLM inference)
- Storage: 6 GB for models

---

## 📚 Advanced: Retraining Models

### SetFit Intent Classifier

To retrain the intent classifier with your own data:

```bash
cd setfit_training/scripts
python train_production_setfit.py
```

See [setfit_training/TEACHING_SETFIT.md](setfit_training/TEACHING_SETFIT.md) for full instructions.

### LLama Fine-tuning

For retraining the LLM with domain-specific knowledge:

See [MODEL_TRAINING_GUIDE.md](MODEL_TRAINING_GUIDE.md) for complete training pipeline.

---

## 💾 Interaction Database (Future Training Data!)

All conversations are stored in `data/web_interaction_history.db` for:
- **Future training data:** Real-world examples for retraining
- **Phonetic correction improvements:** Track which corrections work best
- **Hallucination filter refinement:** Identify edge cases
- **Performance analytics:** Intent accuracy, confidence distributions

**Schema:**
```sql
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    timestamp TEXT,
    user_query TEXT,
    intent TEXT,
    confidence REAL,
    response TEXT,
    metadata TEXT  -- Includes correction history
);
```

**Future Enhancement Path:**
1. Collect 100+ interactions → Analyze patterns
2. Collect 1000+ interactions → Retrain SetFit with real queries
3. Refine phonetic corrections based on usage
4. Deploy improved models

---

## 🤝 Need Help?

1. **Check Issues:** [GitHub Issues](https://github.com/yourusername/axiom-voice-agent/issues)
2. **Documentation:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. **Training Guide:** [MODEL_TRAINING_GUIDE.md](MODEL_TRAINING_GUIDE.md)

---

**Ready to start!** Follow the Quick Setup above and you'll be running AXIOM in minutes. 🚀
