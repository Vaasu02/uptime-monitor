# Uptime Monitor

A lightweight, full-stack application that periodically pings a list of URLs and displays whether each one is active, along with its response time.

## Tech Stack

- **Backend:** FastAPI (Python 3.11), SQLAlchemy 2.0 (async), APScheduler, httpx
- **Frontend:** React 18 + Vite, Tailwind CSS
- **Database:** PostgreSQL 15
- **Containerization:** Docker Compose

---

## 1-Line Setup

```bash
docker compose up --build
```

The app will be available at **http://localhost:3000**

---

## Testing Steps

After running `docker compose up --build`, wait for all containers to start (you'll see `Uvicorn running on http://0.0.0.0:8000` in the logs).

### Via the UI (http://localhost:3000):

1. **Add a healthy URL:**
   - Enter `https://example.com` in the URL field
   - Enter `Example` in the Name field
   - Click "Add URL"

2. **Add a broken URL:**
   - Enter `https://thisurldoesnotexist.invalid` in the URL field
   - Enter `Broken Site` in the Name field
   - Click "Add URL"

3. **Wait ~30 seconds** for the first ping cycle.

4. **Observe:**
   - `https://example.com` → Green dot, response time ~200-400ms
   - `https://thisurldoesnotexist.invalid` → Red dot, no response time (—)

### Via curl (API directly):

```bash
# Add a healthy URL
curl -X POST http://localhost:8000/api/urls \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "name": "Example"}'

# Add a broken URL
curl -X POST http://localhost:8000/api/urls \
  -H "Content-Type: application/json" \
  -d '{"url": "https://thisurldoesnotexist.invalid", "name": "Broken Site"}'

# Check results after 30 seconds
curl http://localhost:8000/api/urls
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/urls` | Register a URL to monitor |
| GET | `/api/urls` | List all URLs with latest status |
| DELETE | `/api/urls/{id}` | Remove a URL from monitoring |
| GET | `/api/urls/{id}/checks` | Get check history for a URL |

### Request body for POST /api/urls:
```json
{
  "url": "https://example.com",
  "name": "Optional display name"
}
```

---

## Architecture

```
┌────────────┐       ┌────────────┐       ┌────────────┐
│  Frontend  │──/api──│  Backend   │───────│ PostgreSQL │
│  (Nginx)   │       │  (FastAPI) │       │            │
│  Port 3000 │       │  Port 8000 │       │  Port 5432 │
└────────────┘       └────────────┘       └────────────┘
                           │
                     APScheduler
                     (every 30s)
                           │
                     Pings all URLs
                     via httpx
```

---

## Deployment Sketch

For production, I would deploy this on AWS using the following topology:

- **Frontend:** Static build served via S3 + CloudFront CDN
- **Backend:** ECS Fargate (serverless containers) behind an ALB
- **Database:** RDS PostgreSQL (managed, with automated backups)

### Hypothetical Terraform snippet:

```hcl
resource "aws_ecs_service" "backend" {
  name            = "uptime-monitor-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }
}

resource "aws_db_instance" "postgres" {
  engine               = "postgres"
  engine_version       = "15"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  db_name              = "uptime_monitor"
  username             = "postgres"
  password             = var.db_password
  skip_final_snapshot  = true
}

resource "aws_s3_bucket" "frontend" {
  bucket = "uptime-monitor-frontend"
}

resource "aws_cloudfront_distribution" "frontend" {
  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "s3-frontend"
  }
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "s3-frontend"
    viewer_protocol_policy = "redirect-to-https"
  }
}
```

**MVP alternative:** For quick validation, run `docker compose up` on a single EC2 instance with Docker installed. This is what we'd do for the first few users before investing in managed infrastructure.
