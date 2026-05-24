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

## ⭐ Community / Status

### 🚀 Update: Trending on r/LocalLLaMA & r/selfhosted!

- **Adoption:** 5000+ clones (community-reported)
- **Visibility:** 50,000+ views on Reddit (community-reported)

If this project helps you, please **star the repo** — it helps others find an offline, low-latency voice agent.

---

## Overview

**AXIOM** is a sophisticated voice agent built for robotics lab environments. It combines modern ML techniques with efficient inference pipelines to deliver:

- **Instant Voice Interaction**: Real-time speech processing with WebSocket communication
- **Intelligent Intent Classification**: SetFit-based intent recognition using **secure `.safetensors`** with 88%+ confidence thresholds (no pickle-based model head)
- **Context-Aware Responses**: Semantic RAG with 2,116+ template responses
- **3D Interactive UI**: WebGL-based carousel for visual equipment interaction
- **Multi-turn Conversation**: FIFO history management for contextual understanding
- **Sub-2s Latency**: Optimized for real-time conversational experience
- **Clean TTS Output**: Phonetic + minimal safe correctors (e.g., `5m` → `5 meters`)
- **Future-Ready Training**: Interaction DB logs corrections for continuous improvement

## Table of Contents

- [Community](#-community--status)
- [Live Demos](#-live-demos)
- [Overview](#overview)
- [Citation](#citation)
- [📋 Architecture](#-architecture)
- [System Architecture](#system-architecture)
  - [High-Level Flow](#high-level-flow)
  - [Component Responsibilities](#component-responsibilities)
  - [🗣️ Response Quality (Unique Feature)](#️-response-quality-unique-feature)
- [🚀 Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Step 1: Clone & Setup](#step-1-clone--setup)
  - [Step 2: Download Models (First Run Only)](#step-2-download-models-first-run-only)
  - [Step 3: Start the Server](#step-3-start-the-server)
  - [Step 4: Open Browser](#step-4-open-browser)
- [📁 Project Structure](#-project-structure)
- [📖 Documentation Roadmap](#-documentation-roadmap)
- [⭐ Breakthrough Features Deep Dive](#-breakthrough-features-deep-dive)
- [📊 Performance Comparison](#-performance-comparison)
- [🔄 Data Flow Example](#-data-flow-example)
- [🧠 Knowledge Bases (RAG)](#-knowledge-bases-rag)
- [🎨 Frontend Features](#-frontend-features)
- [📊 Performance Metrics](#-performance-metrics)
- [🔧 Configuration](#-configuration)
- [📚 API Reference](#-api-reference)
- [🛠️ Development](#️-development)
- [📈 Scalability Notes](#-scalability-notes)
- [🐛 Troubleshooting Guide](#-troubleshooting-guide)
- [🎓 Model Attribution & Licensing](#-model-attribution--licensing)
- [🤝 How to Contribute](#-how-to-contribute)
- [📞 Support Resources](#-support-resources)
- [🌟 Featured In](#-featured-in)
- [📊 Quick Stats](#-quick-stats)
- [Related Projects](#-related-projects)
- [🛡️ Security & Development Roadmap](#-security--development-roadmap)
- [🙏 Acknowledgments](#-acknowledgments)

##  Live Demos

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

### ⭐ Four Breakthrough Features

1. **🔗 Glued Interactions** - Context-aware multi-turn dialogue with 5-interaction FIFO history (stores conversation context for natural coherence)
2. **⚡ Zero-Copy Inference** - Direct tensor streaming from STT to LLM (94% memory reduction, 2.4% latency improvement)
3. **🎨 3D Holographic UI** - Interactive WebGL carousel with GPU-optimized lazy loading (streaming + progressive model loading)
4. **🗣️ Dual Corrector Pipeline** - Phonetic + minimal safe correctors for clean, natural TTS output

## 📊 Real Benchmark Proof (Measured)

![Latency Benchmarks](assets/benchmarks/latency_comparison.png)

![Detailed Performance Table](assets/benchmarks/performance_table.png)

## 🧭 Architecture & Innovation Visuals

![System Architecture](assets/benchmarks/system_architecture.png)

![Innovation Matrix](assets/benchmarks/innovation_matrix.png)

### Performance Metrics

Quantitative analysis of AXIOM's response pipeline across different query types:

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

### Terminal Demo

See AXIOM in action with real voice interactions and system logs:

- **[Terminal Demo Log](demos/TERMINAL_DEMO.md)** - Cleaned excerpts showing key interactions
- **[Asciinema Recording](demos/axiom_demo.cast)** - Full terminal session recording

## 📋 Architecture

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
│ │ • 15+ Intent classes               │  │
│ └────────────────────────────────────┘  │
│ ┌─ Response Pipeline ────────────────┐  │
│ │ • Template-based bypass (80% QPS)  │  │
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
┌─────────────────────────────────────────────────────────────────────────────────┐
│                   Browser (Web UI)                                              │
│   • Voice Capture (MediaDevices)  • 3D WebGL Carousel                            │
│   • Real-time Waveform Display    • Equipment Visualization                      │
└──────────────────────────────────┬──────────────────────────────────────────────┘
                                   │ WebSocket (Binary + JSON)
                                   ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│              FastAPI Backend (main_agent_web.py)                                 │
│                                                                                  │
│  INPUT → [STT] → [Intent] → [Response] → [TTS] → OUTPUT                          │
│                                                                                  │
│  ┌──────���────────────────────────────────────────────────────────────────────┐   │
│  │ 1. SPEECH-TO-TEXT (STT)                                                   │   │
│  │    • Model: Sherpa-ONNX Parakeet-TDT (200MB)                              │   │
│  │    • Speed: <100ms inference                                              │   │
│  │    • Tech: Transducer-based streaming recognition                         │   │
│  │    • File: backend/stt_handler.py                                         │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
│                          ↓                                                       │
│  ┌───────────────────────────────────────────────────────────────────────────┐   │
│  │ 2. INTENT CLASSIFICATION                                                  │   │
│  │    • Model: SetFit (secure `model_head.safetensors` migration)            │   │
│  │    • Speed: <50ms inference                                               │   │
│  │    • Labels: equipment_query, project_ideas, etc. (9)                      │   │
│  │    • Security: manual tensor math (no pickle-based head)                   │   │
│  │    • File: backend/intent_classifier.py                                    │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
│                          ↓                                                       │
│  ┌───────────────────────────────────────────────────────────────────────────┐   │
│  │ 3. CONTEXT INJECTION (Glued Interactions)                                  │   │
│  │    • Stores: Last 5 interactions in SQLite                                 │   │
│  │    • Injects: Previous context into LLM prompt                              │   │
│  │    • Benefit: Natural multi-turn dialogue                                   │   │
│  │    • File: backend/conversation_manager.py                                  │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
│                          ↓                                                       │
│  ┌───────────────────────────────────────────────────────────────────────────┐   │
│  │ 4. RESPONSE GENERATION                                                    │   │
│  │    ┌─ 80% TEMPLATE PATH (Fast)                                             │   │
│  │    │  • 2,116 pre-generated responses                                      │   │
│  │    │  • <10ms latency, deterministic                                       │   │
│  │    │  • Covers common equipment queries                                    │   │
│  │    └─ 20% RAG+LLM PATH (Intelligent)                                       │   │
│  │       • Semantic RAG: Searches knowledge bases                              │   │
│  │       • LLM: Ollama (fallback)                                             │   │
│  │       • Sources: 1,806 facts + 325 project ideas                            │   │
│  │       • Latency: ~100-500ms                                                 │   │
│  │       • File: backend/semantic_rag_handler.py                               │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
│                          ↓                                                       │
│  ┌───────────────────────────────────────────────────────────────────────────┐   │
│  │ 5. TEXT-TO-SPEECH (TTS)                                                   │   │
│  │    • Model: Kokoro-EN (Sherpa-ONNX based, 150MB)                            │   │
│  │    • Speed: <200ms per sentence                                            │   │
│  │    • Tech: Sequential FIFO queue (prevents echo)                            │   │
│  │    • File: backend/sequential_tts_handler.py                                │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
│                          ↓                                                       │
│  ┌───────────────────────────────────────────────────────────────────────────┐   │
│  │ 6. 3D MODEL MAPPING                                                       │   │
│  │    • Keyword Extraction: equipment names                                   │   │
│  │    • Carousel Trigger: robot_dog → unitree_go2.glb                         │   │
│  │    • Files: backend/keyword_mapper.py, backend/model_3d_mapper.py          │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Purpose | Tech Stack |
|---|---|---|
| **STT Handler** | Convert audio → text | Sherpa-ONNX + Silero VAD |
| **Intent Classifier** | Detect user intent | SetFit (sentence-transformers) |
| **RAG Handler** | Search knowledge bases | Sentence-Transformers embeddings |
| **Conversation Manager** | Maintain context | Python `deque` + SQLite |
| **Template Responses** | Fast replies | 2,116 JSON templates |
| **Ollama Interface** | Complex queries | Ollama + local model |
| **TTS Handler** | Generate speech | Kokoro-EN (Sherpa-ONNX) |
| **3D Mapper** | Equipment → GLB files | Keyword extraction |
| **WebSocket Server** | Real-time communication | FastAPI + uvicorn |

### 🗣️ Response Quality (Unique Feature)

- **Phonetic Corrector**: TTS-friendly conversion of units and domain terms
  - Example: `5m` → `5 meters`, `jetson nano` → `Jetson Nano`
- **Minimal Safe Corrector**: Removes markdown/noise without changing meaning
  - Example: `**bold**`, `*italic*`, `` `code` `` → plain text
- **Template Bypass**: Short, verified replies when confidence is high
  - Saves GPU/LLM resources and improves latency

---

## 🚀 Quick Start

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

## 📁 Project Structure

(unchanged below...)
