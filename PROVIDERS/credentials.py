"""Provider-independent local API credential loading."""
from __future__ import annotations

import os
from pathlib import Path

APIKEYS_DIRECTORY = Path(__file__).resolve().parent.parent / "apikeys"
_PROVIDER_ENVIRONMENT_NAMES = {
    "lse": "LSE_API_KEY",
}


class ProviderCredentialError(RuntimeError):
    """Raised when a provider credential is missing or invalid."""


def get_provider_api_key(
    provider_name: str,
    *,
    environment_name: str | None = None,
    api_keys_directory: Path | None = None,
) -> str:
    """Load one provider API key from the environment or its local key file."""
    provider = provider_name.strip().lower()
    if not provider or any(character in provider for character in "/\\\x00"):
        raise ProviderCredentialError("invalid provider credential identifier")

    environment_variable = environment_name or _PROVIDER_ENVIRONMENT_NAMES.get(
        provider,
        f"{provider.upper()}_API_KEY",
    )
    environment_value = os.environ.get(environment_variable, "").strip()
    if environment_value:
        return environment_value

    directory = api_keys_directory or APIKEYS_DIRECTORY
    key_path = directory / f"{provider}.apikey"
    try:
        key_value = key_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise ProviderCredentialError(
            f"API key is not configured for provider '{provider}'"
        ) from exc
    except OSError as exc:
        raise ProviderCredentialError(
            f"API key file cannot be read for provider '{provider}'"
        ) from exc

    if not key_value or key_value == f"PASTE_{provider.upper()}_API_KEY_HERE":
        raise ProviderCredentialError(
            f"API key is not configured for provider '{provider}'"
        )
    return key_value
