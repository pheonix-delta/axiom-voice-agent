# 📚 AXIOM Documentation Map

> Navigation guide to all AXIOM documentation. Find what you need quickly.

---

## Quick Links by Use Case

### 🚀 Just Want to Get Started?

**Start here**: [QUICK_START.md](QUICK_START.md) (15 minutes)
- Installation steps
- Running the application
- Sample queries to try
- Basic troubleshooting

---

### 🎓 Want to Understand the Architecture?

**Read these in order**:
1. [README.md](README.md) - Project overview & breakthrough features (10 min)
2. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design deep dive (20 min)
3. [FEATURES.md](FEATURES.md) - Detailed feature explanations (30 min)

---

### 🔍 Want to Learn a Specific Feature?

#### 🔗 Glued Interactions (Multi-Turn Dialogue)

- [QUICK_START.md - Feature 1](QUICK_START.md#-feature-1-glued-interactions-context-aware-multi-turn-dialogue) - Quick overview
- [special_features/GLUED_INTERACTIONS_DEMO.md](special_features/GLUED_INTERACTIONS_DEMO.md) - Detailed explanation
- [docs/ARCHITECTURE.md - Section 1](docs/ARCHITECTURE.md#1--glued-interactions-context-aware-multi-turn-dialogue) - Architecture details
- [FEATURES.md - Glued Interactions](FEATURES.md#-glued-interactions-context-aware-multi-turn-dialogue) - Complete reference

**To test**: `python special_features/test_glued_interactions.py`

---

#### ⚡ Zero-Copy Inference (Memory Optimization)

- [QUICK_START.md - Feature 2](QUICK_START.md#-feature-2-zero-copy-inference-memory-optimization) - Quick overview
- [special_features/ZERO_COPY_INFERENCE.md](special_features/ZERO_COPY_INFERENCE.md) - Technical deep dive
- [docs/ARCHITECTURE.md - Section 2](docs/ARCHITECTURE.md#2--zero-copy-inference-direct-tensor-streaming) - Architecture details
- [FEATURES.md - Zero-Copy Inference](FEATURES.md#-zero-copy-inference-direct-tensor-streaming) - Complete reference
- [PATH_FIX_SUMMARY.md](PATH_FIX_SUMMARY.md) - Path corrections related to this feature

**To test**: `python special_features/validate_zero_copy_inference.py`

---

#### 🎨 3D Holographic UI (Visual Engagement)

- [QUICK_START.md - Feature 3](QUICK_START.md#-feature-3-3d-holographic-ui-dynamic-model-visualization) - Quick overview
- [special_features/3D_HOLOGRAPHIC_UI.md](special_features/3D_HOLOGRAPHIC_UI.md) - 3D frontend architecture
- [docs/ARCHITECTURE.md - Section 3](docs/ARCHITECTURE.md#3--3d-holographic-ui-dynamic-model-visualization) - Architecture details
- [docs/ARCHITECTURE.md - 3D Management](docs/ARCHITECTURE.md#3d-heavy-frontend-management-streaming--lazy-loading-strategy) - Resource management
- [PATH_FIX_SUMMARY.md - 3D Management](PATH_FIX_SUMMARY.md#3d-frontend-architecture-heavy-asset-management-technique) - Path setup for 3D
- [FEATURES.md - 3D Holographic UI](FEATURES.md#-3d-holographic-ui-interactive-model-visualization) - Complete reference

**To test**: Start server → Say "Show me the robot dog" → Check DevTools Network tab

---

### 🔧 Need to Fix Something?

#### Path Issues

**Read**: [PATH_FIX_SUMMARY.md](PATH_FIX_SUMMARY.md)
- What was fixed
- Why paths were updated
- Verification steps

---

#### Backend Troubleshooting

**Read**: [QUICK_START.md - Troubleshooting](QUICK_START.md#-troubleshooting)
- Microphone not working
- Models not found
- High CPU usage
- Out of memory
- 3D models not loading
- No response audio

---

#### Frontend Issues

**Check**:
1. Browser console (DevTools → Console)
2. Network tab (DevTools → Network)
3. 3D models loading status

**Files to review**:
- `frontend/voice-carousel-integrated.html` - Main UI
- `frontend/audio-capture-processor.js` - Audio handling

---

### 📊 Want Performance Metrics?

**Performance tables in**:
- [QUICK_START.md - Performance Metrics](QUICK_START.md#-performance-metrics)
- [README.md - Performance Comparison](README.md#-performance-comparison)
- [FEATURES.md - Network Efficiency](FEATURES.md#network-efficiency-timeline)

---

### 💾 Need to Access Data?

**Data files located at**:
```
/home/user/Desktop/voice agent/axiom-voice-agent/data/
├── inventory.json                 # Equipment specs
├── template_database.json         # 2,116 Q&A pairs
├── project_ideas_rag.json        # Project ideas
├── rag_knowledge_base.json       # Technical facts
├── carousel_mapping.json         # 3D model mappings
└── web_interaction_history.db    # Conversation history (SQLite)
```

**To explore**: See [QUICK_START.md - Important Files](QUICK_START.md#-important-files-reference)

**To export conversation data**: See [FEATURES.md - Database Export](FEATURES.md#database-export)

---

### 🧪 Want to Run Tests?

**Available tests**:

1. **Glued Interactions Test**
   ```bash
   python special_features/test_glued_interactions.py
   ```
   Validates: FIFO queue, context injection, LLM integration

2. **Zero-Copy Inference Test**
   ```bash
   python special_features/validate_zero_copy_inference.py
   ```
   Validates: Memory reduction, NumPy frombuffer(), performance

3. **3D Model Loading Test**
   - Start server
   - Say "Show me the robot dog"
   - Verify in DevTools Network tab

**Test documentation**: [FEATURES.md - Testing & Validation](FEATURES.md#testing--validation)

---

### 🚢 Ready to Deploy?

**Deployment options**:
- [QUICK_START.md - Deployment](QUICK_START.md#-deployment)
- [README.md - Deployment](README.md) (search "Deployment")
- [QUICK_START.md - Scaling](QUICK_START.md#-scaling-recommendations)

---

## Documentation Files Summary

**Core docs**
- [QUICK_START.md](QUICK_START.md) — Get started immediately (30 min)
- [README.md](README.md) — Project overview (20 min)
- [FEATURES.md](FEATURES.md) — Complete feature reference (45 min)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — System design (30 min)
- [PATH_FIX_SUMMARY.md](PATH_FIX_SUMMARY.md) — Path corrections & 3D setup (10 min)

**Feature deep dives**
- [special_features/GLUED_INTERACTIONS_DEMO.md](special_features/GLUED_INTERACTIONS_DEMO.md) — Multi-turn dialogue details (20 min)
- [special_features/ZERO_COPY_INFERENCE.md](special_features/ZERO_COPY_INFERENCE.md) — Memory optimization (25 min)
- [special_features/3D_HOLOGRAPHIC_UI.md](special_features/3D_HOLOGRAPHIC_UI.md) — 3D frontend details (20 min)

**Navigation**
- [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md) — This file (10 min)

---

## Core Concepts Explained

### What is "Glued Interactions"?

Multi-turn dialogue where the AI remembers previous questions. Conversational context is maintained in a FIFO queue and injected into the LLM prompt.

**Where to learn**:
- Quick: [QUICK_START.md - Feature 1](QUICK_START.md#-feature-1-glued-interactions-context-aware-multi-turn-dialogue)
- Deep: [FEATURES.md - Glued Interactions](FEATURES.md#-glued-interactions-context-aware-multi-turn-dialogue)
- Test: `python special_features/test_glued_interactions.py`

---

### What is "Zero-Copy Inference"?

Direct streaming of speech audio to GPU tensors without intermediate memory copies. Results in 94% memory reduction and 2.4% latency improvement.

**Where to learn**:
- Quick: [QUICK_START.md - Feature 2](QUICK_START.md#-feature-2-zero-copy-inference-memory-optimization)
- Deep: [FEATURES.md - Zero-Copy Inference](FEATURES.md#-zero-copy-inference-direct-tensor-streaming)
- Test: `python special_features/validate_zero_copy_inference.py`

---

### What is "3D Holographic UI"?

Interactive WebGL 3D carousel displaying equipment models. Models load on-demand (lazy loading) and are garbage-collected when off-screen to manage GPU memory efficiently.

**Where to learn**:
- Quick: [QUICK_START.md - Feature 3](QUICK_START.md#-3d-holographic-ui-dynamic-model-visualization)
- Deep: [FEATURES.md - 3D Holographic UI](FEATURES.md#-3d-holographic-ui-interactive-model-visualization)
- Architecture: [docs/ARCHITECTURE.md - 3D Management](docs/ARCHITECTURE.md#3d-heavy-frontend-management-streaming--lazy-loading-strategy)
- Test: Say "Show me the robot dog" → Check DevTools

---

## Consistency Across Documentation

All documentation files include:

✅ **All four breakthrough features** (Glued Interactions, Zero-Copy Inference, 3D UI, Dual Corrector Pipeline)
✅ **Detailed explanations** of why each feature matters
✅ **Technical implementation** details for developers
✅ **Testing procedures** for validation
✅ **Troubleshooting guides** for common issues
✅ **Performance metrics** and comparisons
✅ **Corrected path references** to axiom-voice-agent locations
✅ **Cross-references** to related documentation

---

## Finding Specific Information

### "I need to understand how 3D models load"

→ [QUICK_START.md - 3D Management Strategy](QUICK_START.md#3d-heavy-frontend-management-strategy)

### "I need to know memory requirements"

→ [QUICK_START.md - Prerequisites](QUICK_START.md#prerequisites) or [README.md - Performance Comparison](README.md#-performance-comparison)

### "I need to debug a model loading issue"

→ [PATH_FIX_SUMMARY.md](PATH_FIX_SUMMARY.md) (verify paths) or [QUICK_START.md - 3D Models Not Loading](QUICK_START.md#3d-models-not-loading)

### "I need to know about conversation history"

→ [FEATURES.md - Glued Interactions - Database Export](FEATURES.md#database-export)

### "I need to test the system"

→ [FEATURES.md - Testing & Validation](FEATURES.md#testing--validation)

### "I need to deploy to production"

→ [QUICK_START.md - Deployment](QUICK_START.md#-deployment)

### "I need to scale to 100+ users"

→ [QUICK_START.md - Scaling Recommendations](QUICK_START.md#-scaling-recommendations)

---

## Documentation Standards

All AXIOM documentation:

1. **Feature-Complete**: Every feature mentioned everywhere it's relevant
2. **Cross-Linked**: References between related sections
3. **Consistent**: Same terminology, structure, examples
4. **Practical**: Code examples, testing steps, troubleshooting
5. **Hierarchical**: Quick overviews → Deep dives
6. **Up-to-Date**: Reflects current codebase state
7. **Path-Corrected**: Uses axiom-voice-agent locations

---

## Quick Search Reference

- **Glued Interactions** → Primary: [FEATURES.md](FEATURES.md) | Secondary: [QUICK_START.md](QUICK_START.md) | Test: `python special_features/test_glued_interactions.py`
- **Zero-Copy Inference** → Primary: [FEATURES.md](FEATURES.md) | Secondary: [QUICK_START.md](QUICK_START.md) | Test: `python special_features/validate_zero_copy_inference.py`
- **3D Holographic UI** → Primary: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Secondary: [QUICK_START.md](QUICK_START.md) | Test: Manual (voice + DevTools)
- **Path Fixes** → Primary: [PATH_FIX_SUMMARY.md](PATH_FIX_SUMMARY.md) | Secondary: [README.md](README.md) | Test: Verified manually
- **Setup** → Primary: [QUICK_START.md](QUICK_START.md) | Secondary: [README.md](README.md) | Test: Run server successfully
- **Troubleshooting** → Primary: [QUICK_START.md](QUICK_START.md) | Secondary: [FEATURES.md](FEATURES.md) | Test: Debug steps provided
- **Performance** → Primary: [README.md](README.md) | Secondary: [QUICK_START.md](QUICK_START.md) | Test: Performance tables included
- **Deployment** → Primary: [QUICK_START.md](QUICK_START.md) | Secondary: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Test: Tested locally first

---

## File Organization

```
axiom-voice-agent/
├── QUICK_START.md                    ← START HERE
├── README.md                         ← Then here
├── FEATURES.md                       ← Deep dives
├── PATH_FIX_SUMMARY.md              ← For path issues
├── DOCUMENTATION_MAP.md             ← This file
│
├── docs/
│   └── ARCHITECTURE.md              ← System design
│
├── special_features/
│   ├── GLUED_INTERACTIONS_DEMO.md   ← Feature details
│   ├── ZERO_COPY_INFERENCE.md       ← Feature details
│   └── 3D_HOLOGRAPHIC_UI.md         ← Feature details
│
├── backend/                         ← Implementation
├── frontend/                        ← Implementation
├── data/                           ← Knowledge bases
└── assets/                         ← 3D models
```

---

## Recommended Reading Paths

### Path 1: Quick Start (30 minutes)
1. QUICK_START.md - Installation & overview
2. Try voice commands
3. Check browser console for errors

### Path 2: Full Understanding (2 hours)
1. README.md - Overview
2. QUICK_START.md - Features & testing
3. docs/ARCHITECTURE.md - System design
4. FEATURES.md - Deep dives
5. special_features/ - Feature details

### Path 3: Feature Deep Dive (1-2 hours per feature)
1. QUICK_START.md - Feature section
2. FEATURES.md - Feature details
3. special_features/[FEATURE].md - Full documentation
4. Run tests: `python special_features/test_[feature].py`

### Path 4: Deployment (1 hour)
1. QUICK_START.md - Prerequisites
2. QUICK_START.md - Installation
3. QUICK_START.md - Deployment options
4. QUICK_START.md - Scaling recommendations

---

## Feedback & Updates

If documentation is unclear or missing:
1. Check related files (use table above)
2. Look for cross-references
3. Check special_features/ directory
4. Run relevant test scripts

All features have complete documentation across at least 2 primary sources plus testing procedures.

---

**Start reading**: [QUICK_START.md](QUICK_START.md) or [README.md](README.md)
