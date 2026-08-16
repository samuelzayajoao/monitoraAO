"""
Refatoração do endpoint de dashboard de vendas.

Objetivo: quebrar uma função monolítica em componentes pequenos e coesos,
cada um com uma única responsabilidade (SRP), para que possam ser
reutilizados, testados isoladamente e substituídos sem afetar o resto
(OCP/DIP). A classe `SalesDashboardService` apenas orquestra os
colaboradores; toda a lógica de negócio fica encapsulada em classes
específicas.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from django.db.models import Sum, Count, F, QuerySet, Q
from django.db.models.functions import TruncDate, TruncHour
from asgiref.sync import sync_to_async

from apps.sales.models import Sales
from apps.projects.models import Project  # ajuste o import conforme seu projeto
from ninja.errors import HttpError


# ---------------------------------------------------------------------------
# 1. Acesso e permissão ao projeto
# ---------------------------------------------------------------------------
class ProjectAccessResolver:
    """Responsável apenas por localizar o projeto e validar acesso do usuário."""

    async def get_authorized_project(self, user, project_id) -> "Project":
        try:
            return await Project.objects.aget(
                Q(user=user) | Q(project_collaborator__user=user),
                id=project_id,
                is_active=True,
            )
        except Project.DoesNotExist:
            raise HttpError(404, "Project not found")


# ---------------------------------------------------------------------------
# 2. Resolução de período (atual e anterior)
# ---------------------------------------------------------------------------
class DateRange:
    """Objeto simples de valor para representar um intervalo de datas."""

    __slots__ = ("start", "end")

    def __init__(self, start: datetime, end: datetime):
        self.start = start
        self.end = end

    @property
    def duration(self) -> timedelta:
        return self.end - self.start

    def is_intraday(self) -> bool:
        return self.duration.days < 1

    def previous(self) -> "DateRange":
        """Retorna o intervalo anterior de mesma duração, usado na comparação."""
        prev_end = self.start - timedelta(microseconds=1)
        prev_start = self.start - self.duration
        return DateRange(prev_start, prev_end)


class PeriodResolver:
    """
    Responsável apenas por transformar (period, start_date_str, end_date_str)
    em um DateRange. Isolar essa regra facilita adicionar novos períodos
    (ex: "quarter", "year") sem tocar no restante do sistema.
    """

    def resolve(
        self,
        period: str,
        start_date_str: Optional[str],
        end_date_str: Optional[str],
    ) -> DateRange:
        if start_date_str and end_date_str:
            return self._from_explicit_dates(start_date_str, end_date_str)
        return self._from_named_period(period)

    def _from_explicit_dates(self, start_date_str: str, end_date_str: str) -> DateRange:
        start = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
        end = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
        return DateRange(start, end)

    def _from_named_period(self, period: str) -> DateRange:
        now = datetime.now(timezone.utc)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        strategies = {
            "today": self._today_start,
            "week": self._week_start,
        }
        start_fn = strategies.get(period, self._month_start)
        return DateRange(start_fn(now), end)

    @staticmethod
    def _today_start(now: datetime) -> datetime:
        return now.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def _week_start(now: datetime) -> datetime:
        return (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    @staticmethod
    def _month_start(now: datetime) -> datetime:
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


# ---------------------------------------------------------------------------
# 3. Construção de querysets
# ---------------------------------------------------------------------------
class SalesQueryBuilder:
    """Responsável apenas por montar querysets de Sales filtrados por projeto/período."""

    def for_range(self, project, date_range: DateRange) -> QuerySet:
        return Sales.objects.filter(
            project=project,
            sold_at__gte=date_range.start,
            sold_at__lte=date_range.end,
        )


# ---------------------------------------------------------------------------
# 4. Cálculo de crescimento percentual (regra reutilizável e testável)
# ---------------------------------------------------------------------------
class GrowthCalculator:
    """Calcula variação percentual entre valor atual e anterior."""

    @staticmethod
    def percentage_change(current: float, previous: float) -> float:
        if previous > 0:
            return round((current - previous) / previous * 100, 2)
        return 100.0 if current > 0 else 0.0


# ---------------------------------------------------------------------------
# 5. Métricas agregadas (revenue, sales_count, ticket médio)
# ---------------------------------------------------------------------------
class SalesMetrics:
    """Objeto de valor com as métricas de um período."""

    __slots__ = ("revenue", "sales_count", "average_ticket")

    def __init__(self, revenue: float, sales_count: int):
        self.revenue = revenue
        self.sales_count = sales_count
        self.average_ticket = revenue / sales_count if sales_count > 0 else 0.0

    def as_dict(self) -> dict:
        return {
            "revenue": self.revenue,
            "sales_count": self.sales_count,
            "average_ticket": self.average_ticket,
        }


class SalesMetricsAggregator:
    """Responsável apenas por agregar revenue/quantidade a partir de um queryset."""

    async def aggregate(self, sales_qs: QuerySet) -> SalesMetrics:
        result = await sales_qs.aaggregate(
            revenue=Sum(F("product_price") * F("product_quantity")),
            sales_count=Count("id"),
        )
        revenue = float(result["revenue"] or 0.0)
        sales_count = result["sales_count"] or 0
        return SalesMetrics(revenue=revenue, sales_count=sales_count)


class MetricsComparator:
    """
    Responsável apenas por comparar métricas atuais x anteriores e produzir
    o bloco de "comparison" (revenue_growth, sales_growth, ticket_growth).
    """

    def __init__(self, growth_calculator: GrowthCalculator):
        self._growth = growth_calculator

    def compare(self, current: SalesMetrics, previous: SalesMetrics) -> dict:
        return {
            "revenue_growth": self._growth.percentage_change(
                current.revenue, previous.revenue
            ),
            "sales_growth": self._growth.percentage_change(
                current.sales_count, previous.sales_count
            ),
            "average_ticket_growth": self._growth.percentage_change(
                current.average_ticket, previous.average_ticket
            ),
        }


# ---------------------------------------------------------------------------
# 6. Dados do gráfico (agrupamento por hora/dia + preenchimento de gaps)
# ---------------------------------------------------------------------------
class ChartDataBuilder:
    """
    Responsável apenas por gerar a série temporal do gráfico, incluindo o
    preenchimento de intervalos sem vendas (gaps) com zero.
    """

    def interval_for(self, date_range: DateRange) -> str:
        return "hour" if date_range.is_intraday() else "day"

    @sync_to_async
    def build(
        self, sales_qs: QuerySet, date_range: DateRange
    ) -> tuple[str, list[dict]]:
        interval = self.interval_for(date_range)
        grouped = self._grouped_totals(sales_qs, interval)

        if interval == "hour":
            return interval, self._fill_hourly_gaps(grouped, date_range)
        return interval, self._fill_daily_gaps(grouped, date_range)

    def _grouped_totals(self, sales_qs: QuerySet, interval: str):
        trunc_fn = TruncHour if interval == "hour" else TruncDate
        return (
            sales_qs.annotate(date=trunc_fn("sold_at"))
            .values("date")
            .annotate(
                revenue=Sum(F("product_price") * F("product_quantity")),
                sales=Count("id"),
            )
            .order_by("date")
        )

    def _fill_hourly_gaps(self, grouped, date_range: DateRange) -> list[dict]:
        bucket_by_hour = {
            item["date"].replace(minute=0, second=0, microsecond=0): item
            for item in grouped
            if item["date"]
        }
        cursor = date_range.start.replace(minute=0, second=0, microsecond=0)
        last = date_range.end.replace(minute=0, second=0, microsecond=0)

        chart = []
        while cursor <= last:
            chart.append(
                self._chart_point(cursor.isoformat(), bucket_by_hour.get(cursor))
            )
            cursor += timedelta(hours=1)
        return chart

    def _fill_daily_gaps(self, grouped, date_range: DateRange) -> list[dict]:
        bucket_by_day = {item["date"]: item for item in grouped if item["date"]}
        cursor = date_range.start.date()
        last = date_range.end.date()

        chart = []
        while cursor <= last:
            chart.append(
                self._chart_point(cursor.isoformat(), bucket_by_day.get(cursor))
            )
            cursor += timedelta(days=1)
        return chart

    @staticmethod
    def _chart_point(date_iso: str, bucket: Optional[dict]) -> dict:
        if not bucket:
            return {"date": date_iso, "revenue": 0.0, "sales": 0}
        return {
            "date": date_iso,
            "revenue": float(bucket["revenue"] or 0.0),
            "sales": bucket["sales"],
        }


# ---------------------------------------------------------------------------
# 7. Top produtos
# ---------------------------------------------------------------------------
class TopProductsFinder:
    """Responsável apenas por retornar o ranking de produtos mais vendidos."""

    def __init__(self, limit: int = 5):
        self._limit = limit

    @sync_to_async
    def find(self, sales_qs: QuerySet) -> list[dict]:
        raw = list(
            sales_qs.values("product_name")
            .annotate(
                revenue=Sum(F("product_price") * F("product_quantity")),
                quantity=Sum("product_quantity"),
            )
            .order_by("-revenue")[: self._limit]
        )
        return [
            {
                "name": p["product_name"],
                "quantity": p["quantity"],
                "revenue": float(p["revenue"] or 0.0),
            }
            for p in raw
        ]


# ---------------------------------------------------------------------------
# 8. Vendas recentes
# ---------------------------------------------------------------------------
class RecentSalesSerializer:
    """Responsável apenas por transformar instâncias de Sales em dicts para a API."""

    def serialize(self, sale) -> dict:
        return {
            "id": str(sale.id),
            "product": sale.product_name,
            "category": self._serialize_category(sale.category),
            "external_ref": sale.external_ref,
            "quantity": sale.product_quantity,
            "total": float(sale.product_price * sale.product_quantity),
            "date": sale.sold_at,
        }

    @staticmethod
    def _serialize_category(category) -> Optional[str]:
        if category is None:
            return None
        return str(category.value) if hasattr(category, "value") else str(category)


class RecentSalesFinder:
    """Responsável apenas por buscar e serializar as vendas mais recentes."""

    def __init__(self, serializer: RecentSalesSerializer, limit: int = 10):
        self._serializer = serializer
        self._limit = limit

    @sync_to_async
    def find(self, sales_qs: QuerySet) -> list[dict]:
        raw = list(sales_qs.order_by("-sold_at")[: self._limit])
        return [self._serializer.serialize(sale) for sale in raw]


# ---------------------------------------------------------------------------
# 9. Orquestrador: junta todos os colaboradores acima
# ---------------------------------------------------------------------------
class SalesDashboardService:
    """
    Orquestra a montagem do dashboard, delegando cada responsabilidade a um
    colaborador dedicado. Não contém lógica de negócio própria — apenas
    coordena a chamada dos componentes na ordem certa.

    Cada colaborador pode ser injetado (DIP), o que facilita testes com
    mocks e substituição de comportamento sem alterar esta classe.
    """

    def __init__(
        self,
        project_resolver: Optional[ProjectAccessResolver] = None,
        period_resolver: Optional[PeriodResolver] = None,
        query_builder: Optional[SalesQueryBuilder] = None,
        metrics_aggregator: Optional[SalesMetricsAggregator] = None,
        metrics_comparator: Optional[MetricsComparator] = None,
        chart_builder: Optional[ChartDataBuilder] = None,
        top_products_finder: Optional[TopProductsFinder] = None,
        recent_sales_finder: Optional[RecentSalesFinder] = None,
    ):
        self._project_resolver = project_resolver or ProjectAccessResolver()
        self._period_resolver = period_resolver or PeriodResolver()
        self._query_builder = query_builder or SalesQueryBuilder()
        self._metrics_aggregator = metrics_aggregator or SalesMetricsAggregator()
        self._metrics_comparator = metrics_comparator or MetricsComparator(
            GrowthCalculator()
        )
        self._chart_builder = chart_builder or ChartDataBuilder()
        self._top_products_finder = top_products_finder or TopProductsFinder()
        self._recent_sales_finder = recent_sales_finder or RecentSalesFinder(
            RecentSalesSerializer()
        )

    async def get_dashboard(
        self, user, project_id, period, start_date_str, end_date_str
    ) -> tuple[int, dict]:
        project = await self._project_resolver.get_authorized_project(user, project_id)

        date_range = self._period_resolver.resolve(period, start_date_str, end_date_str)
        previous_range = date_range.previous()

        current_qs = self._query_builder.for_range(project, date_range)
        previous_qs = self._query_builder.for_range(project, previous_range)

        current_metrics = await self._metrics_aggregator.aggregate(current_qs)
        previous_metrics = await self._metrics_aggregator.aggregate(previous_qs)
        comparison = self._metrics_comparator.compare(current_metrics, previous_metrics)

        chart_interval, chart_data = await self._chart_builder.build(
            current_qs, date_range
        )
        top_products = await self._top_products_finder.find(current_qs)
        recent_sales = await self._recent_sales_finder.find(current_qs)

        return 200, {
            "period": {"start": date_range.start, "end": date_range.end},
            "summary": current_metrics.as_dict(),
            "comparison": comparison,
            "chart": {"interval": chart_interval, "data": chart_data},
            "top_products": top_products,
            "recent_sales": recent_sales,
        }


# ---------------------------------------------------------------------------
# Uso no endpoint (exemplo)
# ---------------------------------------------------------------------------
# class DashboardController:
#     def __init__(self):
#         self._service = SalesDashboardService()
#
#     async def get_dashboard(self, user, project_id, period, start_date_str, end_date_str):
#         return await self._service.get_dashboard(
#             user, project_id, period, start_date_str, end_date_str
#         )
