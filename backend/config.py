"""
Configuration module for AXIOM Voice Agent
Centralizes all paths and settings for easy portability and environment-aware model loading.

Model Loading Strategy:
1. Check environment variables (KOKORO_PATH, SHERPA_PATH, etc.)
2. Check relative symlinks from models/ directory (default)
3. Check parent directory (fallback for cloned repos)
4. Raise error with helpful instructions if not found
"""
import os
from pathlib import Path

# Get the base directory (axiom-voice-agent root)
BACKEND_DIR = Path(__file__).parent
PROJECT_ROOT = BACKEND_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Data files
INVENTORY_PATH = DATA_DIR / "inventory.json"
CAROUSEL_MAPPING_PATH = DATA_DIR / "carousel_mapping.json"
TEMPLATE_DATABASE_PATH = DATA_DIR / "template_database.json"
PROJECT_IDEAS_RAG_PATH = DATA_DIR / "project_ideas_rag.json"
RAG_KNOWLEDGE_BASE_PATH = DATA_DIR / "rag_knowledge_base.json"

# Smart model path resolution with environment variable support
def _resolve_model_path(env_var_name, default_name, search_parent=True):
    """
    Resolve model path with multiple fallback strategies.
    
    Args:
        env_var_name: Environment variable name (e.g., 'KOKORO_PATH')
        default_name: Default model directory name in models/
        search_parent: Whether to search parent directory
        
    Returns:
        Path object to model directory
        
    Raises:
        FileNotFoundError: If model not found in any location
    """
    # 1. Check environment variable first (highest priority)
    if env_var_name in os.environ:
        env_path = Path(os.environ[env_var_name])
        if env_path.exists():
            print(f"✓ Using {env_var_name} from environment: {env_path}")
            return env_path
    
    # 2. Check symlink/direct path in models directory
    symlink_path = MODELS_DIR / default_name
    if symlink_path.exists():
        print(f"✓ Found {default_name} in models directory")
        return symlink_path
    
    # 3. Check parent directory (for cloned repos without symlinks)
    if search_parent:
        parent_path = PROJECT_ROOT.parent / default_name
        if parent_path.exists():
            print(f"✓ Found {default_name} in parent directory: {parent_path}")
            return parent_path
    
    # 4. Not found - raise error with helpful instructions
    raise FileNotFoundError(
        f"\n"
        f"❌ Model not found: {default_name}\n"
        f"\n"
        f"Tried these locations:\n"
        f"  1. Environment variable ${env_var_name}\n"
        f"  2. Symlink: {symlink_path}\n"
        f"  3. Parent directory: {PROJECT_ROOT.parent / default_name}\n"
        f"\n"
        f"Fix options:\n"
        f"  A) Create symlinks:\n"
        f"     cd {MODELS_DIR}\n"
        f"     ln -s /path/to/{default_name} {default_name}\n"
        f"\n"
        f"  B) Set environment variable:\n"
        f"     export {env_var_name}=/path/to/{default_name}\n"
        f"     python main_agent_web.py\n"
        f"\n"
        f"  C) Place models in parent directory:\n"
        f"     mkdir {PROJECT_ROOT.parent / default_name}\n"
        f"     cp -r /your/models/* {PROJECT_ROOT.parent / default_name}/\n"
    )

# Model paths - Smart resolution with fallbacks
STT_MODEL_PATH = _resolve_model_path('SHERPA_PATH', 'sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8')
TTS_MODEL_PATH = _resolve_model_path('KOKORO_PATH', 'kokoro-en-v0_19')
VAD_MODEL_PATH = MODELS_DIR / "silero_vad.onnx"
INTENT_CLASSIFIER_PATH = MODELS_DIR / "intent_model" / "setfit_intent_classifier"

# Asset paths
ASSETS_3D_PATH = ASSETS_DIR / "3d v2"

# Frontend paths
FRONTEND_DIR = PROJECT_ROOT / "frontend"
FRONTEND_HTML = FRONTEND_DIR / "voice-carousel-integrated.html"
FRONTEND_JS = FRONTEND_DIR / "audio-capture-processor.js"

# Database path
WEB_INTERACTION_DB_PATH = DATA_DIR / "web_interaction_history.db"

# Verify critical paths exist
def verify_paths():
    """Verify that all required paths exist"""
    critical_paths = [
        DATA_DIR,
        MODELS_DIR,
        INVENTORY_PATH,
        CAROUSEL_MAPPING_PATH,
        TEMPLATE_DATABASE_PATH,
        INTENT_CLASSIFIER_PATH,
    ]
    
    missing = []
    for path in critical_paths:
        # For symlinks, check if it exists OR if the target exists
        if not (path.exists() or (path.is_symlink() and path.resolve().exists())):
            missing.append(str(path))
    
    return missing

if __name__ == "__main__":
    # Test path configuration
    print("=== AXIOM Voice Agent Configuration ===")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Models Directory: {MODELS_DIR}")
    print("\nCritical Paths:")
    print(f"  Inventory: {INVENTORY_PATH} - {'✅' if INVENTORY_PATH.exists() else '❌'}")
    print(f"  Carousel Map: {CAROUSEL_MAPPING_PATH} - {'✅' if CAROUSEL_MAPPING_PATH.exists() else '❌'}")
    print(f"  Template DB: {TEMPLATE_DATABASE_PATH} - {'✅' if TEMPLATE_DATABASE_PATH.exists() else '❌'}")
    print(f"  Intent Classifier: {INTENT_CLASSIFIER_PATH} - {'✅' if INTENT_CLASSIFIER_PATH.exists() else '❌'}")
    print("\nModel Paths:")
    print(f"  STT Model: {STT_MODEL_PATH} - {'✅' if STT_MODEL_PATH.exists() else '❌'}")
    print(f"  TTS Model: {TTS_MODEL_PATH} - {'✅' if TTS_MODEL_PATH.exists() else '❌'}")
    print(f"  VAD Model: {VAD_MODEL_PATH} - {'✅' if VAD_MODEL_PATH.exists() else '❌'}")
    
    missing = verify_paths()
    if missing:
        print("\n⚠️  Missing paths:")
        for path in missing:
            print(f"  - {path}")
    else:
        print("\n✅ All critical paths verified!")
