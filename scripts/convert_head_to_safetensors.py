import os
import joblib
import torch
import numpy as np
from safetensors.torch import save_file
from pathlib import Path

def convert_head():
    # Paths
    model_dir = Path("models/intent_model/setfit_intent_classifier")
    input_path = model_dir / "model_head.pkl"
    output_path = model_dir / "model_head.safetensors"
    
    if not input_path.exists():
        print(f"❌ Error: {input_path} not found.")
        return

    print(f"📂 Loading legacy head from {input_path}")
    try:
        model = joblib.load(input_path)
    except Exception as e:
        print(f"❌ Failed to load pickle: {e}")
        return

    # Extract LogisticRegression parameters
    # coef_ shape: (n_classes, n_features)
    # intercept_ shape: (n_classes,)
    
    weights = model.coef_
    intercept = model.intercept_
    classes = model.classes_
    
    print(f"📊 Extracted Model Params:")
    print(f"   - Weights shape: {weights.shape}")
    print(f"   - Intercept shape: {intercept.shape}")
    print(f"   - Classes: {classes}")

    # Convert to tensors
    tensors = {
        "weights": torch.from_numpy(weights.astype(np.float32)),
        "intercept": torch.from_numpy(intercept.astype(np.float32)),
        # Classes are usually integers or strings, safetensors prefers numeric
        "classes": torch.tensor(classes.astype(np.int64)) if classes.dtype.kind in 'iu' else torch.arange(len(classes))
    }

    print(f"💾 Saving to {output_path}")
    save_file(tensors, output_path)
    print("✅ Conversion complete!")

if __name__ == "__main__":
    convert_head()
