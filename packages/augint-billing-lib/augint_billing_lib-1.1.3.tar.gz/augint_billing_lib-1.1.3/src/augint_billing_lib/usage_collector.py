"""Usage collection service for tracking API usage.

This module provides the UsageCollector class for tracking and storing
API usage data in DynamoDB with proper validation and aggregation.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from .config import get_settings
from .db import DynamoDBClient
from .exceptions import (
    CustomerNotFoundError,
    DynamoDBError,
    PricingConfigurationError,
    RateLimitError,
)
from .models import UsageRecord
from .types import UsagePeriodDict
from .utils import validate_usage

logger = logging.getLogger(__name__)


class UsageCollector:
    """Collects and stores API usage data.

    This class handles tracking API usage, validating usage records,
    checking rate limits, and storing usage data in DynamoDB.
    """

    def __init__(self, table_name: Optional[str] = None):
        """Initialize usage collector.

        Args:
            table_name: DynamoDB table name (uses env var if not provided)
        """
        settings = get_settings()
        self.table_name = table_name or settings.dynamodb_table
        self.db_client = DynamoDBClient(table_name=self.table_name)
        self.default_rate_limit = settings.default_rate_limit
        self.rate_limit_window = settings.rate_limit_window_seconds

        logger.info(f"Initialized UsageCollector with table: {self.table_name}")

    def track_usage(
        self,
        customer_id: str,
        api_endpoint: str,
        usage_count: int = 1,
        timestamp: Optional[datetime] = None,
        validate: bool = True,
        check_rate_limit: bool = True,
    ) -> UsageRecord:
        """Track API usage for a customer.

        Args:
            customer_id: Customer ID
            api_endpoint: API endpoint that was called
            usage_count: Number of calls (default 1)
            timestamp: When the usage occurred (default now)
            validate: Whether to validate the usage record
            check_rate_limit: Whether to check rate limits

        Returns:
            Created usage record

        Raises:
            CustomerNotFoundError: If customer doesn't exist
            UsageValidationError: If validation fails
            RateLimitError: If rate limit exceeded
            DynamoDBError: If storage fails
        """
        # Verify customer exists
        customer = self.db_client.get_customer(customer_id)
        if not customer:
            raise CustomerNotFoundError(customer_id)

        # Create usage record
        record_timestamp = timestamp or datetime.now(timezone.utc)
        date_str = record_timestamp.strftime("%Y-%m-%d")
        timestamp_str = record_timestamp.isoformat()

        usage_record = UsageRecord(
            pk=f"USAGE#{customer_id}",
            sk=f"USAGE#{date_str}#{timestamp_str}",
            gsi1pk=f"USAGE#{date_str}",
            gsi1sk=customer_id,
            customer_id=customer_id,
            api_endpoint=api_endpoint,
            usage_count=usage_count,
            timestamp=record_timestamp,
        )

        # Validate if requested
        if validate:
            validate_usage(usage_record)

        # Check rate limits if requested
        if check_rate_limit:
            self._check_rate_limit(customer_id, customer.get("plan_type", "free"))

        # Store in DynamoDB
        try:
            self.db_client.put_item(usage_record.model_dump())
            logger.info(
                f"Tracked usage for customer {customer_id}: {usage_count} calls to {api_endpoint}"
            )
            return usage_record

        except Exception as e:
            logger.exception("Failed to track usage: ")
            raise DynamoDBError(
                "Failed to store usage record",
                table_name=self.table_name,
                operation="put_item",
                original_error=e,
            ) from e

    def track_batch_usage(
        self, usage_records: list[dict[str, Any]], validate: bool = True
    ) -> list[UsageRecord]:
        """Track multiple usage records in batch.

        Args:
            usage_records: List of usage record data
            validate: Whether to validate records

        Returns:
            List of created usage records

        Raises:
            UsageValidationError: If validation fails
            DynamoDBError: If storage fails
        """
        records = []
        items_to_write = []

        for record_data in usage_records:
            # Create and validate record
            record = UsageRecord(**record_data)

            if validate:
                validate_usage(record)

            records.append(record)
            items_to_write.append(record.model_dump())

        # Batch write to DynamoDB
        try:
            self.db_client.batch_write(items_to_write, operation="put")
            logger.info(f"Tracked {len(records)} usage records in batch")
            return records

        except Exception as e:
            logger.exception("Failed to track batch usage: ")
            raise DynamoDBError(
                "Failed to store batch usage records",
                table_name=self.table_name,
                operation="batch_write",
                original_error=e,
            ) from e

    def get_customer_usage(
        self,
        customer_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> list[UsageRecord]:
        """Get usage records for a customer.

        Args:
            customer_id: Customer ID
            start_date: Start of date range (optional)
            end_date: End of date range (optional)
            limit: Maximum records to return

        Returns:
            List of usage records

        Raises:
            DynamoDBError: If query fails
        """
        try:
            items = self.db_client.get_customer_usage(
                customer_id=customer_id, start_date=start_date, end_date=end_date, limit=limit
            )

            # Convert to UsageRecord models
            records = [UsageRecord(**item) for item in items]

            logger.debug(f"Retrieved {len(records)} usage records for customer {customer_id}")
            return records

        except Exception as e:
            logger.exception("Failed to get customer usage: ")
            raise DynamoDBError(
                "Failed to retrieve usage records",
                table_name=self.table_name,
                operation="query",
                original_error=e,
            ) from e

    def get_usage_by_period(self, customer_id: str, year: int, month: int) -> UsagePeriodDict:
        """Get aggregated usage for a billing period.

        Args:
            customer_id: Customer ID
            year: Billing year
            month: Billing month

        Returns:
            Aggregated usage data with total count and breakdown

        Raises:
            DynamoDBError: If query fails
        """
        # Calculate date range for the month
        start_date = datetime(year, month, 1, tzinfo=timezone.utc)
        december = 12
        if month == december:
            end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)

        # Get all usage records for the period
        records = self.get_customer_usage(
            customer_id=customer_id, start_date=start_date, end_date=end_date
        )

        # Aggregate by endpoint
        endpoint_usage = {}
        total_usage = 0

        for record in records:
            endpoint = record.api_endpoint
            if endpoint not in endpoint_usage:
                endpoint_usage[endpoint] = 0
            endpoint_usage[endpoint] += record.usage_count
            total_usage += record.usage_count

        return {
            "customer_id": customer_id,
            "period": f"{year:04d}-{month:02d}",
            "total_usage": total_usage,
            "endpoint_breakdown": endpoint_usage,
            "record_count": len(records),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }

    def get_daily_usage(
        self, date: datetime, customer_id: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Get usage records for a specific day.

        Args:
            date: Date to query
            customer_id: Optional customer filter

        Returns:
            List of usage records for the day

        Raises:
            DynamoDBError: If query fails
        """
        try:
            items = self.db_client.get_usage_by_date(date=date, customer_id=customer_id)

            # Aggregate by customer if no specific customer requested
            if not customer_id:
                customer_totals: dict[str, dict[str, Any]] = {}
                for item in items:
                    cust_id = item.get("customer_id")
                    if not cust_id:
                        continue
                    if cust_id not in customer_totals:
                        customer_totals[cust_id] = {
                            "customer_id": cust_id,
                            "date": date.strftime("%Y-%m-%d"),
                            "total_usage": 0,
                            "endpoints": set(),
                        }

                    customer_totals[cust_id]["total_usage"] += item.get("usage_count", 0)
                    customer_totals[cust_id]["endpoints"].add(item.get("api_endpoint"))

                # Convert sets to lists for JSON serialization
                for data in customer_totals.values():
                    data["endpoints"] = list(data["endpoints"])

                return list(customer_totals.values())

            # Return raw records for specific customer
            return items

        except Exception as e:
            logger.exception("Failed to get daily usage: ")
            raise DynamoDBError(
                "Failed to retrieve daily usage",
                table_name=self.table_name,
                operation="query",
                original_error=e,
            ) from e

    def _check_rate_limit(self, customer_id: str, plan_type: str) -> None:
        """Check if customer has exceeded rate limits.

        Args:
            customer_id: Customer ID
            plan_type: Customer's plan type

        Raises:
            RateLimitError: If rate limit exceeded
            PricingConfigurationError: If plan type is unknown
        """
        # Get rate limit for plan type
        rate_limits = {"free": 1000, "paid": 10000, "enterprise": 100000}

        if plan_type not in rate_limits:
            raise PricingConfigurationError(
                plan_type=plan_type,
                message=f"Unknown plan type: {plan_type}. Cannot determine rate limit.",
            )

        limit = rate_limits[plan_type]

        # Calculate time window
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=self.rate_limit_window)

        # Get usage in window
        recent_usage = self.get_customer_usage(
            customer_id=customer_id, start_date=window_start, end_date=now
        )

        # Calculate total usage
        total_usage = sum(record.usage_count for record in recent_usage)

        # Check against limit
        if total_usage >= limit:
            reset_time = (now + timedelta(seconds=self.rate_limit_window)).isoformat()
            raise RateLimitError(
                customer_id=customer_id, limit=limit, current=total_usage, reset_time=reset_time
            )

    def cleanup_old_usage(self, days_to_keep: int = 730) -> int:
        """Clean up old usage records.

        Args:
            days_to_keep: Number of days of data to keep (default 2 years)

        Returns:
            Number of records deleted

        Note:
            This should be run as a scheduled job, not during normal operations.
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

        # This would typically be implemented as a batch job
        # scanning for old records and deleting them
        logger.info(f"Would clean up usage records older than {cutoff_date}")

        # In production, this would:
        # 1. Scan for records with timestamp < cutoff_date
        # 2. Batch delete old records
        # 3. Return count of deleted records

        return 0  # Placeholder
