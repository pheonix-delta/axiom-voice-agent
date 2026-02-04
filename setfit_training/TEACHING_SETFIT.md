# 🎓 SetFit Training - Complete Guide

## Quick Reference

Your SetFit architecture is now **clean and well-documented**. Here's how to teach a new user:

---

## 🔧 Installation & Setup

### Prerequisites
Before training or using the SetFit model, ensure you have the required dependencies installed.

**Option 1: Install from requirements.txt** (Recommended)
```bash
# From the project root
pip install -r requirements.txt
```

The `requirements.txt` includes all necessary packages:
- `setfit>=1.0.3` - Core SetFit library
- `sentence-transformers>=2.2.2` - Embedding model backbone  
- `transformers>=4.30.0` - HuggingFace transformers
- `torch>=2.0.0` - PyTorch backend
- `scikit-learn>=1.3.2` - For dataset splitting

**Option 2: Install SetFit packages only**
```bash
pip install setfit sentence-transformers transformers torch scikit-learn
```

### Using the Pre-trained Model

**The trained model weights are already included** in the repository at:
```
models/intent_model/setfit_intent_classifier/
```

Once you install the requirements, the model will activate automatically when you run the application:

```bash
cd backend
python main_agent_web.py
```

No additional training needed unless you want to customize the intents!

---

## 📚 Files to Share (In This Order)

### 1. **Start Here:** `setfit_training/RAG_SEMANTIC_ARCHITECTURE.md`

This single file explains:
- ✅ Folder structure (clean, no duplicates)
- ✅ The 9 intent classes your model learned
- ✅ How training data was created (850+ examples)
- ✅ How the training scripts work (what actually runs)
- ✅ What the trained model looks like (file structure)
- ✅ How SetFit works at runtime (inference)
- ✅ How to retrain if needed

**Time:** 15 minutes to read and understand

---

## �️ Training Scripts (Which One to Use?)

You have 3 training scripts in `setfit_training/scripts/`:

### ✅ **Recommended: `train_production_setfit.py`**
- Uses `production_dataset.json` (850+ examples)
- Production-ready, tested configuration
- **This is what trained the current model**
- 80/20 train/test split with stratification

```bash
cd setfit_training/scripts
python train_production_setfit.py
```

### 📝 `train_final.py`
- Dataset generation script (combines multiple sources)
- Creates the training data from inventory + Kaggle
- Use this if you need to regenerate the dataset

### 🔬 `train_setfit.py`
- Experimental/backup version
- Not recommended for production use

**For retraining with your own data:**
1. Use `train_production_setfit.py` as a template
2. Modify the dataset path or add your own examples
3. Keep the same training arguments (they're optimized)

---

## �🏗️ The Clean Architecture (What User Sees)

```
axiom-voice-agent/
│
├── setfit_training/
│   ├── RAG_SEMANTIC_ARCHITECTURE.md  ← READ THIS (explains everything)
│   ├── generated/                    ← Training data (850+ examples, 244 KB)
│   └── scripts/                      ← Training scripts (how to retrain)
│
├── models/intent_model/
│   └── setfit_intent_classifier/     ← ONE ACTUAL MODEL (87 MB, deployed)
│
└── backend/
    └── intent_classifier.py          ← Loads from ../models/
```

**Key Point for User:**
- Training folder = Documentation + scripts + data (344 KB)
- Model folder = Working AI model used by app (87 MB)
- No duplicates, no confusion

---

## 🎯 Teaching Path (30 minutes)

### Part 1: Understand the Problem (5 min)

Ask user:
> "How should we handle thousands of user questions without calling the LLM for everything?"

Answer:
> "SetFit classifies questions into 9 types (greeting, equipment query, etc). We then use templates or LLM based on confidence."

### Part 2: The Architecture (10 min)

Show them this:
```
User: "Tell me about Jetson Nano"
        ↓ 
    SetFit Classifier
        ↓
    Intent: "equipment_query" (confidence: 0.94)
        ↓
    If confidence > 0.88 → Use template response (FAST)
    Otherwise → Full LLM (SLOW)
```

### Part 3: Training Flow (10 min)

Point to: `setfit_training/RAG_SEMANTIC_ARCHITECTURE.md`

Explain these sections:
1. **Training Data Pipeline** - How 850+ examples were created
2. **The Scripts** - What each script does
3. **Model Structure** - What weights were trained
4. **At Runtime** - How it predicts

### Part 4: Hands On (5 min)

Show them:
```bash
# Where the model is
ls -lh models/intent_model/setfit_intent_classifier/model.safetensors

# Test it
python -c "from backend.intent_classifier import IntentClassifier; \
           ic = IntentClassifier(); \
           print(ic.predict('Tell me about Jetson'))"
```

---

## ❓ Common Questions Users Ask

**Q: Why 9 intent classes?**
> "These cover 90%+ of lab queries. Each has 80-100 training examples."

**Q: Can I add more classes?**
> "Yes! Add training examples and retrain using setfit_training/scripts/train_production_setfit.py"

**Q: Where's the model stored?**
> "One place: models/intent_model/setfit_intent_classifier/ (87 MB)"

**Q: Can I retrain?**
> "Yes! Read setfit_training/RAG_SEMANTIC_ARCHITECTURE.md → Section 'Training Script (Aligned & Path‑Safe)'"

**Q: Why is there a setfit_training folder?**
> "To show how the model was trained. It contains scripts and data, NOT duplicate weights."

**Q: What if I mess up?**
> "The model is only in one place. Git has history. Back it up before retraining."

---

## 📖 Full Learning Path

**For someone learning for first time:**

1. **Day 1 (15 min):** Read `setfit_training/RAG_SEMANTIC_ARCHITECTURE.md` → Understand the 9 intents
2. **Day 2 (30 min):** Run the app, watch it classify inputs correctly
3. **Day 3 (1 hour):** Try retraining with your own data (follow guide in RAG_SEMANTIC_ARCHITECTURE.md)
4. **Day 4+:** Deploy your changes, iterate

---

## ✅ Structure is Perfect For Teaching

**What makes it good:**
- ✅ **Single source of truth** - Model in one place (87 MB)
- ✅ **Training documented** - RAG_SEMANTIC_ARCHITECTURE.md explains everything
- ✅ **Scripts included** - Users can learn by doing
- ✅ **Data included** - 850+ examples to learn from
- ✅ **No duplicates** - Training folder is 344 KB (lean)

**What could confuse:**
- ❌ Multiple model copies → Fixed (only one now)
- ❌ Unclear training process → Fixed (documented)
- ❌ Hidden assumptions → Fixed (architecture explained)

---

## 🚀 For a New Team Member

Give them this checklist:

- [ ] Read `setfit_training/RAG_SEMANTIC_ARCHITECTURE.md` (15 min)
- [ ] Run AXIOM and test it: `python backend/main_agent_web.py`
- [ ] Inspect the model: `ls models/intent_model/setfit_intent_classifier/`
- [ ] Test inference: `python -c "from backend.intent_classifier import IntentClassifier; ic = IntentClassifier(); print(ic.predict('test'))"`
- [ ] Try retraining (optional): Follow guide in RAG_SEMANTIC_ARCHITECTURE.md

---

## 📊 What They'll Learn

After going through this, a user will understand:

- What SetFit is (few-shot intent classifier)
- Why you use it (fast, accurate, local)
- How it was trained (850 examples across 9 classes)
- Where the model is (models/intent_model/)
- How to use it (backend/intent_classifier.py)
- How to retrain it (if needed)

---

## 💡 Pro Tips for Teaching

**DO:**
- ✅ Show them the single model location first
- ✅ Explain the 9 intents with real examples
- ✅ Point to RAG_SEMANTIC_ARCHITECTURE.md early
- ✅ Let them run `intent_classifier.py` and see predictions
- ✅ Encourage them to retrain with their own data

**DON'T:**
- ❌ Don't mention the old archived files
- ❌ Don't try to explain training data generation (too complex)
- ❌ Don't create new documentation (use existing)
- ❌ Don't modify the structure (it's clean now)

---

## 📌 Remember

The goal is **clear teaching, not perfect code**.

```
setfit_training/ = "Here's how we trained it"
models/intent_model/ = "Here's the working model"
```

That's it. That's the whole story. 📚
