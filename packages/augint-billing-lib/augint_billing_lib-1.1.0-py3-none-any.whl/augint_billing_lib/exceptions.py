"""Custom exceptions for the billing service.

This module defines custom exception classes for billing operations,
providing structured error handling with proper context and chaining.
"""

from typing import Any, Optional


class BillingError(Exception):
    """Base exception for all billing-related errors.

    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code
        details: Additional error context
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize billing error.

        Args:
            message: Error message
            error_code: Optional error code for categorization
            details: Optional additional context
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}

    def __str__(self) -> str:
        """String representation of the error."""
        if self.details:
            return f"{self.error_code}: {self.message} - Details: {self.details}"
        return f"{self.error_code}: {self.message}"


class CustomerNotFoundError(BillingError):
    """Raised when a customer cannot be found."""

    def __init__(self, customer_id: str) -> None:
        """Initialize customer not found error.

        Args:
            customer_id: The customer ID that was not found
        """
        super().__init__(
            message=f"Customer not found: {customer_id}",
            error_code="CUSTOMER_NOT_FOUND",
            details={"customer_id": customer_id},
        )


class UsageValidationError(BillingError):
    """Raised when usage data fails validation."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        """Initialize usage validation error.

        Args:
            message: Validation error message
            field: Optional field that failed validation
        """
        details = {}
        if field:
            details["field"] = field

        super().__init__(message=message, error_code="USAGE_VALIDATION_ERROR", details=details)


class PricingConfigurationError(BillingError):
    """Raised when pricing configuration is invalid or missing."""

    def __init__(self, plan_type: str, message: Optional[str] = None) -> None:
        """Initialize pricing configuration error.

        Args:
            plan_type: The plan type with configuration issues
            message: Optional custom message
        """
        msg = message or f"Invalid or missing pricing configuration for plan: {plan_type}"
        super().__init__(
            message=msg, error_code="PRICING_CONFIG_ERROR", details={"plan_type": plan_type}
        )


class StripeError(BillingError):
    """Raised when Stripe operations fail."""

    def __init__(
        self,
        message: str,
        stripe_error_code: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ) -> None:
        """Initialize Stripe error.

        Args:
            message: Error message
            stripe_error_code: Stripe's error code if available
            original_error: Original exception from Stripe
        """
        details = {}
        if stripe_error_code:
            details["stripe_error_code"] = stripe_error_code
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(message=message, error_code="STRIPE_ERROR", details=details)
        self.original_error = original_error


class InvoiceGenerationError(BillingError):
    """Raised when invoice generation fails."""

    def __init__(
        self,
        customer_id: str,
        period: str,
        reason: Optional[str] = None,
    ) -> None:
        """Initialize invoice generation error.

        Args:
            customer_id: Customer for whom invoice generation failed
            period: Billing period that failed
            reason: Optional reason for failure
        """
        message = f"Failed to generate invoice for customer {customer_id}, period {period}"
        if reason:
            message += f": {reason}"

        super().__init__(
            message=message,
            error_code="INVOICE_GENERATION_ERROR",
            details={"customer_id": customer_id, "period": period, "reason": reason},
        )


class WebhookValidationError(BillingError):
    """Raised when webhook validation fails."""

    def __init__(self, message: str, webhook_type: Optional[str] = None) -> None:
        """Initialize webhook validation error.

        Args:
            message: Error message
            webhook_type: Type of webhook that failed validation
        """
        details = {}
        if webhook_type:
            details["webhook_type"] = webhook_type

        super().__init__(message=message, error_code="WEBHOOK_VALIDATION_ERROR", details=details)


class BillingPeriodError(BillingError):
    """Raised when there are issues with billing periods."""

    def __init__(
        self,
        message: str,
        customer_id: Optional[str] = None,
        period: Optional[str] = None,
    ) -> None:
        """Initialize billing period error.

        Args:
            message: Error message
            customer_id: Optional customer ID
            period: Optional billing period
        """
        details = {}
        if customer_id:
            details["customer_id"] = customer_id
        if period:
            details["period"] = period

        super().__init__(message=message, error_code="BILLING_PERIOD_ERROR", details=details)


class DynamoDBError(BillingError):
    """Raised when DynamoDB operations fail."""

    def __init__(
        self,
        message: str,
        table_name: Optional[str] = None,
        operation: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ) -> None:
        """Initialize DynamoDB error.

        Args:
            message: Error message
            table_name: DynamoDB table name
            operation: Operation that failed
            original_error: Original exception from boto3
        """
        details = {}
        if table_name:
            details["table_name"] = table_name
        if operation:
            details["operation"] = operation
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(message=message, error_code="DYNAMODB_ERROR", details=details)
        self.original_error = original_error


class ConfigurationError(BillingError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, config_key: str, message: Optional[str] = None) -> None:
        """Initialize configuration error.

        Args:
            config_key: Configuration key that is missing or invalid
            message: Optional custom message
        """
        msg = message or f"Missing or invalid configuration: {config_key}"
        super().__init__(
            message=msg, error_code="CONFIGURATION_ERROR", details={"config_key": config_key}
        )


class RateLimitError(BillingError):
    """Raised when rate limits are exceeded."""

    def __init__(
        self,
        customer_id: str,
        limit: int,
        current: int,
        reset_time: Optional[str] = None,
    ) -> None:
        """Initialize rate limit error.

        Args:
            customer_id: Customer who exceeded the limit
            limit: The rate limit
            current: Current usage
            reset_time: When the limit resets
        """
        message = f"Rate limit exceeded for customer {customer_id}: {current}/{limit}"
        details = {
            "customer_id": customer_id,
            "limit": limit,
            "current": current,
        }
        if reset_time:
            details["reset_time"] = reset_time

        super().__init__(message=message, error_code="RATE_LIMIT_ERROR", details=details)

        # Store as attributes for easy access
        self.customer_id = customer_id
        self.limit = limit
        self.current_usage = current
        self.reset_time = reset_time


class BillingServiceError(BillingError):
    """Raised when general billing service operations fail."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize billing service error.

        Args:
            message: Error message
            **kwargs: Additional context to include in details
        """
        super().__init__(
            message=message, error_code="BILLING_SERVICE_ERROR", details=kwargs if kwargs else {}
        )


class StripeIntegrationError(StripeError):
    """Raised when Stripe integration operations fail."""

    def __init__(self, message: str, operation: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize Stripe integration error.

        Args:
            message: Error message
            operation: Operation that failed
            **kwargs: Additional context
        """
        details = {"operation": operation} if operation else {}
        details.update(kwargs)
        super().__init__(message=message, stripe_error_code=None, original_error=None)
        self.details = details


class WebhookProcessingError(WebhookValidationError):
    """Raised when webhook processing fails after validation."""

    def __init__(
        self,
        message: str,
        event_type: Optional[str] = None,
        event_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize webhook processing error.

        Args:
            message: Error message
            event_type: Type of webhook event
            event_id: Event identifier
            **kwargs: Additional context
        """
        details = {}
        if event_type:
            details["event_type"] = event_type
        if event_id:
            details["event_id"] = event_id
        details.update(kwargs)

        super().__init__(message=message, webhook_type=event_type)
        self.details = details
