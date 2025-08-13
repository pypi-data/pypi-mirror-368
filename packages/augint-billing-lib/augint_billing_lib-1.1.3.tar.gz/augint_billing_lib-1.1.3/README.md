# Augint Billing Library

**Billing service library for API usage tracking, tiered pricing calculations, and Stripe integration.**

## Overview

This library provides the core business logic for:
- Tracking API usage per customer
- Calculating charges with tiered pricing models  
- Managing Stripe customers and payments
- Processing webhooks from Stripe
- Generating usage and billing reports


[![CI Pipeline](https://github.com/svange/augint-billing-lib/actions/workflows/pipeline.yaml/badge.svg?branch=main)](https://github.com/svange/augint-billing-lib/actions/workflows/pipeline.yaml)
[![PyPI](https://img.shields.io/pypi/v/augint-billing-lib?style=flat-square)](https://pypi.org/project/augint-billing-lib/)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square)](https://www.python.org/downloads/)

[![Poetry](https://img.shields.io/badge/dependency%20manager-poetry-blue?style=flat-square)](https://python-poetry.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=flat-square)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Renovate](https://img.shields.io/badge/renovate-enabled-blue?style=flat-square&logo=renovatebot)](https://renovatebot.com)

[![pytest](https://img.shields.io/badge/testing-pytest-green?style=flat-square&logo=pytest)](https://pytest.org/)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-blue?style=flat-square&logo=github-actions)](https://github.com/features/actions)
[![Semantic Release](https://img.shields.io/badge/release-semantic--release-e10079?style=flat-square&logo=semantic-release)](https://github.com/semantic-release/semantic-release)
[![AWS SAM](https://img.shields.io/badge/Infrastructure-AWS%20SAM-orange?style=flat-square&logo=amazon-aws)](https://aws.amazon.com/serverless/sam/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg?style=flat-square)](https://www.gnu.org/licenses/agpl-3.0)


## 📊 Live Dashboards

| 📖 **[Documentation](https://svange.github.io/augint-billing-lib)** | 🧪 **[Unit Tests](https://svange.github.io/augint-billing-lib/unit-test-report.html)** | 🔬 **[Integration Tests](https://svange.github.io/augint-billing-lib/integration-test-report.html)** | 📊 **[Coverage](https://svange.github.io/augint-billing-lib/htmlcov/index.html)** | ⚡ **[Benchmarks](https://svange.github.io/augint-billing-lib/benchmark-report.html)** | 🔒 **[Security](https://svange.github.io/augint-billing-lib/security-reports.html)** | ⚖️ **[Compliance](https://svange.github.io/augint-billing-lib/license-compatibility.html)** |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|


## 🔑 Key Development Characteristics

| Characteristic | Details |
|:--------------|:--------|
| **Merge Strategy** | Configurable (see .env) |
| **Deployment Model** | Tag-based to PyPI |
| **Environments** | Local → PyPI |
| **Preview Environments** | N/A (library) |
| **Pipeline Features** | Semantic release, Auto-publish to PyPI |
| **Special Considerations** | 90% coverage requirement, Mutation testing |

---




## Project Structure

```
augint-billing-lib-library/
├── src/
│   └── augint_billing_lib/      # Core library code (to be implemented)
├── tests/                   # Test suite (to be implemented)
├── examples/                # Original template code for reference
├── pyproject.toml          # Project dependencies and configuration
├── Makefile                # Development commands
└── README.md               # This file
```

## Development Setup

```bash
# Install dependencies
make install

# Run tests
make test

# Check code quality
make lint
make type-check

# Generate documentation
make docs
```

## Implementation Status

This is a minimal template ready for implementation. The following components need to be built:

### Library Exports (from planning spec)
- [ ] BillingService - Main service class
- [ ] UsageCollector - Track API usage
- [ ] PricingCalculator - Apply tiered pricing
- [ ] StripeManager - Stripe operations
- [ ] WebhookProcessor - Process Stripe webhooks
- [ ] ReportGenerator - Generate reports
- [ ] Data models (Customer, UsageRecord, BillingPeriod, etc.)

### Key Features Removed (Minimal Version)
- ✅ Feature flags removed
- ✅ Telemetry/Sentry removed
- ✅ Mutation testing removed  
- ✅ Complex CLI structures removed

## Dependencies

Core dependencies:
- click - CLI framework
- boto3 - AWS SDK (to be added)
- stripe - Stripe SDK (to be added)
- pydantic - Data validation (to be added)

## Testing

The project uses pytest with pragmatic coverage targets:
- Library code: 70% coverage target
- Focus on core business logic
- Integration tests for AWS/Stripe interactions
