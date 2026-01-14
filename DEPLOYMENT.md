# Deployment Guide for HemoDay Backend

## Prerequisites

- Docker and Docker Compose installed
- Git (for cloning repository)
- Server with at least 2GB RAM
- Domain name (optional, for production)

## Quick Start with Docker

### 1. Clone Repository

```bash
git clone <repository-url>
cd Backend-hemoday
```

### 2. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and update the following variables:

```env
# Database - Use strong passwords in production
POSTGRES_PASSWORD=your_secure_password_here

# JWT Secret - Generate a new secret key
SECRET_KEY=your_secret_key_here

# Optional: Adjust file upload limits
MAX_FILE_SIZE=10485760  # 10MB
```

To generate a secure secret key:

```bash
openssl rand -hex 32
```

### 3. Start Services

Using Docker Compose:

```bash
docker-compose up -d
```

Or using Makefile:

```bash
make build
make up
```

### 4. Initialize Database

Run migrations:

```bash
docker-compose exec api aerich init -t app.core.config.TORTOISE_ORM
docker-compose exec api aerich init-db
```

Or using Makefile:

```bash
make migrate
```

### 5. Verify Installation

Check if services are running:

```bash
docker-compose ps
```

Test API:

```bash
curl http://localhost:8000/health
```

Access API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Production Deployment

### Security Checklist

1. **Environment Variables**
   - [ ] Change `SECRET_KEY` to a random secret
   - [ ] Use strong `POSTGRES_PASSWORD`
   - [ ] Set appropriate `ACCESS_TOKEN_EXPIRE_MINUTES`

2. **CORS Configuration**
   - [ ] Update `allow_origins` in `app/main.py` to specific domains
   - [ ] Remove wildcard `["*"]` origin

3. **HTTPS/SSL**
   - [ ] Configure reverse proxy (nginx/traefik)
   - [ ] Obtain SSL certificate (Let's Encrypt)

4. **Database**
   - [ ] Use managed PostgreSQL service or secure self-hosted instance
   - [ ] Enable connection pooling
   - [ ] Set up regular backups

5. **File Storage**
   - [ ] Consider using S3/CloudFlare R2 for file uploads
   - [ ] Set up backup for `uploads/` directory

### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name api.hemoday.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.hemoday.com;
    
    ssl_certificate /etc/letsencrypt/live/api.hemoday.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.hemoday.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Max upload size
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring and Maintenance

### View Logs

```bash
# All logs
docker-compose logs -f

# API logs only
docker-compose logs -f api

# Database logs
docker-compose logs -f db
```

Or using Makefile:

```bash
make logs
```

### Database Backup

```bash
# Backup
docker-compose exec db pg_dump -U hemoday hemoday > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T db psql -U hemoday hemoday < backup_20260114.sql
```

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Run migrations
docker-compose exec api aerich upgrade
```

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer**: Use nginx/HAProxy for multiple API instances
2. **Session Storage**: JWT tokens are stateless (no session storage needed)
3. **File Storage**: Use shared storage (S3, NFS) for uploads
4. **Database**: Use connection pooling, consider read replicas

### Vertical Scaling

Adjust Docker resource limits in `docker-compose.yml`:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Troubleshooting

### API won't start

1. Check logs: `docker-compose logs api`
2. Verify database connection
3. Ensure migrations are applied

### Database connection errors

1. Check if database is running: `docker-compose ps db`
2. Verify credentials in `.env`
3. Check network connectivity

### File upload issues

1. Verify `uploads/` directory permissions
2. Check `MAX_FILE_SIZE` setting
3. Verify disk space

## Support

For issues and questions:
- Check API documentation: http://localhost:8000/docs
- Review logs: `docker-compose logs -f`
- Inspect container: `docker-compose exec api /bin/bash`
