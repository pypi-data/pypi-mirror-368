import base64
import datetime
import re
import typing

import orjson

from ._dates import parse_timestamp
from ._regex import (
    RE_DOMAIN_NAMES,
    RE_EMAIL,
    RE_HTML,
    RE_JAVASCRIPT,
    RE_PHONE_NUMBER,
    RE_UUID,
    REGEX_CAMEL_CASE,
)


def is_uuid(s: str) -> bool:
    return (
        re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", s)
        is not None
    )


def camel_to_slug(s: str, force_lower: bool = True) -> str:
    # Step 1: Handle acronyms and numbers, keeping numbers joined with preceding letters
    s = REGEX_CAMEL_CASE.sub(r"_", s)

    # Step 2: Remove any leading underscore
    s = s.lstrip("_")

    # Step 3: Convert to lowercase and replace multiple underscores with single ones
    return re.sub(r"_+", "_", s.lower() if force_lower else s)


def camel_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def camel_to_kebab(name: str, protected_acronyms: list[str] | None = None) -> str:
    if protected_acronyms:
        name = re.sub(
            r"(?<!^)(?=[A-Z])",
            "-",
            name,
            count=1,
        )
        for acronym in protected_acronyms:
            name = name.replace(acronym, f"_{acronym}_")
        return name.replace("_", "-").lower()
    else:
        return re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()


def snake_to_camel(name: str) -> str:
    return "".join(word.title() for word in name.split("_"))


def snake_to_kebab(name: str) -> str:
    return name.replace("_", "-")


def kebab_to_camel(name: str) -> str:
    return "".join(word.title() for word in name.split("-"))


def kebab_to_snake(name: str) -> str:
    return name.replace("-", "_")


def slug_to_camel(s: str) -> str:
    return "".join(word.title() for word in s.split("_"))


def slug_to_snake(s: str) -> str:
    return s.replace("-", "_")


def slug_to_kebab(s: str) -> str:
    return s.replace("_", "-")


def detect_string_type(
    string: str,
) -> typing.Literal[
    "url-image",
    "url-video",
    "url",
    "uuid",
    "base64-encoded-string",
    "email-address",
    "html",
    "domain-name",
    "phone-number",
    "json-string",
    "javascript-snippet",
    "date-string",
    "timestamp-string",
    "unknown",
]:
    # Check for URLs
    if re.match(r"^https?://", string):
        if re.match(r"\.(jpeg|jpg|png|gif|bmp)$", string):
            return "url-image"
        elif re.match(r"\.(mp4|webm|ogv)$", string):
            return "url-video"
        else:
            return "url"

    # Check for UUIDs
    if RE_UUID.match(string):
        return "uuid"

    # # Check for base64-encoded strings
    try:
        if base64.b64encode(base64.b64decode(string)) == string:
            return "base64-encoded-string"
    except Exception:
        pass
    # if re.match(r'^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$', string):
    #   return 'base64-encoded-string'

    # Check for email addresses
    if RE_EMAIL.match(string):
        return "email-address"

    if RE_HTML.match(string):
        return "html"

    # Check for domain names
    if RE_DOMAIN_NAMES.match(string):
        return "domain-name"

    # Check for phone numbers
    if RE_PHONE_NUMBER.match(string):
        return "phone-number"

    # Check for JSON strings
    try:
        orjson.loads(string)
        return "json-string"
    except ValueError:
        pass

    # Check for JavaScript snippets
    if RE_JAVASCRIPT.match(string):
        return "javascript-snippet"

    # Check for date and timestamp strings
    try:
        datetime.datetime.strptime(string, "%Y-%m-%d")
        return "date-string"
    except ValueError:
        pass
    try:
        parse_timestamp(string, raise_error=True)
        return "timestamp-string"
    except Exception:
        pass

    return "unknown"


# models
def encode_base32(n):
    """
    Encode a 64-bit integer into a Base32 string.
    Uses the RFC4648 alphabet: A-Z, 2-7
    """
    if not 0 <= n < (1 << 64):
        raise ValueError("Input must be a 64-bit unsigned integer")

    # RFC4648 Base32 alphabet (A-Z, 2-7)
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

    # Convert to base32 string
    result = ""
    while n:
        n, remainder = divmod(n, 32)
        result = alphabet[remainder] + result

    # Handle zero case
    if not result:
        return "A"

    # Left pad with 'A' to ensure consistent 13-character length
    return result.rjust(13, "A")
