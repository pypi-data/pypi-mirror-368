import re
from pathlib import Path

from typing import Dict, Tuple
from samsara_fn.clilogger import logger


def is_one_level_str_dict(prefix: str, d: dict) -> bool:
    """Check if the dictionary is one level deep with string values."""
    had_error = False
    for k, v in d.items():
        if not isinstance(v, str):
            logger.error(
                f"{prefix} key '{k}' must be just a string, not {type(v).__name__}"
            )
            had_error = True

    return not had_error


def is_valid_function_name(name: str) -> bool:
    """Check if the function name is valid."""
    return re.match(r"^[a-zA-Z0-9_-]+$", name) is not None


def is_valid_secrets_file_name(secrets_path: str) -> bool:
    """Check if the secrets file name starts with a dot.

    Args:
        secrets_path: Path to the secrets file

    Returns:
        bool: True if the filename (not the full path) starts with a dot, False otherwise
    """
    filename = Path(secrets_path).name
    return filename.startswith(".")


def clean_alert_payload(payload: Dict) -> Dict:
    """Remove schema reference from payload."""
    return {k: v for k, v in payload.items() if k != "$schema"}


def validate_alert_payload(payload: Dict) -> Tuple[bool, str]:
    """Validate alert payload structure and types.

    This function validates that the alert payload:
    1. Contains all required fields (driverId, assetId, alertConfigurationId)
    2. Has correct types for all fields (all must be strings)
    3. Does not contain any unexpected fields (except $schema)

    Args:
        payload: Dictionary containing the alert payload to validate

    Returns:
        Tuple[bool, str]:
            - First element is True if payload is valid, False otherwise
            - Second element contains error message if validation fails, empty string if valid

    Example of valid payload:
        {
            "driverId": "123",
            "assetId": "456",
            "alertConfigurationId": "789"
        }
    """
    # Required fields
    required_fields = {"driverId": str, "assetId": str, "alertConfigurationId": str}

    # Check for required fields
    for field, expected_type in required_fields.items():
        if field not in payload:
            return False, f"Missing required field: {field}"
        if not isinstance(payload[field], expected_type):
            return (
                False,
                f"Field '{field}' must be a string, got {type(payload[field]).__name__}",
            )

    # Check for extra fields (excluding $schema)
    extra_fields = set(payload.keys()) - set(required_fields.keys()) - {"$schema"}
    if extra_fields:
        return False, f"Unexpected fields found: {', '.join(extra_fields)}"

    return True, ""
