from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .database import get_db, init_db
from .models import MonitoredURL, HealthCheck
from .schemas import URLCreate, URLResponse, HealthCheckResponse
from .pinger import check_all_urls

scheduler = AsyncIOScheduler(job_defaults={"misfire_grace_time": 60, "coalesce": True})


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    scheduler.add_job(
        check_all_urls, "interval", seconds=30, id="ping_job",
        replace_existing=True, next_run_time=datetime.now(timezone.utc)
    )
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="Uptime Monitor", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/urls", response_model=URLResponse)
async def create_url(payload: URLCreate, db: AsyncSession = Depends(get_db)):
    monitored_url = MonitoredURL(url=str(payload.url), name=payload.name)
    db.add(monitored_url)
    await db.commit()
    await db.refresh(monitored_url)
    return URLResponse(
        id=monitored_url.id,
        url=monitored_url.url,
        name=monitored_url.name,
        created_at=monitored_url.created_at,
        latest_check=None,
    )


@app.get("/api/urls", response_model=list[URLResponse])
async def list_urls(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MonitoredURL).options(selectinload(MonitoredURL.checks))
    )
    urls = result.scalars().all()

    response = []
    for url in urls:
        latest_check = None
        if url.checks:
            latest = max(url.checks, key=lambda c: c.checked_at)
            latest_check = HealthCheckResponse(
                id=latest.id,
                status_code=latest.status_code,
                response_time_ms=latest.response_time_ms,
                is_up=latest.is_up,
                checked_at=latest.checked_at,
            )
        response.append(
            URLResponse(
                id=url.id,
                url=url.url,
                name=url.name,
                created_at=url.created_at,
                latest_check=latest_check,
            )
        )
    return response


@app.delete("/api/urls/{url_id}")
async def delete_url(url_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MonitoredURL).where(MonitoredURL.id == url_id))
    url = result.scalar_one_or_none()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    await db.delete(url)
    await db.commit()
    return {"detail": "deleted"}


@app.get("/api/urls/{url_id}/checks", response_model=list[HealthCheckResponse])
async def get_checks(url_id: int, limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MonitoredURL).where(MonitoredURL.id == url_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="URL not found")

    result = await db.execute(
        select(HealthCheck)
        .where(HealthCheck.url_id == url_id)
        .order_by(desc(HealthCheck.checked_at))
        .limit(limit)
    )
    return result.scalars().all()
