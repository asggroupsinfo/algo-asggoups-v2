# DEPLOYMENT & HOSTING SPECIFICATION - algo.asgroups

**Date:** 2026-01-13  
**Project:** algo.asgroups Web Dashboard  
**Status:** Planning Complete  

---

## 📋 DEPLOYMENT OVERVIEW

### Hosting Platform
**Provider:** Hostinger Cloud Hosting (User-provided)  
**Domain:** algo.asgroups (Already registered by user)

### Deployment Strategy
- **Type:** Cloud hosting with Docker containerization
- **CI/CD:** Manual deployment initially, automated later
- **Monitoring:** Built-in Hostinger monitoring + custom health checks
- **Backup:** Daily automated backups via Hostinger

---

## 🖥️ HOSTINGER CLOUD HOSTING SPECIFICATIONS

### Recommended Plan
**Cloud Hosting Plan:** Business Cloud or Cloud Professional

**Minimum Requirements**
- **RAM:** 4GB (for backend + frontend + database)
- **CPU:** 2 vCPUs
- **Storage:** 100GB SSD (for application + logs + database)
- **Bandwidth:** 100GB/month (sufficient for trading dashboard)

**Features Needed:**
- ✅ SSH Access (for deployment)
- ✅ Root Access (for Docker installation)
- ✅ Multiple Domains (algo.asgroups)
- ✅ Free SSL (Let's Encrypt via Hostinger)
- ✅ Database Support (PostgreSQL)
- ✅ Daily Backups

---

## 🚀 DEPLOYMENT ARCHITECTURE

### Server Stack
```
┌─────────────────────────────────────────┐
│         algo.asgroups (Domain)          │
│              HTTPS (443)                │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Nginx Reverse Proxy              │
│    (SSL Termination, Load Balancing)    │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼─────┐  ┌──────▼────────┐
│  Backend   │  │   Frontend    │
│  (FastAPI) │  │   (Next.js)   │
│  Port 8000 │  │   Port 3000   │
└──────┬─────┘  └───────────────┘
       │
┌──────▼──────────────────────────────────┐
│    PostgreSQL 15 (Existing ZepixBot DB) │
│         Port 5432 (Internal)            │
└─────────────────────────────────────────┘
```

---

## 📦 DOCKER CONTAINERIZATION

### Docker Compose Setup
```yaml
version: '3.8'

services:
  backend:
    build: ./algo-asgroups-backend
    container_name: algo_backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/zepix_bot
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    volumes:
      - ./backend-logs:/app/logs
    networks:
      - algo-network

  frontend:
    build: ./algo-asgroups-frontend
    container_name: algo_frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=https://algo.asgroups/api
      - NODE_ENV=production
    depends_on:
      - backend
    networks:
      - algo-network

  nginx:
    image: nginx:alpine
    container_name: algo_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/letsencrypt:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - backend
      - frontend
    networks:
      - algo-network

networks:
  algo-network:
    driver: bridge
```

---

## 🔧 NGINX CONFIGURATION

### Nginx Reverse Proxy Config
```nginx
server {
    listen 80;
    server_name algo.asgroups www.algo.asgroups;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name algo.asgroups www.algo.asgroups;
    
    # SSL Configuration (Hostinger Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/algo.asgroups/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/algo.asgroups/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Frontend (Next.js)
    location / {
        proxy_pass http://frontend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Backend API
    location /api {
        proxy_pass http://backend:8000/api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket (Real-time)
    location /ws {
        proxy_pass http://backend:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

---

## 🔐 SSL CERTIFICATE SETUP

### Using Hostinger's Free SSL
1. **Access Hostinger Panel**
   - Log in to Hostinger control panel
   - Navigate to: SSL → Install SSL
   - Select "Free SSL" (Let's Encrypt)
   - Choose domain: algo.asgroups
   - Click "Install"

2. **Certificate Paths**
   - Certificate: `/etc/letsencrypt/live/algo.asgroups/fullchain.pem`
   - Private Key: `/etc/letsencrypt/live/algo.asgroups/privkey.pem`
   - Chain: `/etc/letsencrypt/live/algo.asgroups/chain.pem`

3. **Auto-Renewal**
   - Hostinger handles automatic renewal (every 90 days)
   - Manual renewal command (if needed):
     ```bash
     certbot renew --dry-run
     ```

---

## 📁 DEPLOYMENT DIRECTORY STRUCTURE

```
/var/www/algo.asgroups/
├── docker-compose.yml
├── .env
├── algo-asgroups-backend/
│   ├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── ...
├── algo-asgroups-frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── package.json
│   └── ...
├── nginx/
│   ├── nginx.conf
│   └── logs/
├── ssl/
│   └── (SSL certificates from Hostinger)
└── logs/
    ├── backend/
    └── frontend/
```

---

## 🚀 DEPLOYMENT PROCESS

### Step 1: Prepare Hostinger Server
```bash
# SSH into Hostinger server
ssh user@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Create deployment directory
sudo mkdir -p /var/www/algo.asgroups
cd /var/www/algo.asgroups
```

### Step 2: Upload Project Files
```bash
# Option A: Using Git (Recommended)
git clone https://github.com/yourusername/algo-asgroups.git .

# Option B: Using SCP from local machine
scp -r ./algo-asgroups user@your-server-ip:/var/www/
```

### Step 3: Configure Environment
```bash
# Create .env file
nano .env

# Add environment variables:
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/zepix_bot
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
```

### Step 4: Build and Start Services
```bash
# Build Docker images
docker-compose build

# Start services
docker-compose up -d

# Check running containers
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 5: Configure Domain in Hostinger
1. Go to Hostinger control panel
2. Navigate to: Domains → Manage → algo.asgroups
3. Point A record to server IP
4. Set up SSL certificate (Let's Encrypt)

### Step 6: Verify Deployment
```bash
# Test health endpoint
curl https://algo.asgroups/health

# Test frontend
curl https://algo.asgroups/

# Test WebSocket (manual browser test)
# Open browser console and connect to wss://algo.asgroups/ws/live
```

---

## 📊 MONITORING & HEALTH CHECKS

### Application Health Checks
```bash
# Backend health check
curl https://algo.asgroups/api/health

# Expected response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "websocket": "active"
# }
```

### Container Monitoring
```bash
# View container status
docker-compose ps

# View container logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx

# View resource usage
docker stats
```

### Hostinger Monitoring
- Access via Hostinger control panel
- Metrics available:
  - CPU usage
  - RAM usage
  - Disk space
  - Bandwidth usage
  - Uptime monitoring

---

## 🔄 UPDATE & MAINTENANCE

### Deploying Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart containers
docker-compose down
docker-compose build
docker-compose up -d

# Or use zero-downtime update:
docker-compose up -d --build
```

### Database Backups
```bash
# Manual backup
docker exec algo_backend pg_dump -U user zepix_bot > backup_$(date +%Y%m%d).sql

# Restore from backup
docker exec -i algo_backend psql -U user zepix_bot < backup_20260113.sql
```

### Log Rotation
```bash
# Configure logrotate
/var/www/algo.asgroups/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    missingok
}
```

---

## 🛡️ SECURITY MEASURES

### Firewall Configuration
```bash
# Allow SSH, HTTP, HTTPS only
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Docker Security
- Run containers as non-root user
- Limit container resources (CPU, memory)
- Use secrets for sensitive data (not in .env)
- Regular security updates

### Application Security
- HTTPS only (enforced by Nginx)
- Strong secret keys (JWT)
- CORS configured properly
- Rate limiting enabled
- SQL injection prevention (SQLAlchemy ORM)

---

## 📈 SCALABILITY CONSIDERATIONS

### Current Setup (Single Server)
- Suitable for: <1000 concurrent users
- Expected load: Low to medium
- Cost: $10-30/month (Hostinger)

### Future Scaling (If Needed)
- **Horizontal Scaling:** Multiple backend instances with load balancer
- **Database Scaling:** Read replicas, connection pooling
- **Caching:** Redis for session storage and API caching
- **CDN:** CloudFlare for static assets

---

## 💰 ESTIMATED COSTS

### Monthly Costs
- **Hostinger Cloud Hosting:** $15-25/month
- **Domain:** $10-15/year ($1.25/month)
- **SSL Certificate:** FREE (Let's Encrypt via Hostinger)
- **Total:** ~ $16-27/month

### One-time Costs
- Domain already registered (User owns it)
- Development time (user or AI-assisted)

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] Hostinger server provisioned
- [ ] Docker and Docker Compose installed
- [ ] Project files uploaded to server
- [ ] Environment variables configured (.env)
- [ ] SSL certificate installed via Hostinger
- [ ] Domain A record points to server IP
- [ ] Docker containers built and running
- [ ] Nginx reverse proxy configured
- [ ] Health check endpoint responding
- [ ] Frontend accessible at https://algo.asgroups
- [ ] Backend API accessible at https://algo.asgroups/api/docs
- [ ] WebSocket working at wss://algo.asgroups/ws/live
- [ ] Firewall configured
- [ ] Monitoring setup
- [ ] Backup strategy implemented
- [ ] SSL auto-renewal configured

---

**Deployment Documentation Status:** ✅ **COMPLETE**  
**Hosting:** Hostinger Cloud Hosting  
**Domain:** algo.asgroups (User-registered)  
**Estimated Setup Time:** 2-4 hours


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

