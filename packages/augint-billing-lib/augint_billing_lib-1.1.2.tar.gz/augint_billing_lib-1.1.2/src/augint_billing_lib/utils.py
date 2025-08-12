"""Utility functions for the billing service.

This module provides utility functions for common billing operations
including charge calculations, usage validation, and currency formatting.
"""

import hashlib
import hmac
import re
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from .exceptions import PricingConfigurationError, UsageValidationError
from .models import PricingTier, UsageRecord
from .types import UsageBreakdownDict


def calculate_charges(
    usage_count: int, pricing_tiers: list[PricingTier], currency: str = "USD"
) -> tuple[Decimal, list[UsageBreakdownDict]]:
    """Calculate charges based on tiered pricing.

    Applies tiered pricing rules to calculate total charges for usage.
    Returns both the total charge and a breakdown by tier.

    Args:
        usage_count: Total usage to calculate charges for
        pricing_tiers: List of pricing tiers to apply
        currency: Currency code for charges

    Returns:
        Tuple of (total_charges, breakdown_list)

    Raises:
        PricingConfigurationError: If pricing tiers are invalid

    Example:
        >>> tiers = [
        ...     PricingTier(tier_number=1, usage_limit=1000, price_per_unit=Decimal('0')),
        ...     PricingTier(tier_number=2, usage_limit=10000, price_per_unit=Decimal('0.01'))
        ... ]
        >>> charges, breakdown = calculate_charges(5000, tiers)
        >>> print(f"Total: ${charges}, Items: {len(breakdown)}")
    """
    if not pricing_tiers:
        raise PricingConfigurationError("unknown", "No pricing tiers provided")

    # Sort tiers by tier number to ensure correct order
    sorted_tiers = sorted(pricing_tiers, key=lambda t: t.tier_number)

    total_charges = Decimal("0")
    breakdown = []
    remaining_usage = usage_count
    previous_limit = 0

    for tier in sorted_tiers:
        if remaining_usage <= 0:
            break

        # Calculate usage in this tier
        if tier.usage_limit is None:
            # Unlimited tier - all remaining usage
            tier_usage = remaining_usage
        else:
            # Calculate how much fits in this tier
            tier_capacity = tier.usage_limit - previous_limit
            tier_usage = min(remaining_usage, tier_capacity)

        # Calculate charges for this tier
        tier_charges = Decimal(str(tier_usage)) * tier.price_per_unit
        tier_charges = tier_charges.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        total_charges += tier_charges
        remaining_usage -= tier_usage

        # Add to breakdown
        if tier_usage > 0:
            breakdown_item: UsageBreakdownDict = {
                "tier": tier.tier_number,
                "usage": tier_usage,
                "rate": float(tier.price_per_unit),
                "charges": float(tier_charges),
                "currency": currency,
                "description": (
                    f"Tier {tier.tier_number}: {tier_usage} units @ ${tier.price_per_unit}/unit"
                ),
            }
            breakdown.append(breakdown_item)

        if tier.usage_limit is not None:
            previous_limit = tier.usage_limit

    # Round total to 2 decimal places
    total_charges = total_charges.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return total_charges, breakdown


def validate_usage(usage_record: UsageRecord) -> bool:
    """Validate a usage record for correctness.

    Performs validation checks on usage records including:
    - Customer ID format
    - API endpoint format
    - Usage count validity
    - Timestamp validity

    Args:
        usage_record: Usage record to validate

    Returns:
        True if valid

    Raises:
        UsageValidationError: If validation fails
    """
    # Validate customer ID format
    if not usage_record.customer_id:
        raise UsageValidationError("Customer ID is required", "customer_id")

    if not re.match(r"^[A-Za-z0-9_.-]+$", usage_record.customer_id):
        raise UsageValidationError(
            f"Invalid customer ID format: {usage_record.customer_id}", "customer_id"
        )

    # Validate API endpoint
    if not usage_record.api_endpoint:
        raise UsageValidationError("API endpoint is required", "api_endpoint")

    if not usage_record.api_endpoint.startswith("/"):
        raise UsageValidationError(
            f"API endpoint must start with '/': {usage_record.api_endpoint}", "api_endpoint"
        )

    # Validate usage count
    if usage_record.usage_count < 0:
        raise UsageValidationError(
            f"Usage count cannot be negative: {usage_record.usage_count}", "usage_count"
        )

    max_usage_count = 1000000
    if usage_record.usage_count > max_usage_count:
        raise UsageValidationError(
            f"Usage count exceeds maximum single record limit: {usage_record.usage_count}",
            "usage_count",
        )

    # Validate timestamp is not in the future
    now = datetime.now(timezone.utc)
    if usage_record.timestamp.replace(tzinfo=timezone.utc) > now + timedelta(minutes=5):
        raise UsageValidationError("Usage timestamp cannot be in the future", "timestamp")

    # Validate timestamp is not too old (e.g., more than 90 days)
    ninety_days_ago = now - timedelta(days=90)
    if usage_record.timestamp.replace(tzinfo=timezone.utc) < ninety_days_ago:
        raise UsageValidationError("Usage timestamp is too old (>90 days)", "timestamp")

    return True


def _format_eur_amount(amount: Decimal, include_symbol: bool) -> str:
    """Format amount in EUR convention with period as thousands separator.

    Args:
        amount: Amount to format (already quantized to 2 decimal places)
        include_symbol: Whether to include the € symbol

    Returns:
        Formatted EUR string
    """
    str_amount = f"{amount:.2f}"
    parts = str_amount.split(".")
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else "00"

    # Handle negative numbers
    is_negative = integer_part.startswith("-")
    if is_negative:
        integer_part = integer_part[1:]  # Remove the negative sign for processing

    # Add thousands separators correctly
    if len(integer_part) > 3:
        # Work from right to left, inserting dots every 3 digits
        result = []
        for i, digit in enumerate(reversed(integer_part)):
            if i > 0 and i % 3 == 0:
                result.append(".")
            result.append(digit)
        integer_part = "".join(reversed(result))

    # Re-add negative sign if needed
    if is_negative:
        integer_part = "-" + integer_part

    formatted = f"{integer_part},{decimal_part}"
    if include_symbol:
        formatted = f"€{formatted}"

    return formatted


def format_currency(amount: Decimal, currency: str = "USD", include_symbol: bool = True) -> str:
    """Format a decimal amount as currency string.

    Args:
        amount: Amount to format
        currency: Currency code (USD, EUR, GBP, etc.)
        include_symbol: Whether to include currency symbol

    Returns:
        Formatted currency string

    Example:
        >>> format_currency(Decimal('1234.56'), 'USD')
        '$1,234.56'
        >>> format_currency(Decimal('1234.56'), 'EUR', False)
        '1.234,56'
    """
    # Ensure amount is quantized to 2 decimal places
    amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Currency symbols mapping
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CNY": "¥",
        "INR": "₹",
        "CAD": "C$",
        "AUD": "A$",
    }

    # Format based on currency conventions
    if currency in ["USD", "GBP", "CAD", "AUD"]:
        # Use comma as thousands separator, period as decimal
        formatted = f"{amount:,.2f}"
        if include_symbol and currency in symbols:
            formatted = f"{symbols[currency]}{formatted}"

    elif currency == "EUR":
        # Use helper function for EUR formatting
        formatted = _format_eur_amount(amount, include_symbol)

    elif currency == "JPY":
        # Japanese Yen doesn't use decimal places
        amount_int = int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        formatted = f"{amount_int:,}"
        if include_symbol and currency in symbols:
            formatted = f"{symbols[currency]}{formatted}"

    else:
        # Default formatting
        formatted = f"{amount:,.2f}"
        if include_symbol:
            formatted = f"{formatted} {currency}"

    return formatted


def get_billing_period_bounds(date: Optional[datetime] = None) -> tuple[datetime, datetime]:
    """Get the start and end dates for a billing period.

    Billing periods are monthly, starting on the 1st of each month.

    Args:
        date: Date to get billing period for (defaults to current date)

    Returns:
        Tuple of (period_start, period_end) as UTC datetimes
    """
    date = datetime.now(timezone.utc) if date is None else date.replace(tzinfo=timezone.utc)

    # Start of the month
    period_start = datetime(date.year, date.month, 1, 0, 0, 0, tzinfo=timezone.utc)

    # End of the month (start of next month)
    december = 12
    if date.month == december:
        period_end = datetime(date.year + 1, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    else:
        period_end = datetime(date.year, date.month + 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    return period_start, period_end


def calculate_proration(
    amount: Decimal,
    start_date: datetime,
    end_date: datetime,
    billing_period_start: datetime,
    billing_period_end: datetime,
) -> Decimal:
    """Calculate prorated amount for partial billing periods.

    Args:
        amount: Full period amount
        start_date: Service start date
        end_date: Service end date
        billing_period_start: Billing period start
        billing_period_end: Billing period end

    Returns:
        Prorated amount
    """
    # Ensure all dates are timezone-aware
    start_date = start_date.replace(tzinfo=timezone.utc)
    end_date = end_date.replace(tzinfo=timezone.utc)
    billing_period_start = billing_period_start.replace(tzinfo=timezone.utc)
    billing_period_end = billing_period_end.replace(tzinfo=timezone.utc)

    # Calculate overlapping period
    effective_start = max(start_date, billing_period_start)
    effective_end = min(end_date, billing_period_end)

    # If no overlap, return 0
    if effective_start >= effective_end:
        return Decimal("0")

    # Calculate proration
    service_days = (effective_end - effective_start).days
    period_days = (billing_period_end - billing_period_start).days

    if period_days == 0:
        return Decimal("0")

    proration_factor = Decimal(str(service_days)) / Decimal(str(period_days))
    prorated_amount = amount * proration_factor

    return prorated_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature for security.

    Args:
        payload: Raw webhook payload bytes
        signature: Signature from webhook header
        secret: Webhook secret key

    Returns:
        True if signature is valid
    """
    expected_signature = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    return hmac.compare_digest(signature, expected_signature)


def generate_invoice_number(customer_id: str, period: str, sequence: int = 1) -> str:
    """Generate a unique invoice number.

    Args:
        customer_id: Customer ID
        period: Billing period (YYYY-MM format)
        sequence: Sequence number for multiple invoices in period

    Returns:
        Invoice number string
    """
    # Clean customer ID for invoice number
    clean_customer = re.sub(r"[^A-Z0-9]", "", customer_id.upper())[:10]

    return f"INV-{clean_customer}-{period}-{sequence:03d}"


def calculate_due_date(invoice_date: datetime, payment_terms_days: int = 30) -> datetime:
    """Calculate invoice due date based on payment terms.

    Args:
        invoice_date: Date invoice was created
        payment_terms_days: Number of days for payment terms

    Returns:
        Due date as datetime
    """
    return invoice_date + timedelta(days=payment_terms_days)
