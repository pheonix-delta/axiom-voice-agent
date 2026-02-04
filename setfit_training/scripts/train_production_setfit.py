"""
Train SetFit Intent Classifier - Production Version
Uses production_dataset.json (850+ examples)
"""
import json
from pathlib import Path
from setfit import SetFitModel, Trainer, TrainingArguments
from datasets import Dataset
from sentence_transformers.losses import CosineSimilarityLoss

# Load dataset
root_dir = Path(__file__).resolve().parents[1]
dataset_path = root_dir / "generated" / "training_data" / "production_dataset.json"
with open(dataset_path, 'r') as f:
    data = json.load(f)

print(f"Loaded {len(data)} examples")

# Split train/test (80/20)
from sklearn.model_selection import train_test_split
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42, stratify=[d['label'] for d in data])

# Create datasets
train_dataset = Dataset.from_list(train_data)
test_dataset = Dataset.from_list(test_data)

print(f"Training on {len(train_dataset)} examples...")
print(f"Testing on {len(test_dataset)} examples...")

# Load base model
model = SetFitModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Training args
args = TrainingArguments(
    batch_size=16,
    num_epochs=1,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)

# Trainer
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    metric="accuracy",
    column_mapping={"text": "text", "label": "label"}
)

# Train
print("\n🚀 Training SetFit...")
trainer.train()

# Evaluate
metrics = trainer.evaluate()
print(f"\n✅ Accuracy: {metrics['accuracy']*100:.2f}%")

# Save
model_output = root_dir.parents[0] / "models" / "intent_model" / "setfit_intent_classifier"
model.save_pretrained(model_output)
print(f"\n💾 Model saved to {model_output}")
