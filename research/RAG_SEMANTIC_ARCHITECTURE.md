# RAG + Semantic Search + SetFit Architecture (Web Version)

## 1) High‑level System Flow
1. **User input**
2. **Intent classification (SetFit)** → routes the query (equipment, lab info, project ideas, etc.)
3. **Template check** (short canned replies for greetings/acknowledgments)
4. **RAG retrieval**
   - **Inventory lookup** (direct JSON match)
   - **Semantic search** over JSON knowledge sources
5. **Context assembly** (RAG + conversation history)
6. **LLM response** (llama-cpp)
7. **TTS output**

## 2) Data Sources (JSON, source of truth)
- **Equipment inventory**: `data/inventory/inventory.json`
- **Project ideas**: `data/projects/project_ideas_rag.json`
- **Technical knowledge base**: `setfit_training_data/generated/rag_knowledge_base.json`

These JSON files are the *authoritative* sources. The system does **not** store knowledge in a separate vector database.

## 3) RAG Structure (How retrieval works)
### A) Direct JSON lookup (deterministic)
- For equipment queries, the system first tries **direct inventory matching** (exact or keyword match).
- This guarantees correct numeric specs because JSON is treated as the source of truth.

### B) Semantic search (in‑memory, derived embeddings)
- For equipment, project ideas, and authority facts, the system runs **semantic search**.
- **Embeddings are created at runtime** from the JSON content and kept **in memory**.
- Query → embedding → cosine similarity over all items → top‑k results (thresholded).

This is **RAG over JSON** with an **in‑memory vector index**, not a separate vector database.

## 4) all‑MiniLM Model Usage
The model `all-MiniLM-L6-v2` is used in two places:
1. **Semantic RAG** (SentenceTransformer)
   - Creates embeddings for equipment, projects, and authority facts.
   - Fast, small (~80MB), 384‑dimensional vectors.
2. **SetFit** (Intent classifier)
   - SetFit uses a sentence‑transformer backbone (also MiniLM).
   - It is fine‑tuned for intent labels and outputs class probabilities.

## 5) SetFit Working (Intent Routing)
- **Input**: user query
- **Output**: `{intent, confidence}`
- **Purpose**: route to the right pipeline *before* the LLM sees the query.
- This reduces hallucination and ensures the correct RAG source is applied.

Example routing:
- `equipment_query` → inventory lookup + semantic RAG
- `project_idea` → project semantic search
- `lab_info` / `people_query` → authority semantic search
- `greeting` / `acknowledgment` → template response

## 6) “Semantic capability without vector DB” — What it really is
You **are using embeddings**, but you **do not persist** them to a vector database.
Instead, the system:
- Loads JSON → builds embeddings in memory at startup
- Runs **brute‑force cosine similarity** over the in‑memory arrays

**Technical name**:
- **In‑memory semantic search**
- **Embedding‑based retrieval without vector database**
- **Brute‑force ANN (exact cosine search) over JSON‑derived vectors**

This is **not unique**, but it is a **simple, fast, and valid** approach for small to medium datasets.

## 7) Why this approach works
- JSON remains the **single source of truth**.
- Semantic search handles natural‑language queries without fragile keyword rules.
- SetFit prevents irrelevant RAG calls and adds control to the pipeline.
- The LLM only sees **grounded context**, lowering hallucination risk.

## 8) Key Files (Web Version)
- `web_version/semantic_rag_handler.py` → builds embeddings + semantic retrieval
- `web_version/intent_classifier.py` → SetFit inference
- `web_version/conversation_orchestrator.py` → routing + prompt assembly
- `web_version/main_agent_web.py` → full orchestration
