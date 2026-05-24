# AXIOM - Advanced Voice Agent with Conversational Intelligence

[![DOI](https://img.shields.io/badge/DOI-10.13140%2FRG.2.2.26858.17603-blue)](https://doi.org/10.13140/RG.2.2.26858.17603)
[![Read Paper](https://img.shields.io/badge/Paper-PDF-red)](research/AXIOM_Research_Paper.pdf)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128%2B-green.svg)](https://fastapi.tiangolo.com/)

<p align="center">
  <img src="assets/branding/axiom-robot.png?v=3" alt="AXIOM Mascot" width="600">
</p>

---

## Overview

**AXIOM** is a voice agent built for robotics / edge environments. It combines modern ML techniques with an efficient inference pipeline to deliver:

- **Instant Voice Interaction**: Real-time speech processing with WebSocket communication
- **Intelligent Intent Classification**: SetFit-based intent recognition using secure `.safetensors` (no pickle-based model head)
- **Context-Aware Responses**: Semantic RAG + 2,116+ template responses
- **3D Interactive UI**: WebGL-based carousel for visual equipment interaction
- **Multi-turn Conversation**: FIFO history management for contextual understanding
- **Clean TTS Output**: Phonetic + minimal safe correctors (e.g., `5m` → `5 meters`)

---

## Quick Start

### Prerequisites

- **Python**: 3.10+
- **RAM**: 8GB minimum (16GB recommended)
- **VRAM**: 2-3.6GB for GPU acceleration (optional—CPU mode works too)
- **Disk**: 1GB for models (Kokoro, Sherpa, SetFit)

### Step 1: Clone & Setup

```bash
# Clone repository
git clone https://github.com/pheonix-delta/axiom-voice-agent.git
cd axiom-voice-agent

# Create virtual environment (recommended name: axiomvenv)
python3 -m venv axiomvenv
source axiomvenv/bin/activate  # Linux/Mac
# or
axiomvenv\Scripts\activate  # Windows

# Install dependencies (avoid --break-system-packages; use the venv)
pip install -r requirements.txt
```

### Step 2: Download Models (First Run Only)

Models are **symlinked** from your system. Verify they're accessible:

```bash
# Check symlinks
ls -la models/
# Output should show:
# kokoro-en-v0_19 -> ../../kokoro-en-v0_19
# sherpa-onnx-... -> ../../sherpa-onnx-...

# If symlinks are broken, set environment variables:
export KOKORO_PATH=/path/to/kokoro-en-v0_19
export SHERPA_PATH=/path/to/sherpa-onnx-...
```

📖 **See [MODEL_PATH_RESOLUTION.md](MODEL_PATH_RESOLUTION.md)** for complete setup options:

- Environment variables (recommended)
- Creating symlinks
- Configuration files (.env)
- Troubleshooting broken paths

### Step 3: Start the Server

```bash
cd backend
python main_agent_web.py

# Output:
# INFO:     Application startup complete
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Open Browser

Navigate to:

```
http://localhost:8000
```

🎙️ **Click the microphone icon** and start speaking!

⚠️ **Important**: Use `localhost` or `127.0.0.1` (not IP addresses) for browser microphone permissions.

---

## Performance Metrics

### Charts

![Latency Benchmarks](assets/benchmarks/latency_comparison.png)

![Detailed Performance Table](assets/benchmarks/performance_table.png)

<p align="center">
  <img src="assets/benchmarks/performance_comparison.png" alt="Performance Analysis" width="800">
  <br>
  <em>Component-level latency breakdown and system throughput metrics</em>
</p>

<p align="center">
  <img src="assets/benchmarks/response_time_analysis.png" alt="Response Time Distribution" width="800">
  <br>
  <em>End-to-end response time analysis across intent categories</em>
</p>

---

## Live Demos

### 🖥️ Web Interface Screenshots

<p align="center">
  <img src="assets/screenshots/web_interface_1.png" alt="AXIOM Web Interface - Main View" width="800">
  <br>
  <em>Interactive carousel with equipment cards and voice agent</em>
</p>

<p align="center">
  <img src="assets/screenshots/web_interface_2.png" alt="AXIOM Web Interface - Equipment Details" width="800">
  <br>
  <em>Detailed equipment specifications and 3D models</em>
</p>

<p align="center">
  <img src="assets/screenshots/web_interface_3.png" alt="AXIOM Web Interface - Voice Interaction" width="800">
  <br>
  <em>Real-time voice interaction with visual feedback</em>
</p>

### Terminal Demo

- **[Terminal Demo Log](demos/TERMINAL_DEMO.md)** - Cleaned excerpts showing key interactions
- **[Asciinema Recording](demos/axiom_demo.cast)** - Full terminal session recording

---

## Real Benchmarks (Measured)

Benchmark scripts and analysis live in `benchmarks/`.

---

## Architecture

```
┌─────────────────────┐
│  Browser (Web UI)   │
│  - Voice Capture    │
│  - 3D Visualization │
└──────────┬──────────┘
           │ WebSocket
           ↓
┌──────────────────────────────────────────┐
│         FastAPI Backend Server           │
├──────────────────────────────────────────┤
│ ┌─ STT Pipeline ─────────────────────┐  │
│ │ • Sherpa-ONNX Parakeet             │  │
│ │ • Silero VAD (Voice Detection)     │  │
│ │ • Phonetic + Minimal Safe Corrector│  │
│ └────────────────────────────────────┘  │
│ ┌─ Intent Classification ────────────┐  │
│ │ • SetFit Model (Local inference)   │  │
│ │ • Intent classes                   │  │
│ └────────────────────────────────────┘  │
│ ┌─ Response Pipeline ────────────────┐  │
│ │ • Template-based bypass            │  │
│ │ • Semantic RAG handler             │  │
│ │ • Ollama LLM fallback              │  │
│ └────────────────────────────────────┘  │
│ ┌─ TTS Engine ───────────────────────┐  │
│ │ • Kokoro TTS (Sherpa-ONNX)         │  │
│ │ • Sequential queue (no echo)       │  │
│ │ • TTS-safe text normalization      │  │
│ └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
        ↓ (Data Persistence)
   SQLite Database
   (Conversation History)
```

## System Architecture

### High-Level Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Browser (frontend/)                                                          │
│  - voice-carousel-integrated.html                                            │
│  - audio-capture-processor.js                                                │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │ WebSocket (binary audio + JSON messages)
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ FastAPI Backend (backend/main_agent_web.py)                                   │
│                                                                              │
│  audio bytes                                                                  │
│     ▼                                                                        │
│  [VAD] backend/vad_handler.py                                                 │
│     ▼                                                                        │
│  [STT] backend/stt_handler.py  → transcription                                │
│     ▼                                                                        │
│  [Intent] backend/intent_classifier.py → intent + confidence                  │
│     ▼                                                                        │
│  [Context] backend/conversation_manager.py (SQLite + FIFO)                    │
│     ▼                                                                        │
│  [Response]                                                                  │
│     - Fast path: backend/template_responses.py (2,116 templates)              │
│     - Smart path: backend/semantic_rag_handler.py (RAG) + backend/axiom_brain.py (LLM)
│     ▼                                                                        │
│  [TTS] backend/sequential_tts_handler.py + text normalizers                   │
│     ▼                                                                        │
│  audio out → WebSocket → browser playback                                     │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Purpose | Tech Stack |
|---|---|---|
| **VAD Handler** | Detect speech segments | Silero VAD |
| **STT Handler** | Convert audio → text | Sherpa-ONNX |
| **Intent Classifier** | Detect user intent | SetFit (sentence-transformers) |
| **Conversation Manager** | Maintain context | SQLite + FIFO |
| **Template Responses** | Fast replies | 2,116 JSON templates |
| **RAG Handler** | Search knowledge bases | Sentence-Transformers embeddings |
| **LLM Interface** | Complex queries | Ollama + local model |
| **TTS Handler** | Generate speech | Kokoro-EN (Sherpa-ONNX) |
| **3D Mapper** | Map keywords → GLB models | Keyword extraction |
| **WebSocket Server** | Real-time communication | FastAPI + uvicorn |

### Response Quality (Unique Feature)

- **Phonetic Corrector**: TTS-friendly conversion of units and domain terms
  - Example: `5m` → `5 meters`, `jetson nano` → `Jetson Nano`
- **Minimal Safe Corrector**: Removes markdown/noise without changing meaning
  - Example: `**bold**`, `*italic*`, `` `code` `` → plain text
- **Template Bypass**: Short, verified replies when confidence is high
  - Saves GPU/LLM resources and improves latency

---

## Project Structure

```
axiom-voice-agent/
├── backend/                      # FastAPI server + core voice pipeline
│   ├── main_agent_web.py         # App entrypoint (WebSocket server)
│   ├── vad_handler.py            # Voice activity detection
│   ├── stt_handler.py            # Speech-to-text
│   ├── intent_classifier.py      # Intent routing
│   ├── semantic_rag_handler.py   # RAG + fallback path
│   ├── template_responses.py     # 2,116 template responses
│   ├── sequential_tts_handler.py # TTS queue + generation
│   └── ...
├── frontend/                     # Web UI
│   ├── voice-carousel-integrated.html
│   └── audio-capture-processor.js
├── data/                         # Knowledge bases + templates
│   ├── template_database.json
│   ├── rag_knowledge_base.json
│   ├── project_ideas_rag.json
│   ├── inventory.json
│   └── carousel_mapping.json
├── assets/                       # Images, 3D models, benchmarks
│   ├── screenshots/
│   ├── branding/
│   ├── benchmarks/
│   └── 3d v2/
├── benchmarks/                   # Benchmark scripts + reports
├── demos/                        # Demo logs + recordings
├── docs/                         # Architecture + installation docs
├── models/                       # Symlink-based model directory
├── scripts/                      # Utilities (charts, safetensors tools, etc.)
├── requirements.txt
├── start.sh
└── README.md
```

---

## Documentation

- **Quick start**: [QUICK_START.md](QUICK_START.md)
- **Installation**: [docs/INSTALLATION.md](docs/INSTALLATION.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Features**: [FEATURES.md](FEATURES.md)
- **Documentation map**: [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md)

---

## Citation

If you use AXIOM in research, please cite:

- DOI: [10.13140/RG.2.2.26858.17603](https://doi.org/10.13140/RG.2.2.26858.17603)
- Paper: [research/AXIOM_Research_Paper.pdf](research/AXIOM_Research_Paper.pdf)

---

## Community

### Trending

- **Adoption:** 5000+ clones (community-reported)
- **Visibility:** 50,000+ views on Reddit (community-reported)

If this project helps you, please **star the repo** — it helps others find an offline, low-latency voice agent.

---

## Acknowledgments

- Open-source ecosystem: FastAPI, Sherpa-ONNX, Silero VAD, SetFit, sentence-transformers, Ollama, model-viewer

