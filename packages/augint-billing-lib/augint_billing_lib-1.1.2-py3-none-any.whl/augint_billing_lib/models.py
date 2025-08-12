"""Data models for the billing service.

This module defines Pydantic models for billing operations including
customers, usage records, billing periods, pricing tiers, and invoices.
All models use proper type hints and validation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Customer(BaseModel):
    """Customer data model for billing operations.

    Attributes:
        pk: DynamoDB partition key (CUSTOMER#{customer_id})
        sk: DynamoDB sort key (METADATA)
        customer_id: Unique customer identifier
        stripe_customer_id: Stripe customer ID if exists
        email: Customer email address
        name: Customer full name
        plan_type: Customer plan (free, paid, enterprise)
        created_at: When customer was created
        updated_at: Last update timestamp
        billing_status: Current billing status
    """

    model_config = ConfigDict(validate_assignment=True)

    pk: str = Field(..., description="Format: CUSTOMER#{customer_id}")
    sk: str = Field(default="METADATA", description="Sort key for customer metadata")
    customer_id: str = Field(..., min_length=1, max_length=100)
    stripe_customer_id: Optional[str] = Field(None, min_length=1, max_length=255)
    email: str = Field(..., min_length=3, max_length=255, description="Customer email")
    name: str = Field(..., min_length=1, max_length=255, description="Customer name")
    plan_type: str = Field(..., pattern="^(free|paid|enterprise)$")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    billing_status: str = Field(default="active", pattern="^(active|past_due|cancelled)$")

    @field_validator("pk")
    @classmethod
    def validate_pk(cls, v: str, _info: Any) -> str:
        """Validate partition key format."""
        if not v.startswith("CUSTOMER#"):
            raise ValueError("pk must start with 'CUSTOMER#'")
        return v

    @model_validator(mode="before")
    @classmethod
    def set_pk_sk(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Auto-set pk and sk if not provided."""
        if isinstance(values, dict):
            if "customer_id" in values and "pk" not in values:
                values["pk"] = f"CUSTOMER#{values['customer_id']}"
            if "sk" not in values:
                values["sk"] = "METADATA"
        return values


class UsageRecord(BaseModel):
    """Usage tracking model for API calls.

    Attributes:
        pk: Partition key (USAGE#{customer_id})
        sk: Sort key (USAGE#{date}#{timestamp})
        gsi1pk: GSI partition key for daily aggregations
        gsi1sk: GSI sort key (customer_id)
        customer_id: Customer making the API calls
        api_endpoint: Which API endpoint was called
        usage_count: Number of calls made
        timestamp: When the usage occurred
        created_at: When record was created
    """

    model_config = ConfigDict(validate_assignment=True)

    pk: str = Field(..., description="Format: USAGE#{customer_id}")
    sk: str = Field(..., description="Format: USAGE#{date}#{timestamp}")
    gsi1pk: str = Field(..., description="Format: USAGE#{date}")
    gsi1sk: str = Field(..., description="Customer ID for GSI")
    customer_id: str = Field(..., min_length=1, max_length=100)
    api_endpoint: str = Field(..., min_length=1, max_length=255)
    usage_count: int = Field(..., ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="before")
    @classmethod
    def set_keys(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Auto-set DynamoDB keys based on data."""
        if isinstance(values, dict):
            if "customer_id" in values and "pk" not in values:
                values["pk"] = f"USAGE#{values['customer_id']}"

            if "timestamp" in values:
                ts = values["timestamp"]
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if "sk" not in values:
                    date_str = ts.strftime("%Y-%m-%d")
                    timestamp_str = ts.isoformat()
                    values["sk"] = f"USAGE#{date_str}#{timestamp_str}"
                if "gsi1pk" not in values:
                    values["gsi1pk"] = f"USAGE#{ts.strftime('%Y-%m-%d')}"

            if "customer_id" in values and "gsi1sk" not in values:
                values["gsi1sk"] = values["customer_id"]

        return values


class BillingPeriod(BaseModel):
    """Billing period model for tracking charges.

    Attributes:
        pk: Partition key (BILLING#{customer_id})
        sk: Sort key (PERIOD#{year}-{month})
        customer_id: Customer for this billing period
        period_start: Start of billing period
        period_end: End of billing period
        usage_total: Total usage in this period
        charges_calculated: Calculated charges amount
        invoice_id: Associated Stripe invoice ID
        payment_status: Current payment status
        created_at: When period was created
    """

    model_config = ConfigDict(validate_assignment=True)

    pk: str = Field(..., description="Format: BILLING#{customer_id}")
    sk: str = Field(..., description="Format: PERIOD#{year}-{month}")
    customer_id: str = Field(..., min_length=1, max_length=100)
    period_start: datetime
    period_end: datetime
    usage_total: int = Field(default=0, ge=0)
    charges_calculated: Decimal = Field(default=Decimal("0.00"), ge=0)
    invoice_id: Optional[str] = Field(None, min_length=1, max_length=255)
    payment_status: str = Field(default="pending", pattern="^(pending|paid|failed)$")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="before")
    @classmethod
    def set_keys(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Auto-set DynamoDB keys based on data."""
        if isinstance(values, dict):
            if "customer_id" in values and "pk" not in values:
                values["pk"] = f"BILLING#{values['customer_id']}"

            if "period_start" in values and "sk" not in values:
                ps = values["period_start"]
                if isinstance(ps, str):
                    ps = datetime.fromisoformat(ps.replace("Z", "+00:00"))
                values["sk"] = f"PERIOD#{ps.strftime('%Y-%m')}"

        return values

    @field_validator("charges_calculated")
    @classmethod
    def validate_decimal(cls, v: Any) -> Decimal:
        """Ensure charges are proper Decimal."""
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            return Decimal(v)
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal: {v}")


class PricingTier(BaseModel):
    """Pricing tier model for tiered pricing calculations.

    Attributes:
        pk: Partition key (PRICING#{plan_type})
        sk: Sort key (TIER#{tier_number})
        plan_type: Which plan this tier applies to
        tier_number: Order of this tier (1, 2, 3, etc.)
        usage_limit: Upper limit for this tier (None = unlimited)
        price_per_unit: Price per unit in this tier
        currency: Currency code (USD, EUR, etc.)
        effective_date: When this pricing becomes effective
    """

    model_config = ConfigDict(validate_assignment=True)

    pk: str = Field(..., description="Format: PRICING#{plan_type}")
    sk: str = Field(..., description="Format: TIER#{tier_number}")
    plan_type: str = Field(..., pattern="^(free|paid|enterprise)$")
    tier_number: int = Field(..., ge=1, le=10)
    usage_limit: Optional[int] = Field(None, ge=0)
    price_per_unit: Decimal = Field(..., ge=0)
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$")
    effective_date: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="before")
    @classmethod
    def set_keys(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Auto-set DynamoDB keys based on data."""
        if isinstance(values, dict):
            if "plan_type" in values and "pk" not in values:
                values["pk"] = f"PRICING#{values['plan_type']}"

            if "tier_number" in values and "sk" not in values:
                values["sk"] = f"TIER#{values['tier_number']:02d}"

        return values

    @field_validator("price_per_unit")
    @classmethod
    def validate_price(cls, v: Any) -> Decimal:
        """Ensure price is proper Decimal."""
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            return Decimal(v)
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal: {v}")


class Invoice(BaseModel):
    """Invoice model for billing records.

    Attributes:
        pk: Partition key (INVOICE#{invoice_id})
        sk: Sort key (METADATA)
        invoice_id: Unique invoice identifier
        customer_id: Customer this invoice is for
        stripe_invoice_id: Stripe's invoice ID
        amount: Total invoice amount
        currency: Currency code
        status: Invoice status
        due_date: When payment is due
        created_at: When invoice was created
        updated_at: Last update timestamp
        line_items: Optional list of line items
    """

    model_config = ConfigDict(validate_assignment=True)

    pk: str = Field(..., description="Format: INVOICE#{invoice_id}")
    sk: str = Field(default="METADATA", description="Sort key for invoice metadata")
    invoice_id: str = Field(..., min_length=1, max_length=100)
    customer_id: str = Field(..., min_length=1, max_length=100)
    stripe_invoice_id: str = Field(..., min_length=0, max_length=255)
    amount: Decimal = Field(..., ge=0)
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$")
    status: str = Field(default="draft", pattern="^(draft|open|paid|void|uncollectible)$")
    due_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    line_items: Optional[list[dict[str, Any]]] = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def set_keys(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Auto-set DynamoDB keys based on data."""
        if isinstance(values, dict):
            if "invoice_id" in values and "pk" not in values:
                values["pk"] = f"INVOICE#{values['invoice_id']}"
            if "sk" not in values:
                values["sk"] = "METADATA"

        return values

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Any) -> Decimal:
        """Ensure amount is proper Decimal."""
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            return Decimal(v)
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal: {v}")


# Additional models for API requests/responses
class UsageRequest(BaseModel):
    """Request model for tracking usage."""

    customer_id: str = Field(..., min_length=1, max_length=100)
    api_endpoint: str = Field(..., min_length=1, max_length=255)
    usage_count: int = Field(..., ge=1)
    timestamp: Optional[datetime] = None


class ChargeCalculationResponse(BaseModel):
    """Response model for charge calculations."""

    customer_id: str
    period_start: datetime
    period_end: datetime
    usage_total: int
    charges: Decimal
    breakdown: list[dict[str, Any]]
    currency: str = "USD"
