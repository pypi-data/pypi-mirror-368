"""Webhook processor for Stripe payment events.

This module handles processing Stripe webhooks for payment events,
updating billing status, and triggering appropriate actions.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Optional

import stripe
from stripe.error import SignatureVerificationError  # type: ignore[attr-defined]

from .config import get_settings
from .db import DynamoDBClient
from .exceptions import WebhookValidationError
from .models import Invoice
from .types import (
    InvoiceEventResultDict,
    PaymentEventResultDict,
    PaymentIntentEventResultDict,
    StripeWebhookEventDict,
    SubscriptionEventResultDict,
    WebhookEventResultDict,
)

logger = logging.getLogger(__name__)


class WebhookProcessor:
    """Processes Stripe webhooks and updates billing status.

    This class handles webhook validation, event processing,
    and updating billing records based on payment events.
    """

    def __init__(
        self,
        stripe_manager: Optional[Any] = None,
        db_client: Optional[DynamoDBClient] = None,
        webhook_secret: Optional[str] = None,
    ):
        """Initialize webhook processor.

        Args:
            stripe_manager: StripeManager instance for Stripe operations
            db_client: DynamoDBClient instance for database operations
            webhook_secret: Stripe webhook secret (uses env var if not provided)
        """
        settings = get_settings()
        self.stripe_manager = stripe_manager
        self.db_client = db_client or DynamoDBClient(table_name=settings.dynamodb_table)
        self.webhook_secret = webhook_secret or settings.stripe_webhook_secret

        # Event handlers mapping
        self.event_handlers: dict[str, Callable[..., Any]] = {
            "invoice.payment_succeeded": self._handle_payment_succeeded,
            "invoice.payment_failed": self._handle_payment_failed,
            "invoice.created": self._handle_invoice_created,
            "invoice.finalized": self._handle_invoice_finalized,
            "invoice.voided": self._handle_invoice_voided,
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "payment_intent.succeeded": self._handle_payment_intent_succeeded,
            "payment_intent.payment_failed": self._handle_payment_intent_failed,
        }

        logger.info(f"Initialized WebhookProcessor with table: {self.db_client.table_name}")

    def process_webhook(
        self, payload: bytes, signature: str, validate_signature: bool = True
    ) -> WebhookEventResultDict:
        """Process a Stripe webhook event.

        Args:
            payload: Raw webhook payload bytes
            signature: Stripe signature header
            validate_signature: Whether to validate webhook signature

        Returns:
            Processing result

        Raises:
            WebhookValidationError: If validation fails
        """
        # Validate signature if required
        if validate_signature:
            event = self._validate_webhook(payload, signature)
        else:
            try:
                event = json.loads(payload)
            except json.JSONDecodeError as e:
                raise WebhookValidationError(f"Invalid JSON payload: {e!s}") from e

        event_type = event.get("type")
        event_id = event.get("id")

        logger.info(f"Processing webhook event: {event_type} (ID: {event_id})")

        # Check if we have a handler for this event type
        handler = self.event_handlers.get(event_type)  # type: ignore[arg-type]

        if handler:
            try:
                result = handler(event)
                logger.info(f"Successfully processed {event_type} event")
                return {
                    "status": "success",
                    "event_id": event_id,
                    "event_type": event_type,
                    "result": result,
                }

            except Exception as e:
                logger.exception("Error processing {event_type} event: ")
                return {
                    "status": "error",
                    "event_id": event_id,
                    "event_type": event_type,
                    "error": str(e),
                }
        else:
            logger.debug(f"No handler for event type: {event_type}")
            return {
                "status": "ignored",
                "event_id": event_id,
                "event_type": event_type,
                "message": "No handler configured for this event type",
            }

    def _validate_webhook(self, payload: bytes, signature: str) -> StripeWebhookEventDict:
        """Validate webhook signature and parse event.

        Args:
            payload: Raw webhook payload
            signature: Stripe signature

        Returns:
            Parsed event data

        Raises:
            WebhookValidationError: If validation fails
        """
        if not self.webhook_secret:
            raise WebhookValidationError("Webhook secret not configured", webhook_type="stripe")
        try:
            event: StripeWebhookEventDict = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )  # type: ignore[no-untyped-call]
            return event

        except ValueError as e:
            raise WebhookValidationError(f"Invalid payload: {e!s}", webhook_type="stripe") from e
        except SignatureVerificationError as e:
            raise WebhookValidationError(f"Invalid signature: {e!s}", webhook_type="stripe") from e

    def _handle_payment_succeeded(self, event: StripeWebhookEventDict) -> PaymentEventResultDict:
        """Handle successful payment event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        invoice = event["data"]["object"]
        invoice_id = invoice["id"]
        customer_id = self._get_customer_id_from_metadata(invoice)
        amount_paid = invoice["amount_paid"] / 100  # Convert from cents

        # Update invoice record
        self._update_invoice_status(
            stripe_invoice_id=invoice_id, status="paid", amount_paid=amount_paid
        )

        # Update billing period if linked
        if customer_id and "billing_period" in invoice.get("metadata", {}):
            period = invoice["metadata"]["billing_period"]
            self._update_billing_period_status(
                customer_id=customer_id, period=period, status="paid", invoice_id=invoice_id
            )

        # Update customer billing status
        if customer_id:
            self._update_customer_billing_status(customer_id, "active")

        logger.info(f"Payment succeeded for invoice {invoice_id}, amount: {amount_paid}")

        return {
            "invoice_id": invoice_id,
            "customer_id": customer_id,
            "amount_paid": amount_paid,
            "status": "paid",
        }

    def _handle_payment_failed(self, event: StripeWebhookEventDict) -> PaymentEventResultDict:
        """Handle failed payment event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        invoice = event["data"]["object"]
        invoice_id = invoice["id"]
        customer_id = self._get_customer_id_from_metadata(invoice)
        attempt_count = invoice.get("attempt_count", 1)

        # Update invoice record
        self._update_invoice_status(
            stripe_invoice_id=invoice_id,
            status="open",
            metadata={"payment_failed": True, "attempt_count": attempt_count},
        )

        # Update billing period if linked
        if customer_id and "billing_period" in invoice.get("metadata", {}):
            period = invoice["metadata"]["billing_period"]
            self._update_billing_period_status(
                customer_id=customer_id, period=period, status="failed"
            )

        # Update customer billing status
        if customer_id:
            self._update_customer_billing_status(customer_id, "past_due")

        logger.warning(f"Payment failed for invoice {invoice_id}, attempt: {attempt_count}")

        return {
            "invoice_id": invoice_id,
            "customer_id": customer_id,
            "attempt_count": attempt_count,
            "status": "failed",
        }

    def _handle_invoice_created(self, event: StripeWebhookEventDict) -> InvoiceEventResultDict:
        """Handle invoice created event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        invoice = event["data"]["object"]
        invoice_id = invoice["id"]
        customer_id = self._get_customer_id_from_metadata(invoice)

        # Create invoice record in database
        clean_invoice_id = invoice_id.replace("in_", "")  # Remove Stripe prefix
        invoice_record = Invoice(
            pk=f"INVOICE#{clean_invoice_id}",
            invoice_id=clean_invoice_id,
            customer_id=customer_id or "unknown",
            stripe_invoice_id=invoice_id,
            amount=invoice["amount_due"] / 100,
            currency=invoice["currency"].upper(),
            status="draft",
            due_date=datetime.fromtimestamp(invoice.get("due_date", 0), tz=timezone.utc),
            line_items=self._extract_line_items(invoice),
        )

        try:
            self.db_client.put_item(invoice_record.model_dump())
            logger.info(f"Created invoice record for {invoice_id}")
        except Exception:
            logger.exception("Failed to create invoice record: ")

        return {"invoice_id": invoice_id, "customer_id": customer_id, "status": "created"}

    def _handle_invoice_finalized(self, event: StripeWebhookEventDict) -> InvoiceEventResultDict:
        """Handle invoice finalized event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        invoice = event["data"]["object"]
        invoice_id = invoice["id"]

        # Update invoice status to open
        self._update_invoice_status(stripe_invoice_id=invoice_id, status="open")

        logger.info(f"Invoice {invoice_id} finalized")

        return {"invoice_id": invoice_id, "status": "finalized"}

    def _handle_invoice_voided(self, event: StripeWebhookEventDict) -> InvoiceEventResultDict:
        """Handle invoice voided event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        invoice = event["data"]["object"]
        invoice_id = invoice["id"]

        # Update invoice status to void
        self._update_invoice_status(stripe_invoice_id=invoice_id, status="void")

        logger.info(f"Invoice {invoice_id} voided")

        return {"invoice_id": invoice_id, "status": "voided"}

    def _handle_subscription_created(
        self, event: StripeWebhookEventDict
    ) -> SubscriptionEventResultDict:
        """Handle subscription created event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        subscription = event["data"]["object"]
        subscription_id = subscription["id"]
        customer_id = self._get_customer_id_from_metadata(subscription)

        logger.info(f"Subscription {subscription_id} created for customer {customer_id}")

        return {"subscription_id": subscription_id, "customer_id": customer_id, "status": "created"}

    def _handle_subscription_updated(
        self, event: StripeWebhookEventDict
    ) -> SubscriptionEventResultDict:
        """Handle subscription updated event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        subscription = event["data"]["object"]
        subscription_id = subscription["id"]
        status = subscription["status"]
        customer_id = self._get_customer_id_from_metadata(subscription)

        logger.info(f"Subscription {subscription_id} updated to status: {status}")

        return {"subscription_id": subscription_id, "customer_id": customer_id, "status": status}

    def _handle_subscription_deleted(
        self, event: StripeWebhookEventDict
    ) -> SubscriptionEventResultDict:
        """Handle subscription deleted event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        subscription = event["data"]["object"]
        subscription_id = subscription["id"]
        customer_id = self._get_customer_id_from_metadata(subscription)

        # Update customer billing status
        if customer_id:
            self._update_customer_billing_status(customer_id, "cancelled")

        logger.info(f"Subscription {subscription_id} deleted")

        return {"subscription_id": subscription_id, "customer_id": customer_id, "status": "deleted"}

    def _handle_payment_intent_succeeded(
        self, event: StripeWebhookEventDict
    ) -> PaymentIntentEventResultDict:
        """Handle payment intent succeeded event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        payment_intent = event["data"]["object"]
        intent_id = payment_intent["id"]
        amount = payment_intent["amount"] / 100

        logger.info(f"Payment intent {intent_id} succeeded, amount: {amount}")

        return {"payment_intent_id": intent_id, "amount": amount, "status": "succeeded"}

    def _handle_payment_intent_failed(
        self, event: StripeWebhookEventDict
    ) -> PaymentIntentEventResultDict:
        """Handle payment intent failed event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        payment_intent = event["data"]["object"]
        intent_id = payment_intent["id"]
        error_message = payment_intent.get("last_payment_error", {}).get("message")

        logger.warning(f"Payment intent {intent_id} failed: {error_message}")

        return {
            "payment_intent_id": intent_id,
            "amount": 0.0,
            "status": "failed",
            "error": error_message,
        }

    def _get_customer_id_from_metadata(
        self, stripe_object: dict[str, Any]
    ) -> Optional[str]:  # stripe_object is from Stripe API
        """Extract internal customer ID from Stripe metadata.

        Args:
            stripe_object: Stripe object with metadata

        Returns:
            Customer ID or None
        """
        metadata = stripe_object.get("metadata", {})
        return metadata.get("internal_customer_id") or metadata.get("customer_id")  # type: ignore[no-any-return]

    def _extract_line_items(self, invoice: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract line items from Stripe invoice.

        Args:
            invoice: Stripe invoice object

        Returns:
            List of line items
        """
        line_items = []

        if "lines" in invoice and "data" in invoice["lines"]:
            for item in invoice["lines"]["data"]:
                line_items.append(
                    {
                        "description": item.get("description", ""),
                        "amount": item.get("amount", 0) / 100,
                        "quantity": item.get("quantity", 1),
                        "currency": item.get("currency", "usd").upper(),
                    }
                )

        return line_items

    def _update_invoice_status(
        self,
        stripe_invoice_id: str,
        status: str,
        amount_paid: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Update invoice status in database.

        Args:
            stripe_invoice_id: Stripe invoice ID
            status: New status
            amount_paid: Amount paid (optional)
            metadata: Additional metadata (optional)
        """
        # Find invoice by Stripe ID
        invoice_id = stripe_invoice_id.replace("in_", "")
        invoice = self.db_client.get_invoice(invoice_id)

        if invoice:
            update_expr = "SET #status = :status, updated_at = :updated_at"
            expr_values = {":status": status, ":updated_at": datetime.now(timezone.utc).isoformat()}

            if amount_paid is not None:
                update_expr += ", amount_paid = :amount_paid"
                expr_values[":amount_paid"] = amount_paid  # type: ignore[assignment]

            if metadata:
                update_expr += ", metadata = :metadata"
                expr_values[":metadata"] = metadata  # type: ignore[assignment]

            try:
                self.db_client.update_item(
                    pk=f"INVOICE#{invoice_id}",
                    sk="METADATA",
                    update_expression=update_expr.replace("#status", "status"),
                    expression_values=expr_values,
                )
            except Exception:
                logger.exception("Failed to update invoice status: ")

    def _update_billing_period_status(
        self, customer_id: str, period: str, status: str, invoice_id: Optional[str] = None
    ) -> None:
        """Update billing period status in database.

        Args:
            customer_id: Customer ID
            period: Billing period (YYYY-MM)
            status: New status
            invoice_id: Associated invoice ID (optional)
        """
        year, month = map(int, period.split("-"))

        update_expr = "SET payment_status = :status"
        expr_values = {":status": status}

        if invoice_id:
            update_expr += ", invoice_id = :invoice_id"
            expr_values[":invoice_id"] = invoice_id

        try:
            self.db_client.update_item(
                pk=f"BILLING#{customer_id}",
                sk=f"PERIOD#{year:04d}-{month:02d}",
                update_expression=update_expr,
                expression_values=expr_values,
            )
        except Exception:
            logger.exception("Failed to update billing period status: ")

    def _update_customer_billing_status(self, customer_id: str, status: str) -> None:
        """Update customer billing status.

        Args:
            customer_id: Customer ID
            status: New billing status
        """
        try:
            self.db_client.update_item(
                pk=f"CUSTOMER#{customer_id}",
                sk="METADATA",
                update_expression="SET billing_status = :status, updated_at = :updated_at",
                expression_values={
                    ":status": status,
                    ":updated_at": datetime.now(timezone.utc).isoformat(),
                },
            )
        except Exception:
            logger.exception("Failed to update customer billing status: ")
