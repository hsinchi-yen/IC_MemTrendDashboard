from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import NewsItem

router = APIRouter(tags=["news"])


@router.get("/news/latest")
async def latest_news(db: AsyncSession = Depends(get_db)) -> list[dict]:
    rows = (await db.scalars(select(NewsItem).order_by(NewsItem.created_at.desc()).limit(20))).all()
    return [
        {
            "id": row.id,
            "title": row.title,
            "source": row.source,
            "published_at": row.published_at,
            "sentiment": row.sentiment or "neutral",
            "summary": (row.key_points[0] if row.key_points else row.content or ""),
        }
        for row in rows
    ]
