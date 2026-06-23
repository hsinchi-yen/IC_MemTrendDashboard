from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import AlertEvent, AlertRule
from app.schemas import AlertRuleIn, AlertRuleOut, AlertRulePatch

router = APIRouter(tags=["alerts"])
VALID_METRICS = {"total_score", "dram_spot_1d_change", "nand_wafer_ma_cross"}
VALID_CONDITIONS = {"gt", "lt", "cross_up", "cross_down"}
VALID_CHANNELS = {"telegram", "line", "email"}


def _validate_rule(metric: str, condition: str, channel: str) -> None:
    if not (metric in VALID_METRICS or metric.startswith("stock_1d_change.")):
        raise HTTPException(status_code=422, detail="invalid_metric")
    if condition not in VALID_CONDITIONS:
        raise HTTPException(status_code=422, detail="invalid_condition")
    if channel not in VALID_CHANNELS:
        raise HTTPException(status_code=422, detail="invalid_channel")


@router.get("/alerts/rules")
async def list_rules(db: AsyncSession = Depends(get_db)) -> list[AlertRuleOut]:
    rows = (await db.scalars(select(AlertRule).order_by(AlertRule.id.desc()))).all()
    return [AlertRuleOut.model_validate(row) for row in rows]


@router.post("/alerts/rules")
async def create_rule(payload: AlertRuleIn, db: AsyncSession = Depends(get_db)) -> AlertRuleOut:
    _validate_rule(payload.metric, payload.condition, payload.channel)
    rule = AlertRule(**payload.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return AlertRuleOut.model_validate(rule)


@router.patch("/alerts/rules/{rule_id}")
async def update_rule(rule_id: int, payload: AlertRulePatch, db: AsyncSession = Depends(get_db)) -> AlertRuleOut:
    rule = await db.get(AlertRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="rule_not_found")
    values = payload.model_dump(exclude_unset=True)
    _validate_rule(values.get("metric", rule.metric), values.get("condition", rule.condition), values.get("channel", rule.channel))
    for key, value in values.items():
        setattr(rule, key, value)
    await db.commit()
    await db.refresh(rule)
    return AlertRuleOut.model_validate(rule)


@router.delete("/alerts/rules/{rule_id}", status_code=204)
async def delete_rule(rule_id: int, db: AsyncSession = Depends(get_db)) -> None:
    rule = await db.get(AlertRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="rule_not_found")
    await db.delete(rule)
    await db.commit()


@router.get("/alerts/events")
async def list_alert_events(db: AsyncSession = Depends(get_db)) -> list[dict]:
    rows = (await db.scalars(select(AlertEvent).order_by(AlertEvent.created_at.desc()))).all()
    return [
        {
            "id": row.id,
            "rule_id": row.rule_id,
            "metric_value": row.metric_value,
            "notify_status": row.notify_status,
            "message": row.message,
            "created_at": row.created_at,
        }
        for row in rows
    ]
