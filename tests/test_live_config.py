"""Tests for live test configuration loading."""

from live_tests.config import load_live_config


def test_load_live_config_from_env(monkeypatch) -> None:
    """Live config reads PROLIPHIX_PLUS_* environment variables."""
    monkeypatch.setenv("PROLIPHIX_PLUS_HOST", "http://example.test:8888")
    monkeypatch.setenv("PROLIPHIX_PLUS_USERNAME", "admin")
    monkeypatch.setenv("PROLIPHIX_PLUS_PASSWORD", "secret")

    config = load_live_config()
    assert config.is_configured
    assert config.host == "http://example.test:8888"
    assert config.username == "admin"
    assert config.password == "secret"
