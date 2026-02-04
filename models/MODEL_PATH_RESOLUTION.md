# Model Path Resolution Guide

## Overview

AXIOM Voice Agent now has **intelligent model path resolution** that works from anywhere on your system. No more manual path configuration!

## How It Works

The system tries to find models in this order:

```
1. Environment Variables (KOKORO_PATH, SHERPA_PATH)
   ↓
2. Symlinks in models/ directory (default setup)
   ↓
3. Parent directory fallback (for cloned repos)
   ↓
4. Clear error with fix instructions
```

---

## Setup Methods (Choose ONE)

### Method A: Environment Variables (✅ RECOMMENDED)

**Best for**: Flexible installations, multiple AXIOM instances, non-standard locations

```bash
# Set environment variables
export KOKORO_PATH=/path/to/kokoro-en-v0_19
export SHERPA_PATH=/path/to/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8

# Start the server (from ANY directory)
cd /home/user/Desktop/voice\ agent/axiom-voice-agent/backend
python main_agent_web.py

# ✅ Works from anywhere!
```

**Persistent Setup** (Linux/Mac - add to `~/.bashrc` or `~/.zshrc`):
```bash
echo 'export KOKORO_PATH=/path/to/kokoro-en-v0_19' >> ~/.bashrc
echo 'export SHERPA_PATH=/path/to/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8' >> ~/.bashrc
source ~/.bashrc
```

**Persistent Setup** (Windows - add to environment variables):
```
Settings → System → About → Advanced system settings → Environment Variables
Add: KOKORO_PATH = C:\path\to\kokoro-en-v0_19
Add: SHERPA_PATH = C:\path\to\sherpa-onnx-...
Restart terminal/IDE
```

---

### Method B: Symlinks (Default)

**Best for**: Standard installations, development environment

```bash
# Create symlinks from models directory
cd /home/user/Desktop/voice\ agent/axiom-voice-agent/models

# If models are in parent directory
ln -s ../../kokoro-en-v0_19 kokoro-en-v0_19
ln -s ../../sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8 sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8

# Verify symlinks
ls -la
# Output should show:
# kokoro-en-v0_19 -> ../../kokoro-en-v0_19
# sherpa-onnx-... -> ../../sherpa-onnx-...

# ✅ Now start server
cd ../backend
python main_agent_web.py
```

**What if models are elsewhere?**
```bash
ln -s /custom/path/to/kokoro-en-v0_19 kokoro-en-v0_19
ln -s /custom/path/to/sherpa-onnx-... sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8
```

---

### Method C: Copy Models (Not Recommended)

**Best for**: Single-machine deployments where you want everything self-contained

```bash
# Copy actual model directories (takes more disk space)
cp -r /source/kokoro-en-v0_19 models/
cp -r /source/sherpa-onnx-... models/

# ✅ Now start server
cd backend
python main_agent_web.py
```

**Drawbacks**:
- Doubles disk usage
- Hard to update models
- Not ideal for development

---

## Quick Troubleshooting

### Check Current Setup

```bash
# List what's in models directory
ls -la models/

# Expected output:
# kokoro-en-v0_19 -> ../../kokoro-en-v0_19 (symlink)
# sherpa-onnx-... -> ../../sherpa-onnx-... (symlink)
# intent_model/ (directory)
# silero_vad.onnx (file)
```

### Test Model Loading

```bash
# From backend directory
cd backend

# Test if models can be found
python -c "from config import STT_MODEL_PATH, TTS_MODEL_PATH; print(f'STT: {STT_MODEL_PATH}'); print(f'TTS: {TTS_MODEL_PATH}')"

# Expected output:
# ✓ Found kokoro-en-v0_19 in models directory
# ✓ Found sherpa-onnx-... in parent directory
# STT: /path/to/models/sherpa-onnx-...
# TTS: /path/to/models/kokoro-en-v0_19
```

### Fix Broken Symlinks

```bash
# If symlink is broken, check where models actually are
ls ../../  # Check parent directory
ls /path/to/parent/  # Check custom path

# Recreate symlink
rm models/kokoro-en-v0_19
ln -s /correct/path/to/kokoro-en-v0_19 models/kokoro-en-v0_19

# Verify
ls -la models/kokoro-en-v0_19
```

---

## Configuration File (.env)

You can also use `.env` file for persistent configuration:

```bash
# Copy template
cp .env.example .env

# Edit .env with your paths
nano .env

# Add these lines:
KOKORO_PATH=/path/to/kokoro-en-v0_19
SHERPA_PATH=/path/to/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8
```

**Note**: The system reads .env automatically via `python-dotenv`

---

## For Contributors

If you're **cloning the repo for development**:

1. **Option A** (Recommended): Set environment variables
   ```bash
   export KOKORO_PATH=/path/to/kokoro-en-v0_19
   export SHERPA_PATH=/path/to/sherpa-onnx-...
   python backend/main_agent_web.py
   ```

2. **Option B**: Create symlinks
   ```bash
   cd models/
   ln -s /path/to/kokoro-en-v0_19 kokoro-en-v0_19
   ln -s /path/to/sherpa-onnx-... sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8
   cd ../backend
   python main_agent_web.py
   ```

3. **Option C**: Copy to .env file
   ```bash
   cp .env.example .env
   # Edit .env with your paths
   python main_agent_web.py
   ```

---

## Architecture: How Path Resolution Works

The `backend/config.py` module handles smart resolution:

```python
def _resolve_model_path(env_var_name, default_name, search_parent=True):
    """
    Try to find model in this order:
    1. Environment variable (e.g., KOKORO_PATH)
    2. Symlink in models/ directory
    3. Parent directory fallback
    4. Raise helpful error
    """
    
    # Priority 1: Check environment variable
    if env_var_name in os.environ:
        return Path(os.environ[env_var_name])
    
    # Priority 2: Check symlink
    symlink = models_dir / default_name
    if symlink.exists():
        return symlink
    
    # Priority 3: Check parent directory
    if search_parent:
        parent_path = project_root.parent / default_name
        if parent_path.exists():
            return parent_path
    
    # Priority 4: Helpful error
    raise FileNotFoundError("Model not found. Try:\n  1. Set env var\n  2. Create symlink\n  3. Copy models")
```

---

## Key Benefits

✅ **Works Anywhere**: No hardcoded paths  
✅ **Flexible**: Multiple setup methods  
✅ **Clear Errors**: Helpful messages if setup wrong  
✅ **Production-Ready**: Tested fallback chain  
✅ **No Duplication**: Symlinks avoid copying 500MB+

---

## Common Questions

### Q: Can I use relative paths in .env?
A: No. Always use absolute paths (`/home/user/models/`) or environment variables.

### Q: What if models move to a new location?
A: Just update the symlink or environment variable. No code changes needed.

### Q: Does this work on Windows?
A: Yes, but:
- Environment variables: ✅ Works great
- Symlinks: ⚠️ Requires admin/developer mode
- Recommendation: Use environment variables on Windows

### Q: Can I use multiple AXIOM instances with different models?
A: Yes! Set different environment variables for each:
```bash
# Instance 1
export KOKORO_PATH=/models/v1/kokoro-en-v0_19
python backend/main_agent_web.py

# Instance 2 (different terminal)
export KOKORO_PATH=/models/v2/kokoro-en-v0_19
python backend/main_agent_web.py
```

### Q: What's the precedence if both symlink and env var exist?
A: **Environment variables win**. Chain is:
1. `$KOKORO_PATH` (highest priority)
2. `models/kokoro-en-v0_19` symlink
3. `../kokoro-en-v0_19` parent directory
4. Error

---

## Deployment Scenarios

### Scenario 1: Single Machine (Desktop/Laptop)

```bash
# Setup once
export KOKORO_PATH=/models/kokoro-en-v0_19
export SHERPA_PATH=/models/sherpa-onnx-...

# Always works, from anywhere
python /anywhere/axiom-voice-agent/backend/main_agent_web.py
```

### Scenario 2: Server/NAS

```bash
# Models on NAS
export KOKORO_PATH=/mnt/nas/ml-models/kokoro-en-v0_19
export SHERPA_PATH=/mnt/nas/ml-models/sherpa-onnx-...

# AXIOM cloned to different location
python /home/app/axiom-voice-agent/backend/main_agent_web.py
```

### Scenario 3: Docker Container

```dockerfile
# Dockerfile
FROM python:3.10
ENV KOKORO_PATH=/models/kokoro-en-v0_19
ENV SHERPA_PATH=/models/sherpa-onnx-...

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "backend/main_agent_web.py"]
```

---

For more help, see:
- [README.md](../README.md) - Quick start
- [OSS_DEPLOYMENT_GUIDE.md](../OSS_DEPLOYMENT_GUIDE.md) - Detailed guide
- [CONTRIBUTING.md](../CONTRIBUTING.md) - For contributors
