from __future__ import annotations

import json
import os
import pytest
from unittest.mock import MagicMock, patch

from app.core.secrets_manager import SecretsProvider
from app.config import get_settings

def test_secrets_provider_local_by_default():
    """Test SecretsProvider defaults to local environment and returns empty dict."""
    with patch.dict(os.environ, {"SECRET_PROVIDER": "local"}):
        provider = SecretsProvider()
        assert provider.provider == "local"
        assert provider.fetch_secrets() == {}


def test_secrets_provider_vault_success():
    """Test successful secrets retrieval from HashiCorp Vault."""
    mock_response_data = {
        "data": {
            "data": {
                "jwt_secret_key": "vault-jwt-secret-12345",
                "mongodb_uri": "mongodb://vault:27017"
            }
        }
    }
    
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(mock_response_data).encode("utf-8")
    
    mock_urlopen_ctx = MagicMock()
    mock_urlopen_ctx.__enter__.return_value = mock_response
    
    with patch.dict(os.environ, {
        "SECRET_PROVIDER": "vault",
        "VAULT_ADDR": "http://mock-vault:8200",
        "VAULT_TOKEN": "mock-token",
        "VAULT_SECRET_PATH": "mock-rhos"
    }), patch("urllib.request.urlopen", return_value=mock_urlopen_ctx) as mock_urlopen:
        
        provider = SecretsProvider()
        assert provider.provider == "vault"
        secrets = provider.fetch_secrets()
        
        assert secrets == {
            "jwt_secret_key": "vault-jwt-secret-12345",
            "mongodb_uri": "mongodb://vault:27017"
        }
        
        mock_urlopen.assert_called_once()
        req = mock_urlopen.call_args[0][0]
        assert req.full_url == "http://mock-vault:8200/v1/secret/data/mock-rhos"
        assert req.get_header("X-vault-token") == "mock-token"


def test_secrets_provider_gcp_success():
    """Test successful secrets retrieval from GCP Secret Manager."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.payload.data = b'{"jwt_secret_key": "gcp-jwt-secret", "gemini_api_key": "gcp-gemini"}'
    mock_client.access_secret_version.return_value = mock_response

    with patch.dict(os.environ, {
        "SECRET_PROVIDER": "gcp",
        "GCP_PROJECT_ID": "mock-gcp-project",
        "GCP_SECRET_NAME": "mock-secrets"
    }), patch("google.cloud.secretmanager.SecretManagerServiceClient", return_value=mock_client):
        
        provider = SecretsProvider()
        assert provider.provider == "gcp"
        secrets = provider.fetch_secrets()
        
        assert secrets == {
            "jwt_secret_key": "gcp-jwt-secret",
            "gemini_api_key": "gcp-gemini"
        }
        mock_client.access_secret_version.assert_called_once_with(
            request={"name": "projects/mock-gcp-project/secrets/mock-secrets/versions/latest"}
        )


def test_get_settings_injects_secrets():
    """Test get_settings successfully loads and overrides configuration from SecretsProvider."""
    # Reset singleton first
    import app.config as config_module
    config_module._settings = None
    
    mock_secrets = {
        "jwt_secret_key": "injected-jwt-secret-key-at-least-32-chars",
        "mongodb_uri": "mongodb://injected-host:27017"
    }
    
    with patch.dict(os.environ, {"SECRET_PROVIDER": "vault"}), \
         patch("app.core.secrets_manager.secrets_provider.fetch_secrets", return_value=mock_secrets):
             
        settings = get_settings()
        assert settings.jwt_secret_key == "injected-jwt-secret-key-at-least-32-chars"
        assert settings.mongodb_uri == "mongodb://injected-host:27017"
        
        # Verify injected into environment
        assert os.environ.get("JWT_SECRET_KEY") == "injected-jwt-secret-key-at-least-32-chars"
        assert os.environ.get("MONGODB_URI") == "mongodb://injected-host:27017"
