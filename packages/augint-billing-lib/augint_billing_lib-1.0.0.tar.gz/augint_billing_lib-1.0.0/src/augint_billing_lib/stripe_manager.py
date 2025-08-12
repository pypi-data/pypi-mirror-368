"""Stripe integration manager for payment processing.

This module handles all Stripe API operations including customer management,
invoice generation, payment processing, and subscription handling. It provides
a high-level interface to Stripe's API with proper error handling and logging.

The StripeManager class wraps Stripe SDK operations and provides:
- Customer creation and management
- Invoice generation and processing
- Payment intent handling
- Subscription management
- Webhook signature verification

Example:
    >>> from augint_billing_lib import StripeManager
    >>>
    >>> # Initialize with API key
    >>> stripe_mgr = StripeManager(api_key="sk_test_...")
    >>>
    >>> # Create a customer
    >>> customer_id = stripe_mgr.create_customer(
    ...     email="customer@example.com",
    ...     name="John Doe",
    ...     customer_id="CUST123"
    ... )
    >>>
    >>> # Create an invoice
    >>> invoice = stripe_mgr.create_invoice(
    ...     stripe_customer_id=customer_id,
    ...     amount=99.99,
    ...     description="Monthly subscription"
    ... )
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional, Union

import stripe
from stripe.error import StripeError as StripeAPIError  # type: ignore[attr-defined]

from .config import get_settings
from .exceptions import StripeError

logger = logging.getLogger(__name__)


class StripeManager:
    """Manager class for Stripe payment operations.

    This class provides a unified interface to Stripe's API for billing operations,
    handling customer management, invoicing, payments, and subscriptions. All methods
    include proper error handling and logging.

    Attributes:
        api_key: Stripe API secret key
        api_version: Stripe API version being used

    Example:
        >>> # Initialize with environment variable
        >>> manager = StripeManager()
        >>>
        >>> # Or with explicit API key
        >>> manager = StripeManager(api_key="sk_test_...")
        >>>
        >>> # Create and charge a customer
        >>> customer_id = manager.create_customer(
        ...     email="user@example.com",
        ...     name="Jane Smith",
        ...     customer_id="CUST456"
        ... )
        >>> invoice = manager.create_invoice(
        ...     stripe_customer_id=customer_id,
        ...     amount=149.99,
        ...     description="API usage charges"
        ... )
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Stripe manager.

        Args:
            api_key: Stripe API key (uses env var if not provided)
        """
        settings = get_settings()
        self.api_key = api_key or settings.stripe_secret_key

        if not self.api_key:
            logger.warning("Stripe API key not configured")
        else:
            stripe.api_key = self.api_key
            stripe.api_version = settings.stripe_api_version
            logger.info(f"Initialized Stripe with API version {settings.stripe_api_version}")

    def create_customer(
        self, email: str, name: str, customer_id: str, metadata: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        """Create a new Stripe customer.

        Creates a customer in Stripe with the provided details and links it
        to the internal customer ID through metadata.

        Args:
            email: Customer email address
            name: Customer full name
            customer_id: Internal customer ID for reference
            metadata: Additional metadata to attach to the customer

        Returns:
            Dictionary containing the created customer data including:
            - id: Stripe customer ID
            - email: Customer email
            - name: Customer name
            - created: Creation timestamp

        Raises:
            StripeError: If customer creation fails

        Example:
            >>> customer = manager.create_customer(
            ...     email="john@example.com",
            ...     name="John Doe",
            ...     customer_id="CUST123",
            ...     metadata={"plan": "premium"}
            ... )
            >>> print(customer['id'])  # cus_AbCdEfGhIjKlMn
        """
        try:
            customer_metadata = {
                "internal_customer_id": customer_id,
                "created_via": "billing_service",
            }
            if metadata:
                customer_metadata.update(metadata)

            stripe_customer = stripe.Customer.create(
                email=email, name=name, metadata=customer_metadata
            )

            logger.info(f"Created Stripe customer {stripe_customer.id} for {customer_id}")
            return {
                "id": stripe_customer.id,
                "email": stripe_customer.email,
                "name": stripe_customer.name,
                "created": datetime.fromtimestamp(stripe_customer.created, tz=timezone.utc),
            }

        except StripeAPIError as e:
            logger.exception("Failed to create Stripe customer: ")
            raise StripeError(
                f"Failed to create customer for {email}",
                stripe_error_code=e.code if hasattr(e, "code") else None,
                original_error=e,
            ) from e

    def get_customer(self, stripe_customer_id: str) -> Optional[dict[str, Any]]:
        """Get Stripe customer details.

        Args:
            stripe_customer_id: Stripe customer ID

        Returns:
            Customer data or None if not found

        Raises:
            StripeError: If operation fails
        """
        try:
            customer = stripe.Customer.retrieve(stripe_customer_id)

            if customer.deleted:
                logger.warning(f"Stripe customer {stripe_customer_id} is deleted")
                return None

            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "currency": customer.currency,
                "balance": customer.balance,
                "delinquent": customer.delinquent,
                "created": datetime.fromtimestamp(customer.created, tz=timezone.utc),
                "metadata": customer.metadata,
            }

        except StripeAPIError as e:
            if e.http_status == 404:
                return None

            logger.exception("Failed to retrieve Stripe customer: ")
            raise StripeError(
                f"Failed to retrieve customer {stripe_customer_id}",
                stripe_error_code=e.code if hasattr(e, "code") else None,
                original_error=e,
            )

    def update_customer(
        self,
        stripe_customer_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> bool:
        """Update Stripe customer details.

        Args:
            stripe_customer_id: Stripe customer ID
            email: New email (optional)
            name: New name (optional)
            metadata: Updated metadata (optional)

        Returns:
            True if successful

        Raises:
            StripeError: If update fails
        """
        try:
            update_params = {}
            if email:
                update_params["email"] = email
            if name:
                update_params["name"] = name
            if metadata:
                update_params["metadata"] = metadata  # type: ignore[assignment]

            stripe.Customer.modify(stripe_customer_id, **update_params)  # type: ignore[arg-type]
            logger.info(f"Updated Stripe customer {stripe_customer_id}")
            return True

        except StripeAPIError as e:
            logger.exception("Failed to update Stripe customer: ")
            raise StripeError(
                f"Failed to update customer {stripe_customer_id}",
                stripe_error_code=e.code if hasattr(e, "code") else None,
                original_error=e,
            ) from e

    def create_invoice(
        self,
        customer_id: str,
        amount: Union[float, Decimal],
        description: str,
        currency: str = "USD",
        metadata: Optional[dict[str, Any]] = None,
        auto_advance: bool = True,
        days_until_due: int = 30,
    ) -> dict[str, Any]:
        """Create a Stripe invoice for billing.

        Creates an invoice in Stripe with line items and optionally finalizes it
        for automatic collection. The invoice can be sent to the customer via email.

        Args:
            customer_id: Internal customer ID (will look up Stripe customer)
            amount: Invoice amount in base currency units (e.g., dollars)
            description: Description for the invoice line item
            currency: Three-letter currency code (e.g., "USD", "EUR")
            metadata: Additional metadata to attach to the invoice
            auto_advance: If True, finalizes the invoice immediately
            days_until_due: Number of days until payment is due

        Returns:
            Dictionary containing invoice details:
            - id: Stripe invoice ID
            - customer: Stripe customer ID
            - amount_due: Total amount due
            - currency: Currency code
            - status: Invoice status (draft, open, paid, etc.)
            - created: Creation timestamp
            - hosted_invoice_url: URL to hosted invoice page (if finalized)
            - metadata: Attached metadata

        Raises:
            CustomerNotFoundError: If customer doesn't exist
            StripeError: If invoice creation fails

        Example:
            >>> invoice = manager.create_invoice(
            ...     customer_id="CUST123",
            ...     amount=299.99,
            ...     description="Monthly API usage",
            ...     metadata={"period": "2024-01"}
            ... )
            >>> print(invoice['hosted_invoice_url'])
        """
        try:
            # Get Stripe customer ID from internal customer ID
            # This would typically look up the customer in the database
            # For now, we'll assume customer_id is the Stripe customer ID
            # In production, this would query DynamoDB for the customer's stripe_customer_id
            stripe_customer_id = customer_id  # TODO: Look up from database

            # Convert amount to cents (Stripe uses smallest currency unit)
            if isinstance(amount, Decimal):
                amount_cents = int(amount * 100)
            else:
                amount_cents = int(float(amount) * 100)

            # Create invoice
            invoice_params = {
                "customer": stripe_customer_id,
                "currency": currency.lower(),
                "auto_advance": auto_advance,
                "metadata": metadata or {},
                "collection_method": "charge_automatically",
            }

            # Only add days_until_due if using send_invoice collection method
            # For charge_automatically, payment is attempted immediately

            invoice = stripe.Invoice.create(**invoice_params)  # type: ignore[arg-type]

            # Add line item
            stripe.InvoiceItem.create(
                customer=stripe_customer_id,
                invoice=invoice.id,  # type: ignore[arg-type]
                amount=amount_cents,
                currency=currency.lower(),
                description=description,
            )

            # Finalize if auto_advance
            if auto_advance:
                invoice = stripe.Invoice.finalize_invoice(invoice.id)  # type: ignore[arg-type]
                logger.info(f"Created and finalized Stripe invoice {invoice.id}")
            else:
                logger.info(f"Created draft Stripe invoice {invoice.id}")

            # Return invoice data
            return {
                "id": invoice.id,
                "customer": invoice.customer,
                "amount_due": invoice.amount_due,
                "currency": invoice.currency.upper(),
                "status": invoice.status,
                "created": datetime.fromtimestamp(invoice.created, tz=timezone.utc).isoformat(),
                "hosted_invoice_url": invoice.hosted_invoice_url if auto_advance else None,
                "metadata": invoice.metadata,
            }

        except StripeAPIError as e:
            logger.exception("Failed to create Stripe invoice: ")
            raise StripeError(
                f"Failed to create invoice for customer {stripe_customer_id}",
                stripe_error_code=e.code if hasattr(e, "code") else None,
                original_error=e,
            ) from e

    def get_invoice(self, stripe_invoice_id: str) -> Optional[dict[str, Any]]:
        """Get Stripe invoice details.

        Args:
            stripe_invoice_id: Stripe invoice ID

        Returns:
            Invoice data or None if not found

        Raises:
            StripeError: If operation fails
        """
        try:
            invoice = stripe.Invoice.retrieve(stripe_invoice_id)

            return {
                "id": invoice.id,
                "customer": invoice.customer,
                "amount_due": Decimal(str(invoice.amount_due / 100)),
                "amount_paid": Decimal(str(invoice.amount_paid / 100)),
                "currency": invoice.currency.upper(),
                "status": invoice.status,
                "created": datetime.fromtimestamp(invoice.created, tz=timezone.utc),
                "due_date": datetime.fromtimestamp(invoice.due_date, tz=timezone.utc)
                if invoice.due_date
                else None,
                "paid": invoice.paid,
                "payment_intent": invoice.payment_intent,
                "number": invoice.number,
                "metadata": invoice.metadata,
            }

        except StripeAPIError as e:
            if e.http_status == 404:
                return None

            logger.exception("Failed to retrieve Stripe invoice: ")
            raise StripeError(
                f"Failed to retrieve invoice {stripe_invoice_id}",
                stripe_error_code=e.code if hasattr(e, "code") else None,
                original_error=e,
            )

    def send_invoice(self, stripe_invoice_id: str) -> bool:
        """Send invoice to customer via email.

        Args:
            stripe_invoice_id: Stripe invoice ID

        Returns:
            True if successful

        Raises:
            StripeError: If sending fails
        """
        try:
            stripe.Invoice.send_invoice(stripe_invoice_id)
            logger.info(f"Sent Stripe invoice {stripe_invoice_id}")
            return True

        except StripeAPIError as e:
            logger.exception("Failed to send Stripe invoice: ")
            raise StripeError(
                f"Failed to send invoice {stripe_invoice_id}",
                stripe_error_code=e.code if hasattr(e, "code") else None,
                original_error=e,
            ) from e

    def void_invoice(self, stripe_invoice_id: str) -> bool:
        """Void a Stripe invoice.

        Args:
            stripe_invoice_id: Stripe invoice ID

        Returns:
            True if successful

        Raises:
            StripeError: If voiding fails
        """
        try:
            stripe.Invoice.void_invoice(stripe_invoice_id)
            logger.info(f"Voided Stripe invoice {stripe_invoice_id}")
            return True

        except StripeAPIError as e:
            logger.exception("Failed to void Stripe invoice: ")
            raise StripeError(
                f"Failed to void invoice {stripe_invoice_id}",
                stripe_error_code=e.code if hasattr(e, "code") else None,
                original_error=e,
            ) from e

    def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        stripe_customer_id: str,
        description: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> str:
        """Create a payment intent for immediate payment.

        Args:
            amount: Payment amount
            currency: Currency code
            stripe_customer_id: Stripe customer ID
            description: Payment description
            metadata: Additional metadata

        Returns:
            Payment intent ID

        Raises:
            StripeError: If creation fails
        """
        try:
            amount_cents = int(amount * 100)

            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                customer=stripe_customer_id,
                description=description,  # type: ignore[arg-type]
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True},
            )

            logger.info(f"Created payment intent {intent.id} for {amount} {currency}")
            return intent.id

        except StripeAPIError as e:
            logger.exception("Failed to create payment intent: ")
            raise StripeError(
                "Failed to create payment intent",
                stripe_error_code=e.code if hasattr(e, "code") else None,
                original_error=e,
            ) from e

    def get_payment_intent(self, payment_intent_id: str) -> Optional[dict[str, Any]]:
        """Get payment intent details.

        Args:
            payment_intent_id: Payment intent ID

        Returns:
            Payment intent data or None

        Raises:
            StripeError: If operation fails
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            return {
                "id": intent.id,
                "amount": Decimal(str(intent.amount / 100)),
                "currency": intent.currency.upper(),
                "status": intent.status,
                "customer": intent.customer,
                "created": datetime.fromtimestamp(intent.created, tz=timezone.utc),
                "metadata": intent.metadata,
            }

        except StripeAPIError as e:
            if e.http_status == 404:
                return None

            logger.exception("Failed to retrieve payment intent: ")
            raise StripeError(
                f"Failed to retrieve payment intent {payment_intent_id}",
                stripe_error_code=e.code if hasattr(e, "code") else None,
                original_error=e,
            )

    def create_subscription(
        self,
        stripe_customer_id: str,
        price_id: str,
        metadata: Optional[dict[str, str]] = None,
        trial_days: Optional[int] = None,
    ) -> str:
        """Create a subscription for recurring billing.

        Args:
            stripe_customer_id: Stripe customer ID
            price_id: Stripe price ID for subscription
            metadata: Additional metadata
            trial_days: Optional trial period in days

        Returns:
            Subscription ID

        Raises:
            StripeError: If creation fails
        """
        try:
            sub_params = {
                "customer": stripe_customer_id,
                "items": [{"price": price_id}],
                "metadata": metadata or {},
            }

            if trial_days:
                sub_params["trial_period_days"] = trial_days  # type: ignore[assignment]

            subscription = stripe.Subscription.create(**sub_params)  # type: ignore[arg-type]

            logger.info(f"Created subscription {subscription.id} for customer {stripe_customer_id}")
            return subscription.id

        except StripeAPIError as e:
            logger.exception("Failed to create subscription: ")
            raise StripeError(
                "Failed to create subscription",
                stripe_error_code=e.code if hasattr(e, "code") else None,
                original_error=e,
            ) from e

    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> bool:
        """Cancel a subscription.

        Args:
            subscription_id: Stripe subscription ID
            at_period_end: Whether to cancel at period end or immediately

        Returns:
            True if successful

        Raises:
            StripeError: If cancellation fails
        """
        try:
            if at_period_end:
                stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
            else:
                stripe.Subscription.delete(subscription_id)  # type: ignore[arg-type]

            logger.info(f"Cancelled subscription {subscription_id}")
            return True

        except StripeAPIError as e:
            logger.exception("Failed to cancel subscription: ")
            raise StripeError(
                f"Failed to cancel subscription {subscription_id}",
                stripe_error_code=e.code if hasattr(e, "code") else None,
                original_error=e,
            ) from e

    def list_invoices(
        self, stripe_customer_id: str, limit: int = 10, starting_after: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """List invoices for a customer.

        Args:
            stripe_customer_id: Stripe customer ID
            limit: Maximum number of invoices to return
            starting_after: Pagination cursor

        Returns:
            List of invoice data

        Raises:
            StripeError: If operation fails
        """
        try:
            list_params = {"customer": stripe_customer_id, "limit": limit}

            if starting_after:
                list_params["starting_after"] = starting_after

            invoices = stripe.Invoice.list(**list_params)  # type: ignore[arg-type]

            return [
                {
                    "id": inv.id,
                    "amount_due": Decimal(str(inv.amount_due / 100)),
                    "currency": inv.currency.upper(),
                    "status": inv.status,
                    "created": datetime.fromtimestamp(inv.created, tz=timezone.utc),
                    "paid": inv.paid,
                }
                for inv in invoices.data
            ]

        except StripeAPIError as e:
            logger.exception("Failed to list invoices: ")
            raise StripeError(
                f"Failed to list invoices for customer {stripe_customer_id}",
                stripe_error_code=e.code if hasattr(e, "code") else None,
                original_error=e,
            ) from e

    def get_payment_method(self, stripe_customer_id: str) -> Optional[dict[str, Any]]:
        """Get the default payment method for a customer.

        Retrieves the default payment method configured for a Stripe customer,
        including card details if available.

        Args:
            stripe_customer_id: Stripe customer ID

        Returns:
            Dictionary containing payment method details:
            - id: Payment method ID
            - type: Payment method type (card, bank_account, etc.)
            - card: Card details if type is card
            - created: Creation timestamp
            Returns None if no payment method is configured

        Raises:
            StripeError: If operation fails

        Example:
            >>> payment_method = manager.get_payment_method("cus_123")
            >>> if payment_method:
            ...     print(f"Card ending in {payment_method['card']['last4']}")
        """
        try:
            # Get customer to find default payment method
            customer = stripe.Customer.retrieve(stripe_customer_id)

            if (
                not customer.invoice_settings
                or not customer.invoice_settings.default_payment_method
            ):
                return None

            # Retrieve payment method details
            payment_method = stripe.PaymentMethod.retrieve(
                str(customer.invoice_settings.default_payment_method)
            )

            result = {
                "id": payment_method.id,
                "type": payment_method.type,
                "created": datetime.fromtimestamp(payment_method.created, tz=timezone.utc),
            }

            # Add card details if available
            if payment_method.type == "card" and payment_method.card:
                result["card"] = {
                    "brand": payment_method.card.brand,
                    "last4": payment_method.card.last4,
                    "exp_month": payment_method.card.exp_month,
                    "exp_year": payment_method.card.exp_year,
                }

            return result

        except StripeAPIError as e:
            if e.http_status == 404:
                return None

            logger.exception("Failed to get payment method: ")
            raise StripeError(
                f"Failed to get payment method for customer {stripe_customer_id}",
                stripe_error_code=e.code if hasattr(e, "code") else None,
                original_error=e,
            )
