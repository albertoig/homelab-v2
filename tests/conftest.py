"""Pytest configuration and fixtures for Pulumi infrastructure tests."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_pulumi_config():
    """Fixture providing a mock Pulumi config."""
    config = MagicMock()
    config.get = MagicMock(return_value="test-value")
    return config


@pytest.fixture
def mock_aws_provider():
    """Fixture providing a mock AWS provider."""
    provider = MagicMock()
    provider.id = "test-provider-id"
    return provider
