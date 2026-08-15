from django.contrib.auth import get_user_model
from ..models import Project
from asgiref.sync import sync_to_async
from ninja.errors import HttpError
from django.db.models import Q

User = get_user_model()


class ProjectServices:
    async def create_project(self, user, payload):
        payload_dict = payload.model_dump()
        project, created = await Project.objects.aget_or_create(
            user=user, name=payload_dict["name"], defaults={**payload_dict}
        )
        if not created:
            return 200, project
        return 201, project

    async def get_project(self, user, project_id):
        try:
            project = await Project.objects.aget(
                Q(user=user) | Q(project_collaborator__user=user),
                id=project_id,
                is_active=True,
            )
        except Project.DoesNotExist:
            raise HttpError(404, "Project not found")
        return 200, project

    async def update_project(self, user, project_id, payload):
        try:
            project = await Project.objects.aget(
                user=user, id=project_id, is_active=True
            )
        except Project.DoesNotExist:
            raise HttpError(404, "Project not found")
        for key, value in payload.dict().items():
            if value is not None:
                setattr(project, key, value)
        await project.asave()
        return project

    async def delete_project(self, user, project_id):
        try:
            project = await Project.objects.aget(
                user=user, id=project_id, is_active=True
            )
        except Project.DoesNotExist:
            raise HttpError(404, "Project not found")
        await project.adelete()
        return project

    async def list_projects(self, user):
        projects = await sync_to_async(list)(
            Project.objects.filter(
                Q(project_collaborator__user=user) | Q(user=user), is_active=True
            )
            .distinct()
            .order_by("-created_at")
        )
        return projects

    async def get_dashboard(self, user, project_id, period, start_date_str, end_date_str):
        from datetime import datetime, timedelta, timezone
        from django.db.models import Sum, Count, F
        from django.db.models.functions import TruncDate
        from apps.sales.models import Sales
        
        try:
            project = await Project.objects.aget(
                Q(user=user) | Q(project_collaborator__user=user),
                id=project_id,
                is_active=True,
            )
        except Project.DoesNotExist:
            raise HttpError(404, "Project not found")

        now = datetime.now(timezone.utc)
        if start_date_str and end_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
            end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
        else:
            if period == 'today':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            elif period == 'week':
                start_date = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            else: # month default
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
                
        duration = end_date - start_date
        prev_start = start_date - duration
        prev_end = start_date - timedelta(microseconds=1)

        sales_qs = Sales.objects.filter(project=project, sold_at__gte=start_date, sold_at__lte=end_date)
        prev_sales_qs = Sales.objects.filter(project=project, sold_at__gte=prev_start, sold_at__lte=prev_end)

        current_agg = await sales_qs.aaggregate(
            revenue=Sum(F('product_price') * F('product_quantity')),
            sales_count=Count('id')
        )
        revenue = float(current_agg['revenue'] or 0.0)
        sales_count = current_agg['sales_count'] or 0
        avg_ticket = revenue / sales_count if sales_count > 0 else 0.0

        prev_agg = await prev_sales_qs.aaggregate(
            revenue=Sum(F('product_price') * F('product_quantity')),
            sales_count=Count('id')
        )
        prev_revenue = float(prev_agg['revenue'] or 0.0)
        prev_sales_count = prev_agg['sales_count'] or 0
        prev_avg_ticket = prev_revenue / prev_sales_count if prev_sales_count > 0 else 0.0

        rev_growth = ((revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else (100.0 if revenue > 0 else 0.0)
        sales_growth = ((sales_count - prev_sales_count) / prev_sales_count * 100) if prev_sales_count > 0 else (100.0 if sales_count > 0 else 0.0)
        ticket_growth = ((avg_ticket - prev_avg_ticket) / prev_avg_ticket * 100) if prev_avg_ticket > 0 else (100.0 if avg_ticket > 0 else 0.0)

        @sync_to_async
        def get_chart_data():
            interval = "hour" if (end_date - start_date).days < 1 else "day"
            
            if interval == "hour":
                from django.db.models.functions import TruncHour
                grouped = sales_qs.annotate(date=TruncHour('sold_at')).values('date').annotate(
                    revenue=Sum(F('product_price') * F('product_quantity')),
                    sales=Count('id')
                ).order_by('date')
            else:
                grouped = sales_qs.annotate(date=TruncDate('sold_at')).values('date').annotate(
                    revenue=Sum(F('product_price') * F('product_quantity')),
                    sales=Count('id')
                ).order_by('date')
            
            chart_list = []
            
            if interval == "hour":
                daily_dict = {item['date'].replace(minute=0, second=0, microsecond=0): item for item in grouped if item['date']}
                curr = start_date.replace(minute=0, second=0, microsecond=0)
                end_d = end_date.replace(minute=0, second=0, microsecond=0)
                
                while curr <= end_d:
                    if curr in daily_dict:
                        chart_list.append({
                            'date': curr.isoformat(),
                            'revenue': float(daily_dict[curr]['revenue'] or 0.0),
                            'sales': daily_dict[curr]['sales']
                        })
                    else:
                        chart_list.append({
                            'date': curr.isoformat(),
                            'revenue': 0.0,
                            'sales': 0
                        })
                    curr += timedelta(hours=1)
            else:
                daily_dict = {item['date']: item for item in grouped if item['date']}
                curr = start_date.date()
                end_d = end_date.date()
                
                while curr <= end_d:
                    if curr in daily_dict:
                        chart_list.append({
                            'date': curr.isoformat(),
                            'revenue': float(daily_dict[curr]['revenue'] or 0.0),
                            'sales': daily_dict[curr]['sales']
                        })
                    else:
                        chart_list.append({
                            'date': curr.isoformat(),
                            'revenue': 0.0,
                            'sales': 0
                        })
                    curr += timedelta(days=1)
            
            return interval, chart_list
            
        chart_interval, chart_data = await get_chart_data()

        @sync_to_async
        def get_top_products():
            return list(sales_qs.values('product_name').annotate(
                revenue=Sum(F('product_price') * F('product_quantity')),
                quantity=Sum('product_quantity')
            ).order_by('-revenue')[:5])
            
        top_prods_raw = await get_top_products()
        top_products = [
            {
                'name': p['product_name'],
                'quantity': p['quantity'],
                'revenue': float(p['revenue'] or 0.0)
            } for p in top_prods_raw
        ]
        
        @sync_to_async
        def get_recent_sales():
            return list(sales_qs.order_by('-sold_at')[:10])
            
        recent_sales_raw = await get_recent_sales()
        recent_sales = [
            {
                'id': str(s.id),
                'product': s.product_name,
                'category': str(s.category.value) if hasattr(s.category, 'value') else str(s.category) if s.category else None,
                'external_ref': s.external_ref,
                'quantity': s.product_quantity,
                'total': float(s.product_price * s.product_quantity),
                'date': s.sold_at
            } for s in recent_sales_raw
        ]

        return 200, {
            "period": {
                "start": start_date,
                "end": end_date
            },
            "summary": {
                "revenue": revenue,
                "sales_count": sales_count,
                "average_ticket": avg_ticket
            },
            "comparison": {
                "revenue_growth": round(rev_growth, 2),
                "sales_growth": round(sales_growth, 2),
                "average_ticket_growth": round(ticket_growth, 2)
            },
            "chart": {
                "interval": chart_interval,
                "data": chart_data
            },
            "top_products": top_products,
            "recent_sales": recent_sales
        }
