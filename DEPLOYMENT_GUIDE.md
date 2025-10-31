# 🚀 MLBattle Deployment Guide

This guide will help you deploy MLBattle to production.

---

## 📋 Prerequisites

- Ubuntu 20.04+ server (or similar Linux distribution)
- MongoDB 6.0+
- Redis 7.x
- Node.js 18+ and npm
- Python 3.10+
- Nginx
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)

---

## 🔧 Server Setup

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Required Packages
```bash
# Python and dependencies
sudo apt install python3.10 python3.10-venv python3-pip -y

# MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install -y mongodb-org

# Redis
sudo apt install redis-server -y

# Nginx
sudo apt install nginx -y

# Node.js (using NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Additional tools
sudo apt install git supervisor -y
```

### 3. Configure MongoDB
```bash
# Start MongoDB
sudo systemctl enable mongod
sudo systemctl start mongod

# Connect to MongoDB shell
mongosh

# Create database and user (optional for production security)
use mlbattle
db.createUser({
  user: "mlbattle_user",
  pwd: "your_secure_password",
  roles: [{role: "readWrite", db: "mlbattle"}]
})
exit
```

> **Note:** MongoDB automatically creates the database on first write. User creation is optional but recommended for production security.

### 4. Configure Redis
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Test Redis
redis-cli ping
# Should return: PONG
```

---

## 📦 Deploy Backend

### 1. Clone Repository
```bash
cd /var/www
sudo git clone <your-repo-url> mlbattle
sudo chown -R $USER:$USER mlbattle
cd mlbattle
```

### 2. Setup Python Environment
```bash
cd backend
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 3. Configure Environment Variables
```bash
cp .env.example .env
nano .env
```

Update with production values:
```env
# Django Settings
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database - MongoDB
DB_NAME=mlbattle
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_USER=mlbattle_user
MONGO_PASSWORD=your_secure_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Kaggle API
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key

# Channels
CHANNEL_LAYER_HOST=localhost
CHANNEL_LAYER_PORT=6379
```

### 4. Run Migrations
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 5. Test Backend
```bash
# Test Django
python manage.py runserver 0.0.0.0:8000

# In another terminal, test if it works
curl http://localhost:8000/api/competitions/
```

---

## 🎨 Deploy Frontend

### 1. Build Frontend
```bash
cd /var/www/mlbattle/frontend

# Configure environment
cp .env.example .env
nano .env
```

Update `.env`:
```env
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_WS_URL=wss://api.yourdomain.com
```

### 2. Install and Build
```bash
npm install
npm run build
```

Build files will be in `build/` directory.

---

## 🔄 Configure Systemd Services

### 1. Gunicorn Service (Django)
```bash
sudo nano /etc/systemd/system/mlbattle.service
```

```ini
[Unit]
Description=MLBattle Gunicorn Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/mlbattle/backend
Environment="PATH=/var/www/mlbattle/backend/venv/bin"
ExecStart=/var/www/mlbattle/backend/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/mlbattle/backend/mlbattle.sock \
    --timeout 120 \
    --access-logfile /var/log/mlbattle/access.log \
    --error-logfile /var/log/mlbattle/error.log \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 2. Daphne Service (WebSocket)
```bash
sudo nano /etc/systemd/system/mlbattle-daphne.service
```

```ini
[Unit]
Description=MLBattle Daphne Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/mlbattle/backend
Environment="PATH=/var/www/mlbattle/backend/venv/bin"
ExecStart=/var/www/mlbattle/backend/venv/bin/daphne \
    -b 0.0.0.0 -p 8001 \
    config.asgi:application

[Install]
WantedBy=multi-user.target
```

### 3. Celery Worker Service
```bash
sudo nano /etc/systemd/system/mlbattle-celery.service
```

```ini
[Unit]
Description=MLBattle Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/mlbattle/backend
Environment="PATH=/var/www/mlbattle/backend/venv/bin"
ExecStart=/var/www/mlbattle/backend/venv/bin/celery \
    -A config worker \
    --loglevel=info \
    --logfile=/var/log/mlbattle/celery-worker.log \
    --pidfile=/var/run/mlbattle/celery-worker.pid

[Install]
WantedBy=multi-user.target
```

### 4. Celery Beat Service
```bash
sudo nano /etc/systemd/system/mlbattle-celerybeat.service
```

```ini
[Unit]
Description=MLBattle Celery Beat
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/mlbattle/backend
Environment="PATH=/var/www/mlbattle/backend/venv/bin"
ExecStart=/var/www/mlbattle/backend/venv/bin/celery \
    -A config beat \
    --loglevel=info \
    --logfile=/var/log/mlbattle/celery-beat.log \
    --pidfile=/var/run/mlbattle/celery-beat.pid

[Install]
WantedBy=multi-user.target
```

### 5. Create Log Directories
```bash
sudo mkdir -p /var/log/mlbattle
sudo mkdir -p /var/run/mlbattle
sudo chown -R www-data:www-data /var/log/mlbattle
sudo chown -R www-data:www-data /var/run/mlbattle
sudo chown -R www-data:www-data /var/www/mlbattle
```

### 6. Enable and Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable mlbattle
sudo systemctl enable mlbattle-daphne
sudo systemctl enable mlbattle-celery
sudo systemctl enable mlbattle-celerybeat

sudo systemctl start mlbattle
sudo systemctl start mlbattle-daphne
sudo systemctl start mlbattle-celery
sudo systemctl start mlbattle-celerybeat

# Check status
sudo systemctl status mlbattle
sudo systemctl status mlbattle-daphne
sudo systemctl status mlbattle-celery
sudo systemctl status mlbattle-celerybeat
```

---

## 🌐 Configure Nginx

### 1. Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/mlbattle
```

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    client_max_body_size 100M;

    location /static/ {
        alias /var/www/mlbattle/backend/staticfiles/;
    }

    location /media/ {
        alias /var/www/mlbattle/backend/media/;
    }

    location / {
        proxy_pass http://unix:/var/www/mlbattle/backend/mlbattle.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    root /var/www/mlbattle/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 2. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/mlbattle /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 Setup SSL with Let's Encrypt

### 1. Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Obtain SSL Certificates
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
```

Follow the prompts. Certbot will automatically update your Nginx configuration.

### 3. Auto-renewal
```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically sets up a cron job for renewal
```

---

## 📊 Monitoring Setup

### 1. Install Monitoring Tools
```bash
sudo apt install htop iotop -y
```

### 2. Check Logs
```bash
# Application logs
sudo tail -f /var/log/mlbattle/access.log
sudo tail -f /var/log/mlbattle/error.log
sudo tail -f /var/log/mlbattle/celery-worker.log
sudo tail -f /var/log/mlbattle/celery-beat.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u mlbattle -f
sudo journalctl -u mlbattle-daphne -f
sudo journalctl -u mlbattle-celery -f
```

---

## 🔄 Deployment Updates

### Update Backend
```bash
cd /var/www/mlbattle
git pull origin main

cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

sudo systemctl restart mlbattle
sudo systemctl restart mlbattle-daphne
sudo systemctl restart mlbattle-celery
sudo systemctl restart mlbattle-celerybeat
```

### Update Frontend
```bash
cd /var/www/mlbattle/frontend
git pull origin main
npm install
npm run build
sudo systemctl restart nginx
```

---

## 🔐 Security Checklist

- [ ] Set strong `SECRET_KEY` in Django settings
- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Use HTTPS (SSL) for all connections
- [ ] Set secure database passwords
- [ ] Configure firewall (UFW):
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```
- [ ] Keep system and packages updated
- [ ] Regular database backups
- [ ] Monitor logs for suspicious activity
- [ ] Use environment variables for secrets
- [ ] Set up fail2ban for SSH protection

---

## 💾 Backup Strategy

### 1. Database Backup Script
```bash
sudo nano /usr/local/bin/backup-mlbattle.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/mlbattle"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U mlbattle_user mlbattle > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/mlbattle/backend/media

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### 2. Schedule Backups
```bash
sudo chmod +x /usr/local/bin/backup-mlbattle.sh
sudo crontab -e
```

Add:
```
0 2 * * * /usr/local/bin/backup-mlbattle.sh
```

---

## 🐛 Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -xe -u mlbattle

# Check permissions
ls -la /var/www/mlbattle/backend/mlbattle.sock
```

### Database connection issues
```bash
# Test MongoDB connection
mongosh --host localhost --port 27017 -u mlbattle_user -p your_secure_password --authenticationDatabase mlbattle

# Check MongoDB service
sudo systemctl status mongod

# Check MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log
```

### Celery tasks not running
```bash
# Check Celery worker status
sudo systemctl status mlbattle-celery

# Check Redis connection
redis-cli ping

# Check Celery logs
sudo tail -f /var/log/mlbattle/celery-worker.log
```

### WebSocket connection fails
```bash
# Check Daphne service
sudo systemctl status mlbattle-daphne

# Check if port 8001 is listening
sudo netstat -tulpn | grep 8001

# Check Nginx WebSocket proxy
sudo nginx -t
```

---

## 📈 Performance Optimization

### 1. MongoDB Tuning
```bash
sudo nano /etc/mongod.conf
```

Adjust based on your server resources:
```yaml
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 1
net:
  maxIncomingConnections: 1000
operationProfiling:
  mode: slowOp
  slowOpThresholdMs: 100
```

### 2. Redis Configuration
```bash
sudo nano /etc/redis/redis.conf
```

```ini
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### 3. Nginx Caching
Add to Nginx configuration:
```nginx
# Enable gzip compression
gzip on;
gzip_vary on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

---

## ✅ Post-Deployment Checklist

- [ ] All services running (check with `systemctl status`)
- [ ] Website accessible at https://yourdomain.com
- [ ] API accessible at https://api.yourdomain.com
- [ ] WebSocket connection working
- [ ] Can login and register users
- [ ] Admin panel accessible at /admin
- [ ] Celery tasks executing (check logs)
- [ ] SSL certificates valid
- [ ] Backups running
- [ ] Monitoring in place
- [ ] Firewall configured
- [ ] Kaggle API credentials working

---

## 🎉 Congratulations!

Your MLBattle platform is now deployed and running in production! 🚀

For support or questions, refer to:
- **DOCUMENTATION_INDEX.md** - Full documentation guide
- **PROJECT_COMPLETE.md** - Feature overview
- **SETUP_GUIDE.md** - Development setup

---

**Need Help?**
- Check logs first: `/var/log/mlbattle/`
- Review service status: `sudo systemctl status mlbattle*`
- Test individual components
- Review this guide again

**Happy Hosting! 🎉**
