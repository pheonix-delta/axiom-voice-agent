# SetFit Training Data Folder Structure

## Purpose
This folder contains all the data needed to train and validate the SetFit Intent Classifier model.

## Data Files

### Training Datasets

**production_dataset.json** (629 samples)
- **Purpose:** Production-ready training data with balanced label distribution
- **Format:** JSON array of objects with `text` and `label` fields
- **Labels:** 9 intent classes (equipment_query, capability_check, compatibility_check, guidance, project_idea, troubleshooting, lab_info, greeting, acknowledgment)
- **Distribution:**
  - equipment_query: 100 samples
  - capability_check: 68 samples
  - compatibility_check: 100 samples
  - guidance: 100 samples
  - project_idea: 100 samples
  - greeting: 100 samples
  - troubleshooting: 25 samples
  - lab_info: 31 samples
  - acknowledgment: 5 samples
- **Source:** Synthesized from LLM generations + manual curation
- **Validation:** All samples checked for proper text/label fields

**setfit_dataset.json** (79 samples)
- **Purpose:** Curated seed dataset used in initial training
- **Format:** JSON array of objects with `text` and `label` fields
- **Labels:** 6 intent classes
- **Use Case:** Cross-validation and seed training
- **Note:** Used as reference for data quality standards

### Data Generation Archives

**consolidated_parallel_results.json** (200 projects)
- **Purpose:** Archive of sanitized project data from parallel LLM generations
- **Format:** JSON with metadata and batch summaries
- **Note:** NOT used for training, kept for reference/audit
- **Sanitization:** Model names removed to prevent exposure of data generation methods

**parallel_results/** (5 batch files - archived, sanitized)
- **batch_1, batch_2, batch_3, batch_4, batch_5:** Original LLM output batches
- **Status:** Sanitized (model identifiers removed)
- **Note:** NOT used for training, kept for historical reference

### RAG Knowledge Base (DO NOT MODIFY)

The following files are **external RAG data** stored in `/data/` - these are NOT training data:
- `inventory.json` - Equipment specifications and compatibility (573 entries)
- `rag_knowledge_base.json` - Technical facts for RAG retrieval (1806 entries)
- `project_ideas_rag.json` - Project templates and ideas
- `template_database.json` - Response templates
- `carousel_mapping.json` - UI/UX data

These are used by the backend for RAG-based response generation, NOT for SetFit model training.

## Training Pipeline

### Step 1: Load Training Data
```python
# train_production_setfit.py loads:
dataset_path = root_dir / "generated" / "training_data" / "production_dataset.json"
```

### Step 2: Validate & Split
- All 629 samples validated for proper structure
- Split into 80/20 train/test (stratified by label to maintain distribution)
- Test data used for evaluation after training

### Step 3: Model Training
- Base Model: `sentence-transformers/all-MiniLM-L6-v2` (384-dim embeddings)
- Framework: SetFit with CosineSimilarityLoss
- Configuration:
  - Batch size: 16
  - Num epochs: 1
  - Evaluation strategy: per epoch
  - Best model selection: enabled
  - Random state: 42 (reproducible splits)

### Step 4: Model Output
- Trained model saved to: `models/intent_model/setfit_intent_classifier/`
- Includes:
  - Model weights (PyTorch)
  - Sentence transformer config
  - Label-to-ID mapping

## Data Quality Checks

✅ **All samples have required fields:** text, label
✅ **Label balance:** Stratified distribution across 9 intent classes
✅ **Text variety:** Domain-specific robotics/hardware queries
✅ **No duplicates:** Deduplicated during consolidation
✅ **Format consistency:** All samples follow JSON list format
✅ **Encoding:** UTF-8 with proper unicode handling

## Usage

### To Train Model
```bash
cd /path/to/axiom-voice-agent
python setfit_training/scripts/train_production_setfit.py
```

### To Update Consolidated Results
```bash
python setfit_training/scripts/consolidate_parallel_results.py
```

### To Validate Data Integrity
Run the data validation snippet (see train_production_setfit.py comments for validation checks)

## Related Files

- Training script: `setfit_training/scripts/train_production_setfit.py`
- Architecture docs: `setfit_training/RAG_SEMANTIC_ARCHITECTURE.md`
- Teaching guide: `setfit_training/TEACHING_SETFIT.md`
- Consolidation script: `setfit_training/scripts/consolidate_parallel_results.py`
