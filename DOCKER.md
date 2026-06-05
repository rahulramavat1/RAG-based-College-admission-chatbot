# Docker Deployment Guide

## 📦 Overview

This guide covers running the College Admission Chatbot using Docker and Docker Compose.

The setup includes:
- **Backend**: FastAPI server running on port 8000
- **Frontend**: React (Vite) UI running on port 5173
- **Networking**: Both services communicate via a Docker network

---

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/install/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)
- Your `.env` file with `GROQ_API_KEY` (optional for demo mode)

### Setup

1. **Clone & Navigate**
   ```bash
   git clone https://github.com/rahulramavat1/RAG-based-College-admission-chatbot.git
   cd college-admission-chatbot
   ```

2. **Create Environment File**
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY (optional)
   ```

3. **Initialize FAISS Index (First Time Only)**
   ```bash
   # This step must be done BEFORE starting Docker services
   python backend/ingest.py
   ```
   This creates the `faiss_index` directory with the vector store.

4. **Build & Start Services**
   ```bash
   docker-compose up --build
   ```

   This will:
   - Build both backend and frontend images
   - Start the backend on http://localhost:8000
   - Start the frontend on http://localhost:5173
   - Connect them via a shared Docker network

5. **Access the Application**
   - **Frontend**: http://localhost:5173
   - **API Docs**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

---

## 📋 File Structure

```
college-admission-chatbot/
├── Dockerfile.backend          # Backend Python/FastAPI image
├── Dockerfile.frontend         # Frontend Node.js/React image
├── docker-compose.yml          # Orchestration config
├── .dockerignore               # Docker build exclusions
├── frontend/
│   ├── .dockerignore          # Frontend-specific build exclusions
│   └── ...
├── backend/
│   ├── api.py
│   ├── rag_pipeline.py
│   ├── ingest.py
│   └── ...
├── faiss_index/               # Vector store (created by ingest.py)
└── ...
```

---

## 🐳 Docker Commands

### Start Services (Foreground)
```bash
docker-compose up
```

### Start Services (Background)
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend

# Real-time logs
docker-compose logs -f backend
```

### Rebuild Images
```bash
docker-compose up --build
```

### Remove Containers & Images
```bash
docker-compose down -v --rmi all
```

---

## 🔧 Environment Variables

Create a `.env` file in the project root:

```env
# Required for LLM responses (Groq API)
GROQ_API_KEY=gsk_your-groq-api-key-here

# Optional (defaults to ./faiss_index)
FAISS_INDEX_PATH=./faiss_index
```

---

## 🛠️ Advanced Usage

### Running Single Service

**Backend only:**
```bash
docker-compose up backend
```

**Frontend only:**
```bash
docker-compose up frontend
```

### Accessing Container Shell

**Backend container:**
```bash
docker exec -it college-admission-backend bash
```

**Frontend container:**
```bash
docker exec -it college-admission-frontend sh
```

### Building Images Separately

**Backend:**
```bash
docker build -t college-admission-backend:latest -f Dockerfile.backend .
```

**Frontend:**
```bash
docker build -t college-admission-frontend:latest -f Dockerfile.frontend .
```

### Running Containers Manually

**Backend:**
```bash
docker run -p 8000:8000 \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  -v $(pwd)/faiss_index:/app/faiss_index \
  college-admission-backend:latest
```

**Frontend:**
```bash
docker run -p 5173:5173 \
  -e VITE_API_URL=http://localhost:8000 \
  college-admission-frontend:latest
```

---

## 🔍 Health Checks

Both services include health checks:

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend health
curl http://localhost:5173
```

View container health status:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

---

## 🐛 Troubleshooting

### "FAISS index not found"
**Solution**: Run `python backend/ingest.py` BEFORE starting Docker
```bash
python backend/ingest.py
docker-compose up --build
```

### "GROQ_API_KEY not set"
**Solution**: The app works in demo mode without this. If you want LLM responses:
```bash
export GROQ_API_KEY=gsk_your-key-here
docker-compose up
```

### Port Already in Use
**Solution**: Change ports in `docker-compose.yml` or stop other services:
```bash
docker-compose down
# or change ports:
# ports:
#   - "8001:8000"  (for backend)
#   - "5174:5173"  (for frontend)
```

### Frontend Can't Connect to Backend
**Solution**: Make sure the `VITE_API_URL` environment variable is set correctly in `docker-compose.yml`:
```yaml
environment:
  - VITE_API_URL=http://backend:8000  # Inside Docker network
```

For local development:
```yaml
environment:
  - VITE_API_URL=http://localhost:8000  # From host machine
```

### Container Exits Immediately
**Check logs:**
```bash
docker-compose logs backend
docker-compose logs frontend
```

---

## 📊 Volume Mounts

The `docker-compose.yml` mounts:

1. **FAISS Index Volume**
   ```yaml
   - ./faiss_index:/app/faiss_index
   ```
   Persists the vector store across container restarts.

2. **Data Volume** (Optional)
   ```yaml
   - ./data:/app/data
   ```
   For access to sample documents inside the container.

---

## 🚀 Production Deployment

For production, consider:

1. **Use environment-specific compose files:**
   ```bash
   docker-compose -f docker-compose.prod.yml up
   ```

2. **Add a reverse proxy (nginx)** for SSL/TLS
3. **Use secrets management** (Docker Secrets or external vault)
4. **Set resource limits:**
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '1'
             memory: 2G
   ```

5. **Use external database** for production vector storage instead of local FAISS

---

## 📝 Notes

- **Frontend API URL**: Ensure frontend correctly points to backend. Use `http://backend:8000` inside Docker network, or `http://localhost:8000` when running from host.
- **Persistence**: The `faiss_index` directory must exist before starting services.
- **Demo Mode**: The chatbot works without `GROQ_API_KEY` using fallback keyword matching.

---

## 📚 Related Documentation

- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Guide](https://vitejs.dev/guide/)

