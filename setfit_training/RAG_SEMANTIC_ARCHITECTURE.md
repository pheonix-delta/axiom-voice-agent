# SetFit + RAG Semantic Architecture (Unified)

This document consolidates the **SetFit training architecture** and **RAG + semantic retrieval pipeline** into a single, clean reference.

---

## 1) High‑Level System Flow
1. **User input**
2. **Intent classification (SetFit)** → routes the query (equipment, lab info, project ideas, etc.)
3. **Template check** (fast replies for greetings/acknowledgments)
4. **RAG retrieval**
   - **Inventory lookup** (direct JSON match)
   - **Semantic search** over JSON knowledge sources
5. **Context assembly** (RAG + conversation history)
6. **LLM response** (Ollama)
7. **TTS output**

---

## 2) Data Sources (JSON = Source of Truth)
- **Equipment inventory**: `data/inventory.json`
- **Project ideas**: `data/project_ideas_rag.json`
- **Technical knowledge base**: `data/rag_knowledge_base.json`
- **Templates**: `data/template_database.json`

**Data folder address (local path)**:
`/home/user/Desktop/voice agent/axiom-voice-agent/data/`

These JSON files are **authoritative**. No external vector DB is used.

---

## 3) RAG Structure (How Retrieval Works)
### A) Direct JSON lookup (deterministic)
- Equipment queries attempt **exact or keyword match** first.
- Ensures correct numeric specs because JSON is the source of truth.

### B) Semantic search (in‑memory embeddings)
- Builds embeddings at runtime and keeps them in memory.
- Query → embedding → cosine similarity → top‑k results.

This is **RAG over JSON** with an **in‑memory vector index**.

### C) How all RAG sources work together (end-to-end)
1. `semantic_rag_handler.py` loads **inventory**, **project ideas**, and **knowledge base** from `data/`.
2. It builds **three embedding indexes** in memory (equipment, projects, authorities).
3. For each user query, it returns a **combined context**:
    - **Equipment matches** (inventory.json)
    - **Project matches** (project_ideas_rag.json)
    - **Technical facts** (rag_knowledge_base.json)
4. `conversation_orchestrator.py` merges this context with conversation history.
5. The LLM sees grounded context only (no external DB), then generates the final response.

---

## 4) SetFit Intent Routing
- **Input**: user query
- **Output**: `{intent, confidence}`
- **Goal**: route to the correct pipeline before LLM usage.

Example routing:
- `equipment_query` → inventory lookup + semantic RAG
- `project_idea` → project semantic search
- `lab_info` / `people_query` → authority semantic search
- `greeting` / `acknowledgment` → template response

---

## 5) Clean Folder Architecture (No Duplicates)

```
axiom-voice-agent/
├── setfit_training/
│   ├── generated/
│   │   ├── training_data/
│   │   │   ├── setfit_dataset.json            ← Curated examples
│   │   │   └── production_dataset.json        ← Full training data (850+ examples)
│   │   ├── consolidated_parallel_results.json ← Sanitized combined LLM variations
│   │   └── parallel_results/                  ← Raw batch outputs (sanitized in place)
│   └── scripts/
│       ├── train_production_setfit.py         ← Train the model
│       └── consolidate_parallel_results.py    ← Merge/sanitize batch outputs
│
├── models/intent_model/
│   └── setfit_intent_classifier/             ← Actual deployed model
│
└── backend/
    └── intent_classifier.py                  ← Loads the model
```

**Key Point:** Only one deployed model exists in `models/intent_model/setfit_intent_classifier/`.

---

## 6) Training Data Pipeline (Sanitized)
1. **Curated base examples** → `generated/training_data/setfit_dataset.json`
2. **Expanded production dataset** → `generated/training_data/production_dataset.json`
3. **Batch variations** → `generated/parallel_results/*.json`
4. **Consolidated + sanitized** → `generated/consolidated_parallel_results.json`

> Model/source identifiers are removed from batch outputs to avoid exposing data‑generation sources.

---

## 7) Training Script (Aligned & Path‑Safe)
**File:** `setfit_training/scripts/train_production_setfit.py`
- Loads: `setfit_training/generated/training_data/production_dataset.json`
- Saves: `models/intent_model/setfit_intent_classifier/`

Run:
```bash
python setfit_training/scripts/train_production_setfit.py
```

---

## 8) Consolidation Script (Sanitization Required)
**File:** `setfit_training/scripts/consolidate_parallel_results.py`
```bash
python setfit_training/scripts/consolidate_parallel_results.py
```

This script:
- Removes model/source identifiers from batch files
- Outputs `generated/consolidated_parallel_results.json`

---

## 9) Why This Architecture Works
- JSON remains the single source of truth.
- Semantic search enables natural queries without fragile keyword rules.
- SetFit prevents irrelevant RAG calls and reduces hallucinations.
- LLM only sees grounded context.
