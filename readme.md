# 💊 Health App

An AI-powered full-stack web application that lets users upload prescriptions and describe symptoms to receive structured health summaries powered by Google Gemini.

> ⚠️ This application is for informational purposes only and does not constitute medical advice. Always consult a qualified healthcare professional.

---

## 🏗️ Architecture

┌─────────────┐     HTTP      ┌─────────────────┐     SQL      ┌──────────────┐
│   React +   │ ───────────▶  │   FastAPI +      │ ──────────▶ │  PostgreSQL  │
│   Nginx     │               │   Uvicorn        │             │  (Docker)    │
│  (port 80)  │               │  (port 8000)     │             │  (port 5432) │
└─────────────┘               └─────────────────┘             └──────────────┘
│
│ Google Gemini API
▼
┌───────────────┐
│  Gemini 2.5   │
│  Flash API    │
└───────────────┘

### Services
- **Frontend:** React + Vite, served via Nginx
- **Backend:** FastAPI (Python), JWT auth, REST API
- **Database:** PostgreSQL 15
- **AI:** Google Gemini 2.5 Flash (multimodal — handles images + PDFs)
- **Containerization:** Docker + Docker Compose

### Data Model

User
└── Prescription (file_path, file_type, symptom_notes)
└── Analysis (medicines JSON, doctor_advice, lifestyle_changes)

---

## ✅ Features Completed

- [x] User signup and login with JWT authentication
- [x] Passwords hashed with bcrypt
- [x] Protected API routes via JWT middleware
- [x] Prescription upload (JPG, PNG, PDF)
- [x] Free-text symptom notes
- [x] AI analysis via Gemini 2.5 Flash
- [x] Structured output: medicines, dosage, doctor advice, lifestyle changes
- [x] Analysis cached in DB (no repeated LLM calls)
- [x] Medical disclaimer on every result
- [x] Multi-prescription support with per-card analyze
- [x] Dockerized with multi-stage builds
- [x] Deployed on AWS EC2 (t3.micro)

## ❌ Features Skipped

- [ ] Medicine reminders / notification system
- [ ] Dose tracking (taken / skipped)

---

## 🔑 Environment Variables

### Backend (`backend/.env`)
|-----------------------------------|-------------------------------------------------------------------------------------|
|              Variable             |                               Description                                           |
|-----------------------------------|-------------------------------------------------------------------------------------|
| `DATABASE_URL`                    | PostgreSQL connection string                                                        |
| `SECRET_KEY`                      | JWT signing secret (use a long random string)                                       |
| `ALGORITHM`                       | JWT algorithm (HS256)                                                               |
| `ACCESS_TOKEN_EXPIRE_MINUTES`     | Token expiry duration                                                               |
| `GEMINI_API_KEY`                  | Google Gemini API key — get from [aistudio.google.com](https://aistudio.google.com) |
| `UPLOAD_DIR`                      | Directory to store uploaded files                                                   |
|-----------------------------------|-------------------------------------------------------------------------------------|


### Frontend (`frontend/.env`)
|-----------------------------------|-------------------------------------------------------------------------------------|
|              Variable             |                               Description                                           |
|-----------------------------------|-------------------------------------------------------------------------------------|
| `VITE_API_URL`                    | Backend API base URL (e.g. `http://YOUR_EC2_IP:8000`)                               |
|-----------------------------------|-------------------------------------------------------------------------------------|


## 💻 Local Setup

### Prerequisites
- Docker Desktop
- Node.js 20+
- Python 3.11+

### Steps

```bash
# Clone the repo
git clone https://github.com/ashutoshdash29/Health-App.git
cd health-app

# Create backend env file
cp backend/.env.example backend/.env
# Fill in your GEMINI_API_KEY and SECRET_KEY

# Set frontend API URL
echo "VITE_API_URL=http://localhost:8000" > frontend/.env

# Run everything
docker compose up --build
```

App will be available at `http://localhost`
API docs at `http://localhost:8000/docs`

---

## 🚀 EC2 Deployment Runbook

### 1. Launch EC2 Instance
- AMI: Ubuntu Server 24.04 LTS
- Instance type: t2.micro (free tier)
- Security group inbound rules:
  - Port 22 (SSH) — My IP
  - Port 80 (HTTP) — Anywhere
  - Port 8000 (API) — Anywhere

### 2. Install Docker

```bash
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker ubuntu
newgrp docker
```

### 3. Clone and Configure

```bash
git clone https://github.com/YOUR_USERNAME/health-companion.git
cd health-companion

# Create backend env
nano backend/.env
# Fill in all variables

# Create frontend env
cat > frontend/.env << 'EOF'
VITE_API_URL=http://YOUR_EC2_IP:8000
EOF
```

### 4. Build and Run

```bash
docker compose up --build -d
```

### 5. Verify

```bash
docker compose ps        # all 3 services should be running
docker compose logs backend --tail=20
```

App live at: `http://YOUR_EC2_IP`

---

## 🔧 Known Issues & Trade-offs

- **File storage:** Uploads stored in a Docker volume on EC2. In production, S3 would be more appropriate for durability and scalability.
- **CORS:** Currently set to `allow_origins=["*"]`. Should be restricted to the frontend domain in production.
- **JWT:** Tokens are stored in localStorage. HttpOnly cookies would be more secure in production.
- **Free tier Gemini:** Rate limits may cause occasional 429 errors. The backend retries up to 3 times with exponential backoff.
- **Single instance:** No load balancing or auto-scaling. Suitable for demo purposes only.
