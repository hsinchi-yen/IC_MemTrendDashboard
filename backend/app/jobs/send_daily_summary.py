from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MarketScore
from app.services.email_notifier import send_email
from app.services.line_notifier import send_line
from app.services.telegram_notifier import send_telegram


async def send_daily_summary(db: AsyncSession) -> dict:
    latest = await db.scalar(select(MarketScore).order_by(MarketScore.score_date.desc()).limit(1))
    if latest:
        text = f"記憶體市場日報 {latest.score_date}\n牛熊評分：{latest.total_score} ({latest.status})"
    else:
        text = "記憶體市場日報\n今日資料尚未更新"
    html = f"<h1>記憶體市場日報</h1><p>{text}</p>"
    await send_telegram(text)
    await send_line(text)
    await send_email("記憶體市場日報", text, html)
    return {"status": "success"}
