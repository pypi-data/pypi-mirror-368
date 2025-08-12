"""Configuration management for the billing service.

This module handles configuration settings, environment variables,
and provides a centralized settings class with validation.
"""

import os
from typing import Any, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BillingSettings(BaseSettings):
    """Settings for the billing service with environment variable support.

    All settings can be configured via environment variables with
    the BILLING_ prefix (e.g., BILLING_DYNAMODB_TABLE).
    """

    model_config = SettingsConfigDict(
        env_prefix="BILLING_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # DynamoDB Configuration
    dynamodb_table: str = Field(
        default_factory=lambda: os.environ.get("DYNAMODB_TABLE", "billing-data-dev"),
        description="DynamoDB table name for billing data",
    )
    aws_region: str = Field(default="us-east-1", description="AWS region for services")
    dynamodb_endpoint_url: Optional[str] = Field(
        default=None, description="Custom DynamoDB endpoint (for local testing)"
    )

    # Stripe Configuration
    stripe_secret_key: Optional[str] = Field(
        default_factory=lambda: os.environ.get("STRIPE_SECRET_KEY"),
        description="Stripe API secret key",
    )
    stripe_webhook_secret: Optional[str] = Field(
        default_factory=lambda: os.environ.get("STRIPE_WEBHOOK_SECRET"),
        description="Stripe webhook endpoint secret",
    )
    stripe_api_version: str = Field(default="2023-10-16", description="Stripe API version to use")

    # EventBridge Configuration
    eventbridge_bus: str = Field(
        default_factory=lambda: os.environ.get("EVENTBRIDGE_BUS", "billing-events"),
        description="EventBridge bus name for billing events",
    )

    # Application Settings
    environment: str = Field(
        default_factory=lambda: os.environ.get("ENVIRONMENT", "dev"),
        pattern="^(dev|staging|prod)$",
        description="Deployment environment",
    )
    log_level: str = Field(
        default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$", description="Logging level"
    )

    # Rate Limiting
    default_rate_limit: int = Field(
        default=10000, ge=1, description="Default API rate limit per day"
    )
    rate_limit_window_seconds: int = Field(
        default=86400,  # 24 hours
        ge=60,
        description="Rate limit window in seconds",
    )

    # Pricing Defaults
    default_currency: str = Field(
        default="USD", pattern="^[A-Z]{3}$", description="Default currency code"
    )
    free_tier_limit: int = Field(default=1000, ge=0, description="Free tier usage limit")

    # Retry Configuration
    max_retries: int = Field(
        default=3, ge=0, le=10, description="Maximum retry attempts for failed operations"
    )
    retry_delay_seconds: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Initial delay between retries (exponential backoff)",
    )

    # Batch Processing
    batch_size: int = Field(
        default=25, ge=1, le=100, description="Batch size for DynamoDB operations"
    )

    # Webhook Settings
    webhook_timeout_seconds: int = Field(
        default=30, ge=5, le=300, description="Webhook processing timeout"
    )

    @field_validator("stripe_secret_key")
    @classmethod
    def validate_stripe_key(cls, v: Optional[str]) -> Optional[str]:
        """Validate Stripe secret key format."""
        if v and not v.startswith(("sk_test_", "sk_live_")):
            raise ValueError("Invalid Stripe secret key format")
        return v

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate and normalize environment."""
        return v.lower()

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "prod"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "dev"

    def get_table_name(self) -> str:
        """Get the fully qualified DynamoDB table name."""
        if self.environment in self.dynamodb_table:
            return self.dynamodb_table
        return f"{self.dynamodb_table}-{self.environment}"

    def to_dict(self, exclude_secrets: bool = True) -> dict[str, Any]:
        """Convert settings to dictionary.

        Args:
            exclude_secrets: Whether to exclude sensitive values

        Returns:
            Dictionary of settings
        """
        data = self.model_dump()

        if exclude_secrets:
            sensitive_fields = [
                "stripe_secret_key",
                "stripe_webhook_secret",
            ]
            for field in sensitive_fields:
                if data.get(field):
                    data[field] = "***REDACTED***"

        return data


# Global settings instance (lazy loaded)
_settings: Optional[BillingSettings] = None


def get_settings() -> BillingSettings:
    """Get the global settings instance (singleton pattern).

    Returns:
        BillingSettings instance
    """
    global _settings
    if _settings is None:
        _settings = BillingSettings()
    return _settings


def reset_settings() -> None:
    """Reset the global settings instance (mainly for testing)."""
    global _settings
    _settings = None


# Pricing tier configurations (can be overridden)
DEFAULT_PRICING_TIERS = {
    "free": [
        {"tier": 1, "limit": 1000, "price_per_unit": 0.00},
    ],
    "paid": [
        {"tier": 1, "limit": 1000, "price_per_unit": 0.00},
        {"tier": 2, "limit": 10000, "price_per_unit": 0.01},
        {"tier": 3, "limit": 100000, "price_per_unit": 0.008},
        {"tier": 4, "limit": None, "price_per_unit": 0.006},
    ],
    "enterprise": [
        {"tier": 1, "limit": 10000, "price_per_unit": 0.00},
        {"tier": 2, "limit": 100000, "price_per_unit": 0.007},
        {"tier": 3, "limit": 1000000, "price_per_unit": 0.005},
        {"tier": 4, "limit": None, "price_per_unit": 0.003},
    ],
}
