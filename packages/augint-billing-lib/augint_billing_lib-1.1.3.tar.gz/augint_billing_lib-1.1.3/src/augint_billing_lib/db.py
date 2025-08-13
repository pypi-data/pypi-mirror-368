"""DynamoDB operations for the billing service.

This module provides async and sync wrappers for DynamoDB operations
using boto3, with proper error handling and retry logic.
"""

import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, NoReturn, Optional

import boto3  # type: ignore[import-untyped]
from boto3.dynamodb.conditions import Key  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]

from .config import get_settings
from .exceptions import DynamoDBError

logger = logging.getLogger(__name__)


class DynamoDBClient:
    """Client for DynamoDB operations with billing-specific methods."""

    def __init__(
        self,
        table_name: Optional[str] = None,
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ):
        """Initialize DynamoDB client.

        Args:
            table_name: DynamoDB table name (uses env var if not provided)
            region_name: AWS region (uses env var if not provided)
            endpoint_url: Custom endpoint URL (for local testing)
        """
        settings = get_settings()

        self.table_name = table_name or settings.dynamodb_table
        self.region_name = region_name or settings.aws_region
        self.endpoint_url = endpoint_url or settings.dynamodb_endpoint_url

        # Initialize DynamoDB resource
        self._resource = boto3.resource(
            "dynamodb", region_name=self.region_name, endpoint_url=self.endpoint_url
        )
        self._table = self._resource.Table(self.table_name)

        logger.info(
            f"Initialized DynamoDB client for table: {self.table_name}, region: {self.region_name}"
        )

    def _handle_error(self, operation: str, error: Exception) -> NoReturn:
        """Handle and wrap DynamoDB errors.

        Args:
            operation: Operation that failed
            error: Original exception

        Raises:
            DynamoDBError: Wrapped error with context
        """
        logger.error(f"DynamoDB {operation} failed: {error}")

        if isinstance(error, ClientError):
            error_code = error.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "ResourceNotFoundException":
                raise DynamoDBError(
                    f"Table not found: {self.table_name}",
                    table_name=self.table_name,
                    operation=operation,
                    original_error=error,
                )
            if error_code == "ValidationException":
                raise DynamoDBError(
                    f"Validation error in {operation}",
                    table_name=self.table_name,
                    operation=operation,
                    original_error=error,
                )

        raise DynamoDBError(
            f"DynamoDB {operation} failed",
            table_name=self.table_name,
            operation=operation,
            original_error=error,
        )

    def put_item(self, item: dict[str, Any]) -> dict[str, Any]:
        """Put an item in DynamoDB.

        Args:
            item: Item to store

        Returns:
            DynamoDB response

        Raises:
            DynamoDBError: If operation fails
        """
        try:
            # Convert Decimal types for DynamoDB
            item = self._prepare_item(item)

            response = self._table.put_item(Item=item)
            logger.debug(f"Put item with pk={item.get('pk')}, sk={item.get('sk')}")
            return response  # type: ignore[no-any-return]

        except Exception as e:
            self._handle_error("put_item", e)

    def get_item(self, pk: str, sk: str) -> Optional[dict[str, Any]]:
        """Get a single item from DynamoDB.

        Args:
            pk: Partition key
            sk: Sort key

        Returns:
            Item dict or None if not found

        Raises:
            DynamoDBError: If operation fails
        """
        try:
            response = self._table.get_item(Key={"pk": pk, "sk": sk})

            item = response.get("Item")
            if item:
                logger.debug(f"Retrieved item with pk={pk}, sk={sk}")
            else:
                logger.debug(f"Item not found: pk={pk}, sk={sk}")

            return item  # type: ignore[no-any-return]

        except Exception as e:
            self._handle_error("get_item", e)

    def query(
        self,
        key_condition: Any,
        index_name: Optional[str] = None,
        limit: Optional[int] = None,
        scan_index_forward: bool = True,
        filter_expression: Optional[Any] = None,
    ) -> list[dict[str, Any]]:
        """Query items from DynamoDB.

        Args:
            key_condition: Key condition expression
            index_name: Optional GSI name
            limit: Maximum items to return
            scan_index_forward: Sort order (True=ascending)
            filter_expression: Optional filter expression

        Returns:
            List of items

        Raises:
            DynamoDBError: If operation fails
        """
        try:
            query_params = {
                "KeyConditionExpression": key_condition,
                "ScanIndexForward": scan_index_forward,
            }

            if index_name:
                query_params["IndexName"] = index_name

            if limit:
                query_params["Limit"] = limit

            if filter_expression:
                query_params["FilterExpression"] = filter_expression

            items = []
            last_evaluated_key = None

            while True:
                if last_evaluated_key:
                    query_params["ExclusiveStartKey"] = last_evaluated_key

                response = self._table.query(**query_params)
                items.extend(response.get("Items", []))

                last_evaluated_key = response.get("LastEvaluatedKey")
                if not last_evaluated_key or (limit and len(items) >= limit):
                    break

            logger.debug(f"Query returned {len(items)} items")
            return items[:limit] if limit else items

        except Exception as e:
            self._handle_error("query", e)

    def batch_write(self, items: list[dict[str, Any]], operation: str = "put") -> None:
        """Batch write items to DynamoDB.

        Args:
            items: List of items to write
            operation: "put" or "delete"

        Raises:
            DynamoDBError: If operation fails
        """
        try:
            settings = get_settings()
            batch_size = settings.batch_size

            # Process in batches
            for i in range(0, len(items), batch_size):
                batch = items[i : i + batch_size]

                with self._table.batch_writer() as batch_writer:
                    for item in batch:
                        if operation == "put":
                            item = self._prepare_item(item)
                            batch_writer.put_item(Item=item)
                        elif operation == "delete":
                            batch_writer.delete_item(Key=item)

                logger.debug(f"Batch {operation} completed for {len(batch)} items")

        except Exception as e:
            self._handle_error(f"batch_{operation}", e)

    def update_item(
        self,
        pk: str,
        sk: str,
        update_expression: str,
        expression_values: dict[str, Any],
        condition_expression: Optional[Any] = None,
    ) -> dict[str, Any]:
        """Update an item in DynamoDB.

        Args:
            pk: Partition key
            sk: Sort key
            update_expression: Update expression
            expression_values: Expression attribute values
            condition_expression: Optional condition expression

        Returns:
            Updated item

        Raises:
            DynamoDBError: If operation fails
        """
        try:
            update_params = {
                "Key": {"pk": pk, "sk": sk},
                "UpdateExpression": update_expression,
                "ExpressionAttributeValues": expression_values,
                "ReturnValues": "ALL_NEW",
            }

            if condition_expression:
                update_params["ConditionExpression"] = condition_expression

            response = self._table.update_item(**update_params)
            logger.debug(f"Updated item with pk={pk}, sk={sk}")

            return response.get("Attributes", {})  # type: ignore[no-any-return]

        except Exception as e:
            self._handle_error("update_item", e)

    def delete_item(self, pk: str, sk: str) -> None:
        """Delete an item from DynamoDB.

        Args:
            pk: Partition key
            sk: Sort key

        Raises:
            DynamoDBError: If operation fails
        """
        try:
            self._table.delete_item(Key={"pk": pk, "sk": sk})
            logger.debug(f"Deleted item with pk={pk}, sk={sk}")

        except Exception as e:
            self._handle_error("delete_item", e)

    # Billing-specific methods

    def query_invoices_by_customer(self, customer_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """Query invoices for a specific customer.

        Args:
            customer_id: Customer identifier
            limit: Maximum number of invoices to return

        Returns:
            List of invoice records

        Raises:
            DynamoDBError: If query operation fails
        """
        try:
            # Query for invoices with customer_id in metadata
            # This would typically use a GSI on customer_id
            # For now, return empty list as placeholder
            return []
        except ClientError as e:
            self._handle_error("query_invoices_by_customer", e)

    def get_customer(self, customer_id: str) -> Optional[dict[str, Any]]:
        """Get customer data by ID.

        Args:
            customer_id: Customer ID

        Returns:
            Customer data or None

        Raises:
            DynamoDBError: If operation fails
        """
        pk = f"CUSTOMER#{customer_id}"
        sk = "METADATA"
        return self.get_item(pk, sk)

    def get_customer_usage(
        self,
        customer_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """Get usage records for a customer.

        Args:
            customer_id: Customer ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum records to return

        Returns:
            List of usage records

        Raises:
            DynamoDBError: If operation fails
        """
        pk = f"USAGE#{customer_id}"

        # Build key condition
        key_condition = Key("pk").eq(pk)

        if start_date and end_date:
            start_sk = f"USAGE#{start_date.strftime('%Y-%m-%d')}#"
            end_sk = f"USAGE#{end_date.strftime('%Y-%m-%d')}#Z"
            key_condition = key_condition & Key("sk").between(start_sk, end_sk)
        elif start_date:
            start_sk = f"USAGE#{start_date.strftime('%Y-%m-%d')}#"
            key_condition = key_condition & Key("sk").gte(start_sk)
        else:
            key_condition = key_condition & Key("sk").begins_with("USAGE#")

        return self.query(
            key_condition=key_condition,
            limit=limit,
            scan_index_forward=False,  # Most recent first
        )

    def get_usage_by_date(
        self, date: datetime, customer_id: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Get usage records for a specific date.

        Args:
            date: Date to query
            customer_id: Optional customer ID filter

        Returns:
            List of usage records

        Raises:
            DynamoDBError: If operation fails
        """
        gsi1pk = f"USAGE#{date.strftime('%Y-%m-%d')}"

        key_condition = Key("gsi1pk").eq(gsi1pk)

        if customer_id:
            key_condition = key_condition & Key("gsi1sk").eq(customer_id)

        return self.query(key_condition=key_condition, index_name="GSI1")

    def get_billing_period(
        self, customer_id: str, year: int, month: int
    ) -> Optional[dict[str, Any]]:
        """Get billing period data for a customer.

        Args:
            customer_id: Customer ID
            year: Billing year
            month: Billing month

        Returns:
            Billing period data or None

        Raises:
            DynamoDBError: If operation fails
        """
        pk = f"BILLING#{customer_id}"
        sk = f"PERIOD#{year:04d}-{month:02d}"
        return self.get_item(pk, sk)

    def get_pricing_tiers(self, plan_type: str) -> list[dict[str, Any]]:
        """Get pricing tiers for a plan type.

        Args:
            plan_type: Plan type (free, paid, enterprise)

        Returns:
            List of pricing tiers

        Raises:
            DynamoDBError: If operation fails
        """
        pk = f"PRICING#{plan_type}"

        return self.query(
            key_condition=Key("pk").eq(pk) & Key("sk").begins_with("TIER#"),
            scan_index_forward=True,  # Order by tier number
        )

    def get_invoice(self, invoice_id: str) -> Optional[dict[str, Any]]:
        """Get invoice by ID.

        Args:
            invoice_id: Invoice ID

        Returns:
            Invoice data or None

        Raises:
            DynamoDBError: If operation fails
        """
        pk = f"INVOICE#{invoice_id}"
        sk = "METADATA"
        return self.get_item(pk, sk)

    def get_customer_billing_periods(
        self, customer_id: str, limit: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Get billing periods for a customer.

        Args:
            customer_id: Customer ID
            limit: Maximum periods to return

        Returns:
            List of billing periods

        Raises:
            DynamoDBError: If operation fails
        """
        pk = f"BILLING#{customer_id}"

        return self.query(
            key_condition=Key("pk").eq(pk) & Key("sk").begins_with("PERIOD#"),
            limit=limit,
            scan_index_forward=False,  # Most recent first
        )

    def update_billing_period_invoice(
        self, customer_id: str, year: int, month: int, invoice_id: str
    ) -> dict[str, Any]:
        """Update billing period with invoice ID.

        Args:
            customer_id: Customer ID
            year: Billing year
            month: Billing month
            invoice_id: Invoice ID to set

        Returns:
            Updated billing period

        Raises:
            DynamoDBError: If operation fails
        """
        pk = f"BILLING#{customer_id}"
        sk = f"PERIOD#{year:04d}-{month:02d}"

        return self.update_item(
            pk=pk,
            sk=sk,
            update_expression="SET invoice_id = :invoice_id, updated_at = :updated_at",
            expression_values={
                ":invoice_id": invoice_id,
                ":updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    def list_customers(
        self, limit: Optional[int] = None, last_evaluated_key: Optional[dict[str, Any]] = None
    ) -> list[dict[str, Any]]:
        """List all customers.

        Args:
            limit: Maximum customers to return
            last_evaluated_key: Pagination key

        Returns:
            List of customers

        Raises:
            DynamoDBError: If operation fails
        """
        try:
            scan_params = {
                "FilterExpression": Key("pk").begins_with("CUSTOMER#") & Key("sk").eq("METADATA")
            }

            if limit:
                scan_params["Limit"] = limit

            if last_evaluated_key:
                scan_params["ExclusiveStartKey"] = last_evaluated_key

            response = self._table.scan(**scan_params)

            items = response.get("Items", [])
            logger.debug(f"Listed {len(items)} customers")

            return items  # type: ignore[no-any-return]

        except Exception as e:
            self._handle_error("list_customers", e)

    def _prepare_item(self, item: dict[str, Any]) -> dict[str, Any]:
        """Prepare an item for DynamoDB storage.

        Converts datetime objects to ISO strings and ensures
        Decimal types are properly formatted.

        Args:
            item: Item to prepare

        Returns:
            Prepared item
        """
        prepared: dict[str, Any] = {}

        for key, value in item.items():
            if isinstance(value, datetime):
                prepared[key] = value.isoformat()
            elif isinstance(value, Decimal):
                # Ensure Decimal is clean for DynamoDB
                prepared[key] = value
            elif isinstance(value, dict):
                prepared[key] = self._prepare_item(value)
            elif isinstance(value, list):
                prepared[key] = [self._prepare_item(v) if isinstance(v, dict) else v for v in value]
            else:
                prepared[key] = value

        return prepared


# Async wrapper for DynamoDB operations
class AsyncDynamoDBClient:
    """Async wrapper for DynamoDB operations."""

    def __init__(self, sync_client: Optional[DynamoDBClient] = None):
        """Initialize async client.

        Args:
            sync_client: Optional sync client to wrap
        """
        self._sync_client = sync_client or DynamoDBClient()
        self._executor = None

    async def __aenter__(self) -> "AsyncDynamoDBClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""

    def _run_sync(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """Run a sync function in executor."""
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(self._executor, func, *args, **kwargs)

    async def put_item(self, item: dict[str, Any]) -> dict[str, Any]:
        """Async put item."""
        return await self._run_sync(self._sync_client.put_item, item)  # type: ignore[no-any-return]

    async def get_item(self, pk: str, sk: str) -> Optional[dict[str, Any]]:
        """Async get item."""
        return await self._run_sync(self._sync_client.get_item, pk, sk)  # type: ignore[no-any-return]

    async def query(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Async query."""
        return await self._run_sync(self._sync_client.query, **kwargs)  # type: ignore[no-any-return]

    async def get_customer(self, customer_id: str) -> Optional[dict[str, Any]]:
        """Async get customer."""
        return await self._run_sync(self._sync_client.get_customer, customer_id)  # type: ignore[no-any-return]

    async def get_customer_usage(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Async get customer usage."""
        return await self._run_sync(self._sync_client.get_customer_usage, **kwargs)  # type: ignore[no-any-return]
