"""Report generation service for billing and usage analytics.

This module provides the ReportGenerator class for creating various
reports including usage summaries, billing reports, and revenue analytics.
"""

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Optional

from .config import get_settings
from .db import DynamoDBClient
from .exceptions import CustomerNotFoundError
from .utils import get_billing_period_bounds

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Creates usage and billing reports.

    This class generates various reports including customer usage summaries,
    billing period reports, revenue analytics, and usage trends.
    """

    def __init__(self, table_name: Optional[str] = None, stripe_manager: Optional[Any] = None):
        """Initialize report generator.

        Args:
            table_name: DynamoDB table name (uses env var if not provided)
            stripe_manager: Optional StripeManager instance for payment data
        """
        settings = get_settings()
        self.table_name = table_name or settings.dynamodb_table
        self.db_client = DynamoDBClient(table_name=self.table_name)
        self.stripe_manager = stripe_manager
        self.default_currency = settings.default_currency

        logger.info(f"Initialized ReportGenerator with table: {self.table_name}")

    def generate_usage_report(
        self,
        customer_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = "day",
    ) -> dict[str, Any]:
        """Generate usage report for a customer or all customers.

        Args:
            customer_id: Optional customer ID (None for all customers)
            start_date: Report start date (default: 30 days ago)
            end_date: Report end date (default: now)
            group_by: Grouping period (day, week, month)

        Returns:
            Usage report with aggregated data

        Raises:
            CustomerNotFoundError: If specified customer doesn't exist
        """
        # Set default date range
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Validate customer if specified
        if customer_id:
            customer = self.db_client.get_customer(customer_id)
            if not customer:
                raise CustomerNotFoundError(customer_id)

        # Collect usage data
        if customer_id:
            usage_data = self._get_customer_usage_data(customer_id, start_date, end_date)
        else:
            usage_data = self._get_all_usage_data(start_date, end_date)

        # Aggregate by period
        aggregated = self._aggregate_usage_by_period(usage_data, group_by)

        # Calculate statistics
        stats = self._calculate_usage_statistics(usage_data)

        report = {
            "report_type": "usage",
            "customer_id": customer_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days,
            },
            "group_by": group_by,
            "total_usage": stats["total_usage"],
            "unique_endpoints": stats["unique_endpoints"],
            "peak_day": stats["peak_day"],
            "average_daily_usage": stats["average_daily"],
            "data": aggregated,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(
            f"Generated usage report for {customer_id or 'all customers'}, "
            f"period: {start_date.date()} to {end_date.date()}"
        )

        return report

    def generate_billing_report(
        self,
        customer_id: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
    ) -> dict[str, Any]:
        """Generate billing report for a period.

        Args:
            customer_id: Optional customer ID (None for all customers)
            year: Billing year (default: current year)
            month: Billing month (default: current month)

        Returns:
            Billing report with charges and payment status
        """
        # Set default period
        now = datetime.now(timezone.utc)
        if not year:
            year = now.year
        if not month:
            month = now.month

        period_start, period_end = get_billing_period_bounds(
            datetime(year, month, 1, tzinfo=timezone.utc)
        )

        # Collect billing data
        if customer_id:
            billing_data = self._get_customer_billing_data(customer_id, year, month)
            customers = [billing_data] if billing_data else []
        else:
            customers = self._get_all_billing_data(year, month)

        # Aggregate totals
        total_charges = Decimal("0")
        total_paid = Decimal("0")
        total_pending = Decimal("0")
        total_failed = Decimal("0")

        customer_details = []

        for customer_billing in customers:
            charges = Decimal(str(customer_billing.get("charges_calculated", 0)))
            status = customer_billing.get("payment_status", "pending")

            total_charges += charges

            if status == "paid":
                total_paid += charges
            elif status == "failed":
                total_failed += charges
            else:
                total_pending += charges

            customer_details.append(
                {
                    "customer_id": customer_billing.get("customer_id"),
                    "usage_total": customer_billing.get("usage_total", 0),
                    "charges": float(charges),
                    "currency": self.default_currency,
                    "payment_status": status,
                    "invoice_id": customer_billing.get("invoice_id"),
                }
            )

        report = {
            "report_type": "billing",
            "period": {
                "year": year,
                "month": month,
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
            },
            "summary": {
                "total_customers": len(customer_details),
                "total_charges": float(total_charges),
                "total_paid": float(total_paid),
                "total_pending": float(total_pending),
                "total_failed": float(total_failed),
                "currency": self.default_currency,
            },
            "customers": customer_details,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        if customer_id:
            report["customer_id"] = customer_id

        logger.info(f"Generated billing report for {year}-{month:02d}")

        return report

    def generate_revenue_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = "month",
    ) -> dict[str, Any]:
        """Generate revenue analytics report.

        Args:
            start_date: Report start date (default: 12 months ago)
            end_date: Report end date (default: now)
            group_by: Grouping period (day, week, month, quarter, year)

        Returns:
            Revenue report with trends and analytics
        """
        # Set default date range
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=365)

        # Collect invoice data
        invoices = self._get_invoices_in_range(start_date, end_date)

        # Group by period
        revenue_by_period = self._aggregate_revenue_by_period(invoices, group_by)

        # Calculate metrics
        total_revenue = sum(inv.get("amount", 0) for inv in invoices if inv.get("status") == "paid")
        total_outstanding = sum(
            inv.get("amount", 0) for inv in invoices if inv.get("status") in ["open", "draft"]
        )

        # Calculate growth metrics
        growth_metrics = self._calculate_growth_metrics(revenue_by_period)

        # Customer metrics
        customer_metrics = self._calculate_customer_metrics(invoices)

        report = {
            "report_type": "revenue",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days,
            },
            "group_by": group_by,
            "summary": {
                "total_revenue": total_revenue,
                "total_outstanding": total_outstanding,
                "currency": self.default_currency,
                "invoice_count": len(invoices),
                "paid_invoice_count": len([i for i in invoices if i.get("status") == "paid"]),
            },
            "growth": growth_metrics,
            "customers": customer_metrics,
            "revenue_by_period": revenue_by_period,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"Generated revenue report for {start_date.date()} to {end_date.date()}")

        return report

    def generate_customer_summary(
        self, customer_id: str, include_history: bool = True
    ) -> dict[str, Any]:
        """Generate comprehensive summary for a customer.

        Args:
            customer_id: Customer ID
            include_history: Whether to include historical data

        Returns:
            Customer summary report

        Raises:
            CustomerNotFoundError: If customer doesn't exist
        """
        # Get customer data
        customer = self.db_client.get_customer(customer_id)
        if not customer:
            raise CustomerNotFoundError(customer_id)

        # Current month usage
        now = datetime.now(timezone.utc)
        current_usage = self._get_customer_usage_data(
            customer_id, datetime(now.year, now.month, 1, tzinfo=timezone.utc), now
        )

        # Current month billing
        current_billing = self.db_client.get_billing_period(customer_id, now.year, now.month)

        summary = {
            "customer": {
                "customer_id": customer_id,
                "email": customer.get("email"),
                "name": customer.get("name"),
                "plan_type": customer.get("plan_type"),
                "billing_status": customer.get("billing_status"),
                "stripe_customer_id": customer.get("stripe_customer_id"),
                "created_at": customer.get("created_at"),
            },
            "current_period": {
                "year": now.year,
                "month": now.month,
                "usage_count": sum(u.get("usage_count", 0) for u in current_usage),
                "charges": float(current_billing.get("charges_calculated", 0))
                if current_billing
                else 0,
                "payment_status": current_billing.get("payment_status", "pending")
                if current_billing
                else "no_billing",
            },
        }

        # Add history if requested
        if include_history:
            history = self._get_customer_history(customer_id, months=12)
            summary["history"] = history  # type: ignore[assignment]

        # Calculate lifetime metrics
        lifetime_metrics = self._calculate_lifetime_metrics(customer_id)
        summary["lifetime"] = lifetime_metrics

        summary["generated_at"] = datetime.now(timezone.utc).isoformat()  # type: ignore[assignment]

        logger.info(f"Generated customer summary for {customer_id}")

        return summary

    def export_report(self, report: dict[str, Any], format_type: str = "json") -> str:
        """Export report in specified format.

        Args:
            report: Report data to export
            format: Export format (json, csv)

        Returns:
            Exported report as string
        """
        if format_type == "json":
            return json.dumps(report, indent=2, default=str)

        if format_type == "csv":
            # Simple CSV export for tabular data
            lines = []

            # Extract data section
            if "data" in report:
                data = report["data"]
                if data and isinstance(data, list):
                    # Header
                    headers = list(data[0].keys())
                    lines.append(",".join(headers))

                    # Rows
                    for row in data:
                        values = [str(row.get(h, "")) for h in headers]
                        lines.append(",".join(values))

            return "\n".join(lines)

        raise ValueError(f"Unsupported export format: {format_type}")

    def _get_customer_usage_data(
        self, customer_id: str, start_date: datetime, end_date: datetime
    ) -> list[dict[str, Any]]:
        """Get usage data for a customer."""
        return self.db_client.get_customer_usage(
            customer_id=customer_id, start_date=start_date, end_date=end_date
        )

    def _get_all_usage_data(self, start_date: datetime, end_date: datetime) -> list[dict[str, Any]]:
        """Get usage data for all customers in date range."""
        all_usage = []

        # Iterate through each day in range
        current_date = start_date
        while current_date < end_date:
            daily_usage = self.db_client.get_usage_by_date(current_date)
            all_usage.extend(daily_usage)
            current_date += timedelta(days=1)

        return all_usage

    def _get_customer_billing_data(
        self, customer_id: str, year: int, month: int
    ) -> Optional[dict[str, Any]]:
        """Get billing data for a customer."""
        return self.db_client.get_billing_period(customer_id, year, month)

    def _get_all_billing_data(self, year: int, month: int) -> list[dict[str, Any]]:
        """Get billing data for all customers in a period."""
        # This would typically scan the table for all billing records
        # For now, return empty list as placeholder
        logger.warning("Full table scan for billing data not implemented")
        return []

    def _get_invoices_in_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[dict[str, Any]]:
        """Get all invoices in date range."""
        # This would typically query invoices by date range
        # For now, return empty list as placeholder
        logger.warning("Invoice range query not implemented")
        return []

    def _aggregate_usage_by_period(
        self, usage_data: list[dict[str, Any]], group_by: str
    ) -> list[dict[str, Any]]:
        """Aggregate usage data by time period."""
        aggregated: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"usage_count": 0, "endpoints": set()}
        )

        for record in usage_data:
            timestamp_str = record.get("timestamp", "")
            if not timestamp_str:  # Skip records without timestamp
                continue
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except (ValueError, TypeError):
                continue  # Skip invalid timestamps

            if group_by == "day":
                key = timestamp.strftime("%Y-%m-%d")
            elif group_by == "week":
                key = timestamp.strftime("%Y-W%U")
            elif group_by == "month":
                key = timestamp.strftime("%Y-%m")
            else:
                key = timestamp.strftime("%Y-%m-%d")

            aggregated[key]["usage_count"] += record.get("usage_count", 0)
            aggregated[key]["endpoints"].add(record.get("api_endpoint", ""))

        # Convert to list and clean up
        result = []
        for period, data in sorted(aggregated.items()):
            result.append(
                {
                    "period": period,
                    "usage_count": data["usage_count"],
                    "unique_endpoints": len(data["endpoints"]),
                    "endpoints": list(data["endpoints"]),
                }
            )

        return result

    def _aggregate_revenue_by_period(
        self, invoices: list[dict[str, Any]], group_by: str
    ) -> list[dict[str, Any]]:
        """Aggregate revenue by time period."""
        aggregated: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"revenue": Decimal("0"), "invoice_count": 0, "customer_count": set()}
        )

        for invoice in invoices:
            if invoice.get("status") != "paid":
                continue

            created_at = datetime.fromisoformat(invoice.get("created_at", ""))

            if group_by == "day":
                key = created_at.strftime("%Y-%m-%d")
            elif group_by == "week":
                key = created_at.strftime("%Y-W%U")
            elif group_by == "month":
                key = created_at.strftime("%Y-%m")
            elif group_by == "quarter":
                quarter = (created_at.month - 1) // 3 + 1
                key = f"{created_at.year}-Q{quarter}"
            elif group_by == "year":
                key = str(created_at.year)
            else:
                key = created_at.strftime("%Y-%m")

            aggregated[key]["revenue"] += Decimal(str(invoice.get("amount", 0)))
            aggregated[key]["invoice_count"] += 1
            aggregated[key]["customer_count"].add(invoice.get("customer_id"))

        # Convert to list
        result = []
        for period, data in sorted(aggregated.items()):
            result.append(
                {
                    "period": period,
                    "revenue": float(data["revenue"]),
                    "invoice_count": data["invoice_count"],
                    "unique_customers": len(data["customer_count"]),
                }
            )

        return result

    def _calculate_usage_statistics(self, usage_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate usage statistics."""
        if not usage_data:
            return {"total_usage": 0, "unique_endpoints": 0, "peak_day": None, "average_daily": 0}

        # Total usage
        total_usage = sum(r.get("usage_count", 0) for r in usage_data)

        # Unique endpoints (filter out None values)
        endpoints = {r.get("api_endpoint") for r in usage_data if r.get("api_endpoint")}

        # Daily aggregation for peak day
        daily_usage: dict[Any, int] = defaultdict(int)
        for record in usage_data:
            timestamp_str = record.get("timestamp", "")
            usage_count = record.get("usage_count", 0)
            if (
                timestamp_str and usage_count is not None
            ):  # Skip empty timestamps or None usage counts
                try:
                    date = datetime.fromisoformat(timestamp_str).date()
                    daily_usage[date] += usage_count
                except (ValueError, TypeError):
                    # Skip invalid timestamps
                    continue

        # Peak day
        peak_day = None
        if daily_usage:
            peak_date = max(daily_usage, key=lambda x: daily_usage[x])
            peak_day = {"date": peak_date.isoformat(), "usage": daily_usage[peak_date]}
            daily_usage[peak_date]

        # Average daily
        days = len(daily_usage)
        average_daily = total_usage / days if days > 0 else 0

        return {
            "total_usage": total_usage,
            "unique_endpoints": len(endpoints),
            "peak_day": peak_day,
            "average_daily": round(average_daily, 2),
        }

    def _calculate_growth_metrics(self, revenue_by_period: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate revenue growth metrics."""
        if len(revenue_by_period) < 2:
            return {"growth_rate": 0, "trend": "stable"}

        # Compare last two periods
        current = revenue_by_period[-1]["revenue"]
        previous = revenue_by_period[-2]["revenue"]

        growth_rate = 0
        if previous > 0:
            growth_rate = ((current - previous) / previous) * 100

        # Determine trend
        if growth_rate > 10:
            trend = "growing"
        elif growth_rate < -10:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "growth_rate": round(growth_rate, 2),
            "trend": trend,
            "current_period_revenue": current,
            "previous_period_revenue": previous,
        }

    def _calculate_customer_metrics(self, invoices: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate customer-related metrics."""
        customer_revenues: dict[str, Decimal] = defaultdict(Decimal)

        for invoice in invoices:
            if invoice.get("status") == "paid":
                customer_id = invoice.get("customer_id")
                if customer_id:
                    customer_revenues[customer_id] += Decimal(str(invoice.get("amount", 0)))

        if not customer_revenues:
            return {"total_customers": 0, "average_revenue_per_customer": 0, "top_customers": []}

        # Calculate average
        total_customers = len(customer_revenues)
        total_revenue = sum(customer_revenues.values())
        average_revenue = total_revenue / total_customers

        # Get top customers
        top_customers = sorted(customer_revenues.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_customers": total_customers,
            "average_revenue_per_customer": float(average_revenue),
            "top_customers": [
                {"customer_id": cid, "revenue": float(rev)} for cid, rev in top_customers
            ],
        }

    def _get_customer_history(self, customer_id: str, months: int) -> list[dict[str, Any]]:
        """Get customer billing history."""
        history = []
        now = datetime.now(timezone.utc)

        for i in range(months):
            # Calculate month
            month_offset = now.month - i
            year = now.year

            while month_offset <= 0:
                month_offset += 12
                year -= 1

            # Get billing data for month
            billing = self.db_client.get_billing_period(customer_id, year, month_offset)

            if billing:
                history.append(
                    {
                        "period": f"{year:04d}-{month_offset:02d}",
                        "usage": billing.get("usage_total", 0),
                        "charges": float(billing.get("charges_calculated", 0)),
                        "status": billing.get("payment_status", "unknown"),
                    }
                )

        return history

    def _calculate_lifetime_metrics(self, customer_id: str) -> dict[str, Any]:
        """Calculate lifetime metrics for a customer."""
        # This would typically aggregate all historical data
        # For now, return placeholder metrics
        return {
            "total_usage": 0,
            "total_revenue": 0,
            "months_active": 0,
            "average_monthly_usage": 0,
            "average_monthly_revenue": 0,
        }
