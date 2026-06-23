from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PaginatedResponse(BaseModel):
    total_count: int
    data: list


class InstrumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    market: str
    name: str | None = None
    name_en: str | None = None
    tier: str
    supply_chain_tag: str | None = None
    currency: str | None = None
    is_active: bool
    score_weight: Decimal
    score_only_observe: bool


class PriceRow(BaseModel):
    date: date
    open: Decimal | None = None
    high: Decimal | None = None
    low: Decimal | None = None
    close: Decimal | None = None
    volume: int | None = None


class QuoteRow(BaseModel):
    product: str
    category: str
    price_type: str | None = None
    price_avg: Decimal | None = None
    change_pct: Decimal | None = None
    snapshot_date: date


class ScoreRow(BaseModel):
    score_date: date
    total_score: Decimal | None = None
    status: str | None = None
    narrative: dict | None = None
    sub_scores: dict | None = None


class TrendMetricRow(BaseModel):
    as_of_date: date
    period: str
    change_pct: Decimal | None = None
    direction: str | None = None
    momentum: Decimal | None = None
    ma_state: dict | None = None
    volatility: Decimal | None = None
    streak: int | None = None
    normalized_index: Decimal | None = None
    narrative: str | None = None


class RefreshStatus(BaseModel):
    job_id: str | None = None
    status: str
    progress: dict | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_msg: str | None = None


class RefreshHealthSection(BaseModel):
    last_updated: datetime | None = None
    hours_since_update: float | None = None
    is_stale: bool
    threshold_hours: int


class RefreshHealthResponse(BaseModel):
    overall_status: str
    equity_prices: RefreshHealthSection
    memory_quotes: RefreshHealthSection
    last_scheduler_run: dict | None = None


class AlertRuleIn(BaseModel):
    rule_name: str
    metric: str
    condition: str
    threshold: Decimal
    channel: str
    is_active: bool = True


class AlertRulePatch(BaseModel):
    rule_name: str | None = None
    metric: str | None = None
    condition: str | None = None
    threshold: Decimal | None = None
    channel: str | None = None
    is_active: bool | None = None


class AlertRuleOut(AlertRuleIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class MarketEventIn(BaseModel):
    event_date: date
    title: str
    description: str | None = None
    related_tickers: list[str] = Field(default_factory=list)
    category: str


class MarketEventOut(MarketEventIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class BacktestRequest(BaseModel):
    entry_condition: str
    exit_condition: str
    start_date: date
    end_date: date
    target: str
