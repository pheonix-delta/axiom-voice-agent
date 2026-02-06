# AXIOM Voice Agent - Reddit Post Guide

## 🎯 Project Title
**AXIOM: Production-Grade Voice AI on Consumer Hardware (GTX 1650, 4GB VRAM)**

## 📝 Post Template

### Title Options:
1. "Built a voice AI agent that runs on a $150 GPU with sub-2s latency [Research Paper + Demo]"
2. "AXIOM: Voice-controlled robotics lab assistant running entirely offline on 4GB VRAM"
3. "My first AI project: Voice agent with 3D visualization, 405ms response time on GTX 1650"

### Post Body:

```markdown
# AXIOM - Advanced Voice Agent for Robotics Labs

Hey r/MachineLearning! This is my first major AI project, and I'd love to share it with you.

## 🎯 What is it?

AXIOM is a **production-grade voice-first AI system** designed for robotics labs. It combines:
- Real-time speech processing (STT + TTS)
- Intent classification with SetFit
- RAG-powered knowledge retrieval
- Interactive 3D equipment visualization
- **All running locally with sub-2-second latency on a GTX 1650 (4GB VRAM)**

## 🚀 Key Achievements

- ⚡ **405ms** fast-path latency (template responses)
- 🤖 **1,155ms** complex-path latency (RAG + LLM)
- 💾 **3.6GB** total VRAM usage (entire pipeline)
- 🎯 **94% memory reduction** via zero-copy inference
- 📦 **Zero operational cost** (fully offline)

## 🎬 Demo

> **[Record your demo video and upload to YouTube/Imgur, then paste the link here]**

The demo shows:
1. **Idle state** - Breathing animation while waiting
2. **Keyword detection** - "robot dog" triggers carousel navigation
3. **Thinking state** - Processing with pulsing orb
4. **3D Hologram** - Interactive Unitree Go2 model
5. **Speaking state** - Reactive waveform during TTS playback

## 🏗️ Architecture

### Pipeline:
```
Microphone → VAD (Silero) → STT (Parakeet 0.6B) → Intent (SetFit) 
→ RAG (Semantic Search) → LLM (Llama 3.2 1B) → TTS (Kokoro) → Speaker
```

### Key Optimizations:
- **Zero-copy streaming** for STT/TTS (no intermediate buffers)
- **Template bypass** for 2,116 common queries (saves GPU time)
- **Semantic RAG** with 325 project ideas + 27 equipment specs
- **WebSocket architecture** for real-time state sync

## 📊 Benchmarks (GTX 1650, 4GB VRAM)

| Component | Model | VRAM | Latency |
|-----------|-------|------|---------|
| STT | Parakeet 0.6B INT8 | 600MB | 180ms |
| Intent | SetFit (MiniLM) | 400MB | 25ms |
| RAG | all-MiniLM-L6-v2 | 400MB | 50ms |
| LLM | Llama 3.2 1B Q4 | 1.2GB | 800ms |
| TTS | Kokoro EN v0.19 | 1.0GB | 100ms |
| **Total** | | **3.6GB** | **1,155ms** |

## 📚 Research Paper

I wrote a full academic paper documenting the architecture and optimizations:
- **DOI**: [10.13140/RG.2.2.26858.17603](https://doi.org/10.13140/RG.2.2.26858.17603)
- **PDF**: [Download here](research/AXIOM_Research_Paper.pdf)
- **13 pages** with benchmarks, ablation studies, and visualizations

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, WebSockets
- **STT**: Sherpa-ONNX (Parakeet TDT 0.6B)
- **TTS**: Kokoro TTS (EN v0.19)
- **Intent**: SetFit (sentence-transformers)
- **LLM**: Llama 3.2 1B (via llama-cpp-python)
- **Frontend**: Vanilla JS, Three.js, Model Viewer
- **3D**: GLB models with real-time rendering

## 🎨 Features

✅ **Voice Control**: Natural language queries about lab equipment
✅ **3D Visualization**: Interactive holograms of robotics hardware
✅ **Smart Carousel**: Auto-rotates through 10 equipment cards
✅ **Keyword Triggers**: Detects equipment names and navigates automatically
✅ **State Animations**: Idle/Thinking/Speaking with reactive visuals
✅ **Offline First**: No API calls, no cloud dependencies

## 📖 What I Learned

This is my **first major AI project**, and here's what I learned:
1. **Memory optimization is critical** - INT8 quantization saved 75% VRAM
2. **Template responses** are underrated - 90% of queries don't need LLM
3. **Zero-copy streaming** eliminates latency bottlenecks
4. **WebSocket state sync** is essential for real-time UX
5. **Semantic search** beats keyword matching for RAG

## 🚧 Challenges

- **Echo prevention**: VAD had to pause during TTS playback
- **Model loading**: Needed lazy initialization to fit in 4GB
- **3D performance**: Had to optimize GLB models for web rendering
- **STT hallucinations**: Built a vocabulary filter to catch nonsense

## 🔮 Future Work

- [ ] Add more 3D models for all equipment
- [ ] Multi-language support (currently English only)
- [ ] Voice cloning for personalized TTS
- [ ] Integration with ROS2 for real robot control
- [ ] Mobile app version

## 📦 Open Source

The full codebase is available on GitHub:
**[github.com/pheonix-delta/axiom-voice-agent](https://github.com/pheonix-delta/axiom-voice-agent)**

## 🙏 Acknowledgments

Special thanks to:
- **Sherpa-ONNX** team for the amazing STT models
- **Kokoro TTS** for high-quality voice synthesis
- **SetFit** for efficient few-shot classification
- **llama.cpp** for making LLMs accessible on consumer hardware

## 💬 Questions?

I'm happy to answer any questions about the architecture, optimizations, or implementation details!

---

**TL;DR**: Built a voice AI agent that runs on a $150 GPU with sub-2s latency. It can answer questions about robotics equipment, show 3D models, and runs entirely offline. First major AI project - feedback welcome!
```

## 🎨 Visuals to Include

1. **Main Demo Video**: (Your recorded showcase)
2. **UI Screenshot**: `assets/branding/ui_preview.png`
3. **Robot Dog Hero**: `assets/branding/robot_dog_hero.png`
4. **Architecture Diagram**: From research paper
5. **Benchmark Chart**: From research paper

## 📍 Subreddits to Post

### Primary:
- r/MachineLearning (main audience)
- r/LocalLLaMA (offline AI enthusiasts)
- r/robotics (robotics community)

### Secondary:
- r/ArtificialIntelligence
- r/learnmachinelearning
- r/SideProject
- r/coolgithubprojects

## 🎯 Posting Tips

1. **Be humble**: Mention it's your first project
2. **Show, don't tell**: Lead with the demo GIF
3. **Provide value**: Share the research paper and code
4. **Engage**: Respond to all comments within 24 hours
5. **Cross-post**: Share to multiple relevant subreddits
6. **Timing**: Post on weekdays, 9-11 AM EST for max visibility

## 📊 Expected Reception

**Positive signals**:
- ✅ Real benchmarks on consumer hardware
- ✅ Open source with documentation
- ✅ Academic paper with DOI
- ✅ Working demo (not just slides)
- ✅ Honest about being first project

**Potential criticism**:
- "Why not use Whisper?" → Parakeet is faster and smaller
- "Why not use GPT API?" → Offline-first design goal
- "1.1s is slow" → Clarify this includes RAG + LLM inference
- "Only 1B model?" → Constraint-driven design for 4GB VRAM

## 🔗 Links to Include

- GitHub: https://github.com/pheonix-delta/axiom-voice-agent
- DOI: https://doi.org/10.13140/RG.2.2.26858.17603
- Demo Video: (Upload to YouTube/Streamable)
- Paper PDF: (Host on GitHub releases)

## 📝 Follow-up Posts

After initial post, consider:
1. **Technical deep-dive**: "How I optimized voice AI to run on 4GB VRAM"
2. **Tutorial**: "Building a voice agent from scratch"
3. **Comparison**: "Parakeet vs Whisper: Speed vs Accuracy"
4. **Use case**: "Using AXIOM in a real robotics lab"

---

**Good luck with your post! 🚀**
