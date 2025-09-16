# TradingGrow Production Deployment Guide

## Overview
This guide covers deploying TradingGrow to your own server with production-ready configurations, real financial data integration, and security best practices.

## Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ or CentOS 8+ (recommended)
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 50GB SSD
- **CPU**: Minimum 2 cores, Recommended 4+ cores
- **Network**: Public IP address for web access

### Required Software
- Docker & Docker Compose
- Nginx (if not using Docker setup)
- PostgreSQL 15+ (if not using Docker)
- Redis (if not using Docker)
- SSL certificates (Let's Encrypt recommended)

## Quick Start with Docker (Recommended)

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again to apply Docker group changes
```

### 2. Clone and Setup Project
```bash
# Clone your repository
git clone https://github.com/yourusername/tradinggrow.git
cd tradinggrow

# Copy production environment template
cp production.env .env

# Generate secure secrets
openssl rand -hex 32  # Use for SESSION_SECRET
openssl rand -hex 32  # Use for JWT_SECRET_KEY
openssl rand -base64 32  # Use for DB_PASSWORD
```

### 3. Configure Environment Variables
Edit the `.env` file with your actual values:

```bash
# Required - Database
DATABASE_URL=postgresql://tradinggrow:YOUR_SECURE_DB_PASSWORD@db:5432/tradinggrow_prod
DB_PASSWORD=YOUR_SECURE_DB_PASSWORD

# Required - Security
SESSION_SECRET=your-64-character-secret-from-openssl-command
JWT_SECRET_KEY=your-second-64-character-secret

# Optional but Recommended - Financial Data APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
POLYGON_API_KEY=your_polygon_key
FMP_API_KEY=your_fmp_key

# Optional - OAuth (for social login)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Optional - Payments
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key

# Domain Configuration
DOMAIN=yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 4. SSL Certificate Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate (replace yourdomain.com)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to project
sudo mkdir -p ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem
sudo chown -R $USER:$USER ssl/
```

### 5. Deploy Application
```bash
# Build and start all services
docker-compose up -d

# Check if all services are running
docker-compose ps

# View logs
docker-compose logs -f app

# Initialize database (first time only)
docker-compose exec app flask db upgrade
```

### 6. Verify Deployment
```bash
# Check health endpoint
curl https://yourdomain.com/health

# Check application
curl https://yourdomain.com/

# Monitor logs
docker-compose logs -f
```

## Financial Data API Setup

### Alpha Vantage (Recommended - Free tier available)
1. Visit: https://www.alphavantage.co/support/#api-key
2. Sign up for free account
3. Get your API key
4. Add to `.env`: `ALPHA_VANTAGE_API_KEY=your_key_here`
5. Limits: 5 requests/minute, 500 requests/day (free tier)

### Polygon.io (Alternative)
1. Visit: https://polygon.io/
2. Sign up and get API key
3. Add to `.env`: `POLYGON_API_KEY=your_key_here`
4. Better rate limits but requires paid plan for real-time data

### Financial Modeling Prep (Alternative)
1. Visit: https://financialmodelingprep.com/developer/docs
2. Get API key
3. Add to `.env`: `FMP_API_KEY=your_key_here`

## Security Configuration

### Firewall Setup
```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH (change 22 to your SSH port if different)
sudo ufw allow 22

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Check status
sudo ufw status
```

### SSL Certificate Auto-Renewal
```bash
# Add to crontab for automatic renewal
sudo crontab -e

# Add this line to run twice daily
0 12 * * * /usr/bin/certbot renew --quiet
```

### Database Security
```bash
# Connect to database container
docker-compose exec db psql -U tradinggrow tradinggrow_prod

# Create additional database users if needed
CREATE USER readonly_user WITH PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
```

## Production Optimization

### 1. Database Performance
```sql
-- Connect to database and run these optimizations
docker-compose exec db psql -U tradinggrow tradinggrow_prod

-- Create indexes for better performance
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_user_subscription ON users(subscription_tier);
CREATE INDEX idx_watchlist_user ON watchlists(user_id);

-- Update table statistics
ANALYZE;
```

### 2. Enable Monitoring
```bash
# Add monitoring service to docker-compose.yml
# Or set up external monitoring like:
# - New Relic
# - DataDog
# - Prometheus + Grafana
```

### 3. Backup Configuration
```bash
# The docker-compose.yml includes automatic daily backups
# Backups are stored in ./backups/ directory

# Manual backup
docker-compose exec db pg_dump -U tradinggrow tradinggrow_prod > backup_$(date +%Y%m%d).sql

# Restore from backup
docker-compose exec -T db psql -U tradinggrow tradinggrow_prod < backup_file.sql
```

## Manual Installation (Without Docker)

### 1. Install Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip postgresql-15 redis-server nginx nodejs npm

# Create application user
sudo useradd -m -s /bin/bash tradinggrow
sudo mkdir -p /opt/tradinggrow
sudo chown tradinggrow:tradinggrow /opt/tradinggrow
```

### 2. Setup Application
```bash
# Switch to app user
sudo su - tradinggrow

# Clone repository
cd /opt/tradinggrow
git clone https://github.com/yourusername/tradinggrow.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies and build frontend
npm install
npm run build
```

### 3. Database Setup
```bash
# Switch to postgres user
sudo su - postgres

# Create database and user
createdb tradinggrow_prod
createuser tradinggrow
psql -c "ALTER USER tradinggrow WITH PASSWORD 'secure_password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE tradinggrow_prod TO tradinggrow;"
```

### 4. Configure Services

#### Systemd Service for Application
```bash
# Create service file
sudo nano /etc/systemd/system/tradinggrow.service
```

```ini
[Unit]
Description=TradingGrow Financial Platform
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=tradinggrow
Group=tradinggrow
WorkingDirectory=/opt/tradinggrow
Environment=PATH=/opt/tradinggrow/venv/bin
ExecStart=/opt/tradinggrow/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Nginx Configuration
```bash
# Create Nginx site configuration
sudo nano /etc/nginx/sites-available/tradinggrow
```

Use the nginx.conf content from the project, then:

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/tradinggrow /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Start Services
```bash
# Enable and start services
sudo systemctl enable tradinggrow redis postgresql nginx
sudo systemctl start tradinggrow redis postgresql nginx

# Check status
sudo systemctl status tradinggrow
```

## Monitoring and Maintenance

### Log Monitoring
```bash
# Application logs
docker-compose logs -f app

# Database logs
docker-compose logs -f db

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Performance Monitoring
```bash
# Check resource usage
docker stats

# Database performance
docker-compose exec db psql -U tradinggrow -d tradinggrow_prod -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;"
```

### Update Procedure
```bash
# 1. Backup database
docker-compose exec db pg_dump -U tradinggrow tradinggrow_prod > backup_before_update.sql

# 2. Pull latest code
git pull origin main

# 3. Rebuild and restart
docker-compose build
docker-compose up -d

# 4. Run any database migrations
docker-compose exec app flask db upgrade

# 5. Verify deployment
curl https://yourdomain.com/health
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database container
   docker-compose logs db
   
   # Test connection
   docker-compose exec db psql -U tradinggrow tradinggrow_prod -c "SELECT 1;"
   ```

2. **SSL Certificate Issues**
   ```bash
   # Check certificate validity
   openssl x509 -in ssl/cert.pem -text -noout
   
   # Renew certificate
   sudo certbot renew
   ```

3. **API Rate Limiting**
   ```bash
   # Check financial API logs
   docker-compose logs app | grep "API"
   
   # Verify API keys
   curl "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AAPL&interval=1min&apikey=YOUR_API_KEY"
   ```

4. **High Memory Usage**
   ```bash
   # Check memory usage
   docker stats
   
   # Restart services if needed
   docker-compose restart
   ```

### Getting Help
- Check application logs: `docker-compose logs -f app`
- Health check: `curl https://yourdomain.com/health/detailed`
- Database status: `docker-compose exec db pg_isready`

## Security Checklist

- [ ] SSL certificates installed and auto-renewing
- [ ] Firewall configured (ports 80, 443, SSH only)
- [ ] Strong passwords for all accounts
- [ ] Environment variables properly secured
- [ ] Database user has minimal required permissions
- [ ] Regular backups configured and tested
- [ ] Monitoring and alerting set up
- [ ] Log rotation configured
- [ ] SSH key-based authentication (disable password auth)
- [ ] Regular security updates applied

## Performance Optimization

### Database Tuning
```sql
-- PostgreSQL performance settings (add to postgresql.conf)
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### Redis Optimization
```bash
# Redis configuration for caching
# Add to redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
```

### Application Scaling
```bash
# Scale application containers
docker-compose up -d --scale app=3

# Use load balancer (nginx upstream)
# Configure multiple app instances in nginx.conf
```

This completes your production deployment guide. The application is now ready for real-world use with proper security, monitoring, and real financial data integration.