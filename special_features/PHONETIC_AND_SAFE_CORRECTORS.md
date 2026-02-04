# 🗣️ Phonetic + Minimal Safe Correctors

This document explains the **dual correction pipeline** that makes AXIOM’s spoken responses clean, natural, and TTS-friendly.

---

## ✅ Why This Exists

Raw STT/LLM outputs often contain:
- Abbreviations that sound wrong in speech ("5m", "10gb")
- Markdown artifacts ("**bold**", "`code`")
- Noise tags ("[Music]", "[Applause]")
- Inconsistent capitalization of technical names

AXIOM fixes this using **two lightweight, safe correction stages**.

---

## 1) Minimal Safe Corrector (Formatting Only)

**File:** `backend/minimal_safe_corrector.py`

**Principle:** Never change meaning—only fix formatting.

**What it does:**
- Removes markdown artifacts (`**bold**`, `*italic*`, `` `code` ``)
- Removes noise tags ("[Music]", "[Applause]")
- Expands unit abbreviations ("5m" → "5 meters")
- Standardizes common units ("10gb" → "10 GB")

**Example:**
```
Input:  "The **Jetson Orin** has `8gb` of memory and 5m range."
Output: "The Jetson Orin has 8 GB of memory and 5 meters range."
```

---

## 2) Phonetic Corrector (Domain Vocabulary)

**File:** `backend/vocabulary_handler.py`

**Purpose:** Ensure correct pronunciation of robotics terms and equipment.

**What it does:**
- Normalizes domain words (Jetson, LiDAR, SLAM)
- Fixes capitalization of proper nouns
- Makes speech sound professional and accurate

**Example:**
```
Input:  "tell me about jetson nano"
Output: "Tell me about Jetson Nano"
```

---

## ✅ The Combined Pipeline

```
Raw Text
   ↓ Minimal Safe Corrector (formatting + units)
Clean Text
   ↓ Phonetic Corrector (domain vocabulary)
TTS-Ready Output
```

**Benefits:**
- Natural speech output
- No content distortion
- Clear pronunciation of technical terms

---

## 📦 Stored for Continuous Improvement

All corrections are logged in:
`data/web_interaction_history.db`

This lets us:
- Improve phonetic rules using real user inputs
- Detect hallucination patterns
- Retrain the classifier with real-world queries

---

## ✅ How It’s Used in the Pipeline

1. **STT output** → minimal safe correction
2. **LLM response** → minimal safe correction
3. **Phonetic correction** → final TTS-ready output

---

## TL;DR

AXIOM uses **two safe correction layers** so the system *sounds professional*:
- **Minimal Safe Corrector**: formatting + units
- **Phonetic Corrector**: robotics vocabulary

This is one of the features that makes AXIOM feel polished in live demos.
