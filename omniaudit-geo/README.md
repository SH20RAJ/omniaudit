# OmniAudit-GEO — Web Control Plane & MCP Server

Production-grade, sub-second web control plane and JSON-RPC 2.0 Model Context Protocol (MCP) server for the **OmniAudit-GEO** Brand AI-Readiness platform. Built 100% in pure Python using **Streamlit** and **FastAPI** (Zero Node.js, zero client-side JavaScript frameworks).

---

## 🚀 Quickstart (Local Development)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run ASGI Server
```bash
# From workspace root:
python3 -m uvicorn main:app --app-dir omniaudit-geo --reload --port 8000
```

- **Home Page:** [http://localhost:8000/](http://localhost:8000/)
- **Live Audit Console:** [http://localhost:8000/audit?url=adobe.com](http://localhost:8000/audit?url=adobe.com)
- **16 Golden Benchmarks:** [http://localhost:8000/benchmarks](http://localhost:8000/benchmarks)
- **Marketplace Manifest:** [http://localhost:8000/marketplace](http://localhost:8000/marketplace)
- **Interactive Swagger Docs:** [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **MCP Server Endpoint:** `POST http://localhost:8000/api/mcp`

### 3. Run Unit Tests
```bash
python3 -m unittest discover -s tests -v
```

---

## 🐳 Docker Deployment (DigitalOcean)

### Option A: 1-Click DigitalOcean App Platform
1. Fork or push this repository to GitHub.
2. In DigitalOcean Cloud Console, navigate to **Apps** → **Create App**.
3. Select GitHub and choose `omniaudit`.
4. DigitalOcean automatically detects the root `Dockerfile` and `.do/app.yaml`.
5. Click **Deploy**. Your app will be live with auto-scaling HTTPS in under 2 minutes.

### Option B: DigitalOcean Droplet (Docker Compose)
SSH into your DigitalOcean droplet and run:
```bash
git clone https://github.com/SH20RAJ/omniaudit.git
cd omniaudit

# Build and start container in background
docker compose up -d --build

# Verify container is healthy
docker compose ps
curl http://localhost:8000/api/health
```

### Option C: Standalone Docker Run
```bash
docker build -t omniaudit-geo .
docker run -d -p 80:8000 --name omniaudit-geo --restart unless-stopped omniaudit-geo
```

---

## 🔒 Security & Architecture Guardrails
- **Zero Client JS Build Step:** Native Streamlit enterprise UI ensures instant, interactive AI readiness analysis without complex frontend toolchains.
- **SSRF Hardened:** Protects internal metadata endpoints (`169.254.169.254`), loopbacks, and RFC 1918 private subnets.
- **Unified Logic:** Imports directly from canonical `skills/audit-orchestrator` and `skills/crawl-render-audit`.
