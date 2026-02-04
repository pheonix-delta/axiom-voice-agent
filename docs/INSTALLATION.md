# AXIOM Installation & Setup Guide

## 📋 Prerequisites

- **OS**: Linux, macOS, or Windows
- **Python**: 3.8 - 3.11 (3.10 recommended)
- **RAM**: 4GB minimum (8GB+ recommended)
- **GPU** (Optional): 4GB+ VRAM for accelerated inference
- **Disk**: 3GB for models + dependencies

## 🚀 Step-by-Step Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/axiom.git
cd axiom
```

### 2. Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\\venv\\Scripts\\Activate.ps1
```

### 3. Upgrade pip
```bash
pip install --upgrade pip setuptools wheel
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

**Expected output**: ~1-2 minutes, ~500MB download

### 5. Verify Installation
```bash
# Check Python packages
pip list

# Test imports
python -c "import fastapi, sherpa_onnx, setfit; print('✓ All imports successful')"
```

## 🎯 Quick Start

### Option 1: Simple Server (Recommended for Testing)
```bash
cd backend
python main_agent_web.py
```

**Expected output:**
```
80 INFO: Started server process
127.0.0.1:54321 - "GET / HTTP/1.1" 200
✅ All modules initialized (llama-cpp-python loaded)
```

### Option 2: With Auto-Reload (Development)
```bash
cd backend
uvicorn main_agent_web:app --reload --host 127.0.0.1 --port 8000
```

### 3. Open Browser
```
http://localhost:8000
```

✅ You should see the 3D carousel interface

## 🎤 Testing the System

### 1. Microphone Permission
- Browser will prompt for microphone access
- Grant permission to proceed

### 2. Voice Test
1. Click the **Microphone** button
2. Say: "Tell me about the robot dog"
3. Wait for response (2-3 seconds)
4. Listen to TTS audio output

### 3. Sample Queries
```
"What equipment is in the lab?"
"Show me project ideas"
"How does the Unitree Go2 work?"
"List all sensors"
"Tell me about robotics"
```

## 📊 Troubleshooting

### Issue: Models Not Found
```bash
# Check model directory structure
ls -la models/
# Should show: intent_model/, kokoro-en-v0_19/, sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8/, silero_vad.onnx
```

**Solution**: Ensure all models are copied to the `models/` directory.

### Issue: "No audio input"
```bash
# Test microphone availability
python -c "
import sounddevice
print('Available devices:')
print(sounddevice.query_devices())
"
```

**Solution**: 
- Use Chrome/Edge (best microphone support)
- Ensure `localhost` or `127.0.0.1` in browser URL

### Issue: High CPU Usage
```bash
# Reduce worker threads
export STT_NUM_THREADS=2
python main_agent_web.py
```

### Issue: Out of Memory
```bash
# Reduce model precision (if GPU available)
# Edit backend/stt_handler.py, line ~45:
# providers=['CUDAExecutionProvider'] → ['CPUExecutionProvider']
```

## 🐳 Docker Deployment (Optional)

Create `Dockerfile` in root:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "backend/main_agent_web.py"]
```

Build and run:
```bash
docker build -t axiom .
docker run -p 8000:8000 -v $(pwd)/data:/app/data axiom
```

## ☁️ Cloud Deployment

### AWS EC2
```bash
# Instance: t3.medium (2GB RAM) or higher
# OS: Ubuntu 22.04 LTS

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10
sudo apt install python3.10 python3.10-venv -y

# Clone and setup
git clone https://github.com/yourusername/axiom.git
cd axiom
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with gunicorn for production
pip install gunicorn
gunicorn -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 backend.main_agent_web:app
```

### Heroku
```bash
# Create Procfile
echo "web: gunicorn -w 1 -k uvicorn.workers.UvicornWorker backend.main_agent_web:app" > Procfile

# Add runtime
echo "python-3.10.12" > runtime.txt

# Deploy
git push heroku main
```

## 🔐 Security Checklist

- [ ] Set CORS origins in production
- [ ] Enable HTTPS only
- [ ] Validate user input in STT handler
- [ ] Rate limit WebSocket connections
- [ ] Store sensitive configs in environment variables
- [ ] Regular security audits

## 📈 Performance Tuning

### For Production
```python
# backend/main_agent_web.py, line ~90
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict origins
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["content-type"],
)
```

### GPU Acceleration
```bash
# Install GPU support (NVIDIA)
pip install onnxruntime-gpu

# Or CPU-optimized
pip install onnxruntime-extensions
```

## 🧪 Running Tests (if included)
```bash
pytest tests/ -v
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Sherpa-ONNX Docs](https://k2-fsa.github.io/sherpa/onnx/)
- [SetFit Documentation](https://github.com/huggingface/setfit)
- [WebSocket Guide](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

## 🎓 Learning Path

1. **Understand Architecture**: Read `README.md`
2. **Explore Handlers**: Check `backend/` files
3. **Study Frontend**: Examine `frontend/voice-carousel-integrated.html`
4. **Extend System**: Add new intents/knowledge bases
5. **Deploy**: Follow cloud deployment guide

## 💡 Tips

- Models are cached after first load (faster subsequent startups)
- Enable Python unbuffered output: `PYTHONUNBUFFERED=1`
- Use `--log-level debug` for detailed server logs
- Monitor database size: `du -sh data/`

---

**Ready to deploy AXIOM?** Follow the Quick Start section above! 🚀
