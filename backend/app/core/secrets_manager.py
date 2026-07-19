from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)


class SecretsProvider:
    """Manages retrieving production configuration secrets from external vault/cloud providers."""

    def __init__(self) -> None:
        self.provider = os.getenv("SECRET_PROVIDER", "local").lower().strip()
        logger.info("Initializing secret provider: %s", self.provider)

    def fetch_secrets(self) -> dict[str, Any]:
        """Fetch secrets dictionary from the configured provider."""
        if self.provider == "vault":
            return self._fetch_from_vault()
        elif self.provider == "gcp":
            return self._fetch_from_gcp()
        else:
            logger.info(
                "Using local environment settings. No external secrets fetched."
            )
            return {}

    def _fetch_from_vault(self) -> dict[str, Any]:
        """Fetch secrets from HashiCorp Vault HTTP API."""
        vault_addr = os.getenv("VAULT_ADDR", "http://localhost:8200").rstrip("/")
        vault_token = os.getenv("VAULT_TOKEN", "root")
        vault_path = os.getenv("VAULT_SECRET_PATH", "rhos")

        # Vault KV v2 API: secret/data/{path}
        url = f"{vault_addr}/v1/secret/data/{vault_path}"
        logger.info("Fetching secrets from Vault at %s", url)

        req = urllib.request.Request(url)
        req.add_header("X-Vault-Token", vault_token)

        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                body = response.read().decode("utf-8")
                res_data = json.loads(body)
                secrets = res_data.get("data", {}).get("data", {})
                logger.info(
                    "Successfully fetched %d secrets from HashiCorp Vault", len(secrets)
                )
                return secrets
        except urllib.error.URLError as e:
            logger.error(
                "Failed to fetch secrets from Vault: %s. Falling back to local env.", e
            )
            return {}
        except Exception as e:
            logger.error("Unexpected error fetching secrets from Vault: %s", e)
            return {}

    def _fetch_from_gcp(self) -> dict[str, Any]:
        """Fetch JSON secrets payload from GCP Secret Manager."""
        project_id = os.getenv("GCP_PROJECT_ID")
        secret_name = os.getenv("GCP_SECRET_NAME", "rhos-secrets")
        version = os.getenv("GCP_SECRET_VERSION", "latest")

        if not project_id:
            logger.warning(
                "GCP_PROJECT_ID environment variable is missing. Cannot fetch GCP secrets."
            )
            return {}

        # If google-cloud-secret-manager package is installed, use it. Otherwise fall back.
        try:
            from google.cloud import secretmanager

            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{project_id}/secrets/{secret_name}/versions/{version}"
            logger.info("Fetching secrets from GCP Secret Manager: %s", name)
            response = client.access_secret_version(request={"name": name})
            payload = response.payload.data.decode("UTF-8")
            secrets = json.loads(payload)
            logger.info(
                "Successfully fetched %d secrets from GCP Secret Manager", len(secrets)
            )
            return secrets
        except ImportError:
            logger.warning(
                "google-cloud-secret-manager library is not installed. Cannot use GCP provider."
            )
            return {}
        except Exception as e:
            logger.error("Error retrieving secrets from GCP Secret Manager: %s", e)
            return {}


secrets_provider = SecretsProvider()
