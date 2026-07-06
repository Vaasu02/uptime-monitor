import httpx
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select

from .database import async_session
from .models import MonitoredURL, HealthCheck


async def ping_url(url: str, timeout: float = 10.0) -> dict:
    headers = {
        "User-Agent": "UptimeMoitor/1.0"
    }
    try:
        async with httpx.AsyncClient() as client:
            start = asyncio.get_event_loop().time()
            response = await client.get(url, timeout=timeout, follow_redirects=True, headers=headers)
            elapsed_ms = (asyncio.get_event_loop().time() - start) * 1000
            return {
                "status_code": response.status_code,
                "response_time_ms": round(elapsed_ms, 2),
                "is_up": response.status_code < 500,
            }
    except (httpx.TimeoutException, httpx.ConnectError, httpx.RequestError):
        return {
            "status_code": None,
            "response_time_ms": None,
            "is_up": False,
        }


async def check_all_urls():
    async with async_session() as session:
        result = await session.execute(select(MonitoredURL))
        urls = result.scalars().all()

        for monitored_url in urls:
            ping_result = await ping_url(monitored_url.url)
            check = HealthCheck(
                url_id=monitored_url.id,
                status_code=ping_result["status_code"],
                response_time_ms=ping_result["response_time_ms"],
                is_up=ping_result["is_up"],
                checked_at=datetime.now(timezone.utc),
            )
            session.add(check)

        await session.commit()
