"""Provider-independent local API credential loading."""
from __future__ import annotations

import os
from pathlib import Path

# PROVIDERS_DIRECTORY — canonical local provider-credential directory.
PROVIDERS_DIRECTORY = Path(__file__).resolve().parent
# Backward-compatible constant name; it points to PROVIDERS/, never an apikeys/ directory.
APIKEYS_DIRECTORY = PROVIDERS_DIRECTORY

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
    """Load exactly one provider API key from an environment override or local file."""
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

    directory = Path(api_keys_directory) if api_keys_directory is not None else PROVIDERS_DIRECTORY
    key_path = directory / f"{provider}.apikey"
    try:
        raw_lines = key_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise ProviderCredentialError(
            f"API key is not configured for provider '{provider}'"
        ) from exc
    except OSError as exc:
        raise ProviderCredentialError(
            f"API key file cannot be read for provider '{provider}'"
        ) from exc

    non_empty_lines = [line.strip() for line in raw_lines if line.strip()]
    if len(non_empty_lines) != 1:
        raise ProviderCredentialError(
            f"API key is not configured for provider '{provider}'"
        )

    key_value = non_empty_lines[0]
    placeholder_values = {
        f"PASTE_{provider.upper()}_API_KEY_HERE",
        "YOUR_API_KEY_HERE",
        "YOUR_API_KEY",
    }
    if key_value in placeholder_values:
        raise ProviderCredentialError(
            f"API key is not configured for provider '{provider}'"
        )
    return key_value
