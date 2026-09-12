# 🚀 FormMind AI — Production Deployment Guide

This guide covers deploying **FormMind AI** to production with high availability, enterprise security, and zero downtime.

---

## 📑 Deployment Options

| Option | Best For | Complexity | Database |
| :--- | :--- | :--- | :--- |
| **1. Vercel Monorepo (Recommended)** | Zero-config edge hosting, global CDN, instant deployments | 🟢 Low | Cloud PostgreSQL (Neon / Supabase) or Serverless /tmp SQLite |
| **2. Vercel Frontend + Render/Railway Backend** | High traffic, long-running reports, dedicated worker pool | 🟡 Medium | Managed PostgreSQL |
| **3. Docker Compose (Self-Hosted)** | Private servers, on-premise, AWS EC2, DigitalOcean | 🟡 Medium | Bundled PostgreSQL container |

---

## ⚡ Option 1: Deploying to Vercel (Fullstack Monorepo)

FormMind AI is pre-configured for **1-click Vercel Monorepo deployment** using Vercel Serverless Python functions for FastAPI and Vercel Edge CDN for the Vite/React SPA.

### Step 1: Push Repository to GitHub / GitLab
Ensure all files including `vercel.json`, `api/index.py`, `requirements.txt`, and `frontend/` are pushed to your repository.

### Step 2: Import Project into Vercel
1. Go to [vercel.com](https://vercel.com) and click **"Add New Project"**.
2. Select your `FormMindAI-agent` repository.
3. Leave the **Root Directory** as `./` (the root).
4. Vercel will automatically detect `vercel.json` and build the frontend with `@vercel/static-build` and backend with `@vercel/python`.

### Step 3: Configure Environment Variables in Vercel
Go to **Project Settings > Environment Variables** and add:

| Key | Example Value | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Enables production security mode |
| `SECRET_KEY` | *(64-character random string)* | JWT session signing secret |
| `DATABASE_URL` | `postgresql://user:pass@ep-cool-db.us-east-2.aws.neon.tech/formmind` | Cloud PostgreSQL connection string (Neon/Supabase) |
| `CORS_ORIGINS` | `https://your-project.vercel.app` | Allowed CORS frontend origins |
| `GOOGLE_CLIENT_ID` | `...apps.googleusercontent.com` | Google Cloud OAuth Client ID |
| `GOOGLE_CLIENT_SECRET` | `GOCSPX-...` | Google Cloud OAuth Client Secret |
| `GOOGLE_REDIRECT_URI` | `https://your-project.vercel.app/auth/callback` | Authorized Google OAuth Redirect URI |
| `AI_PROVIDER` | `auto` | `auto` (zero-cost deterministic engine), `gemini`, `openai`, or `groq` |
| `GEMINI_API_KEY` | `AIzaSy...` | Optional Gemini API key |
| `NEXT_PUBLIC_GA_ID` | `G-SPWVNPXRQZ` | Google Analytics 4 Measurement ID |

### Step 4: Configure Google Cloud Console OAuth
In [Google Cloud Console](https://console.cloud.google.com/apis/credentials):
1. Add Authorized JavaScript origins: `https://your-project.vercel.app`
2. Add Authorized redirect URIs: `https://your-project.vercel.app/auth/callback`

---

## 🌐 Option 2: Vercel Frontend + Render/Railway Backend

If you prefer running your FastAPI backend on a continuous ASGI server (Render, Railway, Fly.io, AWS ECS):

1. **Deploy Backend**:
   - Host: Render / Railway / Fly.io
   - Start Command: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers 2`
   - Set environment variables as listed in `.env.production.example`.

2. **Deploy Frontend on Vercel**:
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Environment Variable: `VITE_API_BASE_URL=https://your-backend-service.onrender.com/api`

---

## 🐳 Option 3: Docker & Docker Compose (Production Self-Hosting)

For single-server production deployment using Docker:

### 1. Configure Environment
```bash
cp .env.production.example .env
# Edit .env with your production secrets and credentials
```

### 2. Launch Production Stack
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

This starts:
- **`formmind-postgres`**: Hardened PostgreSQL 15 database container with persistent data volume.
- **`formmind-backend`**: Multi-stage FastAPI container running on non-root user with health check probe.
- **`formmind-frontend`**: Nginx container serving optimized static assets with gzip compression and reverse proxying `/api` requests to backend.

### 3. Verify Health Probes
```bash
curl http://localhost/health
curl http://localhost/health/ready
```

---

## 🔒 Production Security Checklist

- [x] **Secure Random SECRET_KEY**: Generated via `openssl rand -hex 32`.
- [x] **Strict Security Headers**: CSP, HSTS, `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff`.
- [x] **Rate Limiting**: Throttling configured to protect against API abuse.
- [x] **Payload Size Safeguards**: File uploads capped at `MAX_UPLOAD_SIZE_MB` (50MB).
- [x] **RFC 7807 Error Sanitization**: Internal tracebacks hidden from clients in production.
- [x] **Serverless Temp Directory Routing**: Ephemeral uploads and report exports mapped to `/tmp` in serverless runtime.
- [x] **Database Connection Pooling**: `pool_size`, `max_overflow`, and `pool_pre_ping` configured for robust PostgreSQL pooling.
- [x] **Frontend Code Splitting**: Vendor chunks optimized for Edge CDN caching.
- [x] **React Error Boundary**: White-screen crash prevention with user recovery actions.
