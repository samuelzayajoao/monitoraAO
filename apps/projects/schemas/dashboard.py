from ninja import Schema
from typing import List, Optional, Literal
from datetime import datetime
from pydantic import field_validator


class DashboardFilterSchema(Schema):
    period: Optional[Literal["today", "week", "month"]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def validate_iso_format(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                # Tenta fazer o parse estrito para garantir que não é um mero número/timestamp
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("Must be a valid ISO 8601 date string, not a timestamp")
        elif isinstance(v, (int, float)):
            raise ValueError("Numeric timestamps are not allowed. Use ISO 8601.")
        return v


class PeriodSchema(Schema):
    start: datetime
    end: datetime


class SummarySchema(Schema):
    revenue: float
    sales_count: int
    average_ticket: float


class ComparisonSchema(Schema):
    revenue_growth: float
    sales_growth: float
    average_ticket_growth: float


class ChartDataPointSchema(Schema):
    date: str
    revenue: float
    sales: int


class ChartDataSchema(Schema):
    interval: str
    data: List[ChartDataPointSchema]


class TopProductSchema(Schema):
    name: str
    quantity: int
    revenue: float


class RecentSaleSchema(Schema):
    id: str
    product: str
    category: Optional[str] = None
    external_ref: Optional[str] = None
    quantity: int
    total: float
    date: datetime


class DashboardResponseSchema(Schema):
    period: PeriodSchema
    summary: SummarySchema
    comparison: ComparisonSchema
    chart: ChartDataSchema
    top_products: List[TopProductSchema]
    recent_sales: List[RecentSaleSchema]
