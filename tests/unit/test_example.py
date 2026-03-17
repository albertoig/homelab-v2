"""Example unit tests for Pulumi infrastructure."""


def test_example_placeholder():
    """Placeholder test to verify test discovery works."""
    assert True


def test_example_with_config(mock_pulumi_config):
    """Example test using the mock Pulumi config fixture."""
    value = mock_pulumi_config.get("test-key")
    assert value == "test-value"
