"""Pricing calculation service for tiered billing.

This module provides the PricingCalculator class for applying
tiered pricing rules and calculating charges for usage.
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from .config import DEFAULT_PRICING_TIERS, get_settings
from .db import DynamoDBClient
from .exceptions import CustomerNotFoundError, PricingConfigurationError
from .models import BillingPeriod, PricingTier
from .types import ChargeEstimateDict, PeriodChargesDict
from .usage_collector import UsageCollector
from .utils import calculate_charges, get_billing_period_bounds

logger = logging.getLogger(__name__)


class PricingCalculator:
    """Applies tiered pricing rules to calculate charges.

    This class handles loading pricing configurations, applying tiered
    pricing models, and calculating charges for customer usage.
    """

    def __init__(self, table_name: Optional[str] = None):
        """Initialize pricing calculator.

        Args:
            table_name: DynamoDB table name (uses env var if not provided)
        """
        settings = get_settings()
        self.table_name = table_name or settings.dynamodb_table
        self.db_client = DynamoDBClient(table_name=self.table_name)
        self.default_currency = settings.default_currency

        # Cache for pricing tiers (refreshed periodically)
        self._pricing_cache: dict[str, list[PricingTier]] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl_seconds = 300  # 5 minutes

        logger.info(f"Initialized PricingCalculator with table: {self.table_name}")

    def calculate_customer_charges(
        self,
        customer_id: str,
        usage_count: int,
        period: Optional[str] = None,
        save_to_db: bool = False,
    ) -> dict[str, Any]:
        """Calculate charges for a customer's usage.

        Args:
            customer_id: Customer ID
            usage_count: Total usage to calculate charges for
            period: Billing period (YYYY-MM format, optional)
            save_to_db: Whether to save billing period to database

        Returns:
            Dictionary with charges and breakdown

        Raises:
            CustomerNotFoundError: If customer doesn't exist
            PricingConfigurationError: If pricing config is invalid
        """
        # Get customer data
        customer = self.db_client.get_customer(customer_id)
        if not customer:
            raise CustomerNotFoundError(customer_id)

        plan_type = customer.get("plan_type", "free")

        # Get pricing tiers for customer's plan
        pricing_tiers = self.get_pricing_tiers(plan_type)

        # Calculate charges
        total_charges, breakdown = calculate_charges(
            usage_count=usage_count, pricing_tiers=pricing_tiers, currency=self.default_currency
        )

        result = {
            "customer_id": customer_id,
            "plan_type": plan_type,
            "usage_count": usage_count,
            "total_charges": float(total_charges),
            "currency": self.default_currency,
            "breakdown": breakdown,
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }

        # Save to database if requested
        if save_to_db and period:
            self._save_billing_period(
                customer_id=customer_id,
                period=period,
                usage_total=usage_count,
                charges=total_charges,
            )

        logger.info(
            f"Calculated charges for customer {customer_id}: "
            f"{total_charges} {self.default_currency} for {usage_count} units"
        )

        return result

    def get_pricing_tiers(
        self, plan_type: str, use_cache: bool = True, effective_date: Optional[datetime] = None
    ) -> list[PricingTier]:
        """Get pricing tiers for a plan type.

        Args:
            plan_type: Plan type (free, paid, enterprise)
            use_cache: Whether to use cached tiers
            effective_date: Date for which to get pricing (default: now)

        Returns:
            List of pricing tiers

        Raises:
            PricingConfigurationError: If no pricing found
        """
        # Check cache if enabled
        if use_cache and self._is_cache_valid() and plan_type in self._pricing_cache:
            return self._pricing_cache[plan_type]

        # Try to load from database
        try:
            items = self.db_client.get_pricing_tiers(plan_type)

            if items:
                # Convert to PricingTier models
                tiers = []
                for item in items:
                    # Filter by effective date if provided
                    if effective_date:
                        eff_date_str = item.get("effective_date")
                        if eff_date_str:
                            eff_date = datetime.fromisoformat(eff_date_str)
                        else:
                            continue
                        if eff_date > effective_date:
                            continue

                    tiers.append(PricingTier(**item))

                # Sort by tier number
                tiers.sort(key=lambda t: t.tier_number)

                # Update cache
                self._pricing_cache[plan_type] = tiers
                self._cache_timestamp = datetime.now(timezone.utc)

                logger.debug(f"Loaded {len(tiers)} pricing tiers for {plan_type}")
                return tiers

        except Exception as e:
            logger.warning(f"Failed to load pricing from database: {e}")

        # Fall back to default configuration
        default_tiers = DEFAULT_PRICING_TIERS.get(plan_type)
        if not default_tiers:
            raise PricingConfigurationError(
                plan_type, f"No pricing configuration found for plan type: {plan_type}"
            )
        # Convert default config to PricingTier models
        tiers = []
        tier_config: dict[str, Any]
        for i, tier_config in enumerate(default_tiers, 1):  # type: ignore[arg-type]
            tier = PricingTier(
                pk=f"PRICING#{plan_type}",
                sk=f"TIER#{i}",
                plan_type=plan_type,
                tier_number=i,
                usage_limit=tier_config["limit"],  # type: ignore[index]
                price_per_unit=Decimal(str(tier_config["price_per_unit"])),  # type: ignore[index]
                currency=self.default_currency,
                effective_date=datetime.now(timezone.utc),
            )
            tiers.append(tier)

        # Update cache
        self._pricing_cache[plan_type] = tiers
        self._cache_timestamp = datetime.now(timezone.utc)

        logger.info(f"Using default pricing tiers for {plan_type}")
        return tiers

    def update_pricing_tiers(
        self, plan_type: str, tiers: list[dict[str, Any]], effective_date: Optional[datetime] = None
    ) -> bool:
        """Update pricing tiers for a plan type.

        Args:
            plan_type: Plan type to update
            tiers: List of tier configurations
            effective_date: When pricing becomes effective

        Returns:
            True if successful

        Raises:
            PricingConfigurationError: If configuration is invalid
        """
        if not tiers:
            raise PricingConfigurationError(plan_type, "At least one pricing tier is required")

        effective_date = effective_date or datetime.now(timezone.utc)

        # Validate and create PricingTier models
        tier_models = []
        for i, tier_config in enumerate(tiers, 1):
            tier = PricingTier(
                pk=f"PRICING#{plan_type}",
                sk=f"TIER#{i}",
                plan_type=plan_type,
                tier_number=i,
                usage_limit=tier_config.get("usage_limit"),
                price_per_unit=Decimal(str(tier_config["price_per_unit"])),
                currency=tier_config.get("currency", self.default_currency),
                effective_date=effective_date,
            )
            tier_models.append(tier)

        # Save to database
        try:
            items_to_write = [tier.model_dump() for tier in tier_models]
            self.db_client.batch_write(items_to_write, operation="put")

            # Invalidate cache
            self._invalidate_cache()

            logger.info(f"Updated {len(tier_models)} pricing tiers for {plan_type}")
            return True

        except Exception as e:
            logger.exception("Failed to update pricing tiers: ")
            raise PricingConfigurationError(
                plan_type, f"Failed to save pricing tiers: {e!s}"
            ) from e

    def calculate_period_charges(
        self, customer_id: str, year: int, month: int
    ) -> PeriodChargesDict:
        """Calculate charges for a full billing period.

        Args:
            customer_id: Customer ID
            year: Billing year
            month: Billing month

        Returns:
            Billing period data with charges

        Raises:
            BillingPeriodError: If period data is invalid
        """
        # Get or create billing period
        billing_period = self.db_client.get_billing_period(customer_id, year, month)

        if not billing_period:
            # Calculate period bounds
            period_start, period_end = get_billing_period_bounds(
                datetime(year, month, 1, tzinfo=timezone.utc)
            )

            # Get usage for period
            collector = UsageCollector(table_name=self.table_name)
            usage_data = collector.get_usage_by_period(customer_id, year, month)

            usage_total = usage_data["total_usage"]
        else:
            usage_total = billing_period.get("usage_total", 0)
            period_start = datetime.fromisoformat(billing_period["period_start"])
            period_end = datetime.fromisoformat(billing_period["period_end"])

        # Calculate charges
        result = self.calculate_customer_charges(
            customer_id=customer_id,
            usage_count=usage_total,
            period=f"{year:04d}-{month:02d}",
            save_to_db=True,
        )

        result.update(
            {
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "year": year,
                "month": month,
            }
        )

        return result  # type: ignore[return-value]

    def estimate_charges(self, plan_type: str, usage_count: int) -> ChargeEstimateDict:
        """Estimate charges for a given usage amount.

        Args:
            plan_type: Plan type to estimate for
            usage_count: Usage amount to estimate

        Returns:
            Estimated charges and breakdown

        Raises:
            PricingConfigurationError: If pricing config is invalid
        """
        # Get pricing tiers
        pricing_tiers = self.get_pricing_tiers(plan_type)

        # Calculate charges
        total_charges, breakdown = calculate_charges(
            usage_count=usage_count, pricing_tiers=pricing_tiers, currency=self.default_currency
        )

        return {
            "plan_type": plan_type,
            "usage_count": usage_count,
            "estimated_charges": float(total_charges),
            "currency": self.default_currency,
            "breakdown": breakdown,
            "is_estimate": True,
        }

    def compare_plans(self, usage_count: int) -> list[ChargeEstimateDict]:
        """Compare charges across different plan types.

        Args:
            usage_count: Usage amount to compare

        Returns:
            List of estimates for each plan type
        """
        plans = ["free", "paid", "enterprise"]
        comparisons = []

        for plan_type in plans:
            try:
                estimate = self.estimate_charges(plan_type, usage_count)
                comparisons.append(estimate)
            except PricingConfigurationError:
                logger.warning(f"Could not estimate charges for plan: {plan_type}")

        # Sort by total charges
        comparisons.sort(key=lambda x: x["estimated_charges"])

        return comparisons

    def _save_billing_period(
        self, customer_id: str, period: str, usage_total: int, charges: Decimal
    ) -> None:
        """Save billing period data to database.

        Args:
            customer_id: Customer ID
            period: Period string (YYYY-MM)
            usage_total: Total usage
            charges: Calculated charges
        """
        year, month = map(int, period.split("-"))
        period_start, period_end = get_billing_period_bounds(
            datetime(year, month, 1, tzinfo=timezone.utc)
        )

        period_key = f"{year}-{month:02d}"
        billing_period = BillingPeriod(
            pk=f"BILLING#{customer_id}",
            sk=f"PERIOD#{period_key}",
            customer_id=customer_id,
            period_start=period_start,
            period_end=period_end,
            usage_total=usage_total,
            charges_calculated=charges,
            invoice_id=None,
            payment_status="pending",
        )

        try:
            self.db_client.put_item(billing_period.model_dump())
            logger.debug(f"Saved billing period for {customer_id}: {period}")
        except Exception:
            logger.exception("Failed to save billing period: ")

    def _is_cache_valid(self) -> bool:
        """Check if pricing cache is still valid."""
        if not self._cache_timestamp:
            return False

        age = (datetime.now(timezone.utc) - self._cache_timestamp).total_seconds()
        return age < self._cache_ttl_seconds

    def _invalidate_cache(self) -> None:
        """Invalidate the pricing cache."""
        self._pricing_cache.clear()
        self._cache_timestamp = None
        logger.debug("Invalidated pricing cache")
