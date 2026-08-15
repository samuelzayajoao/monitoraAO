from ninja import Schema
from typing import List, Optional
from datetime import datetime

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
