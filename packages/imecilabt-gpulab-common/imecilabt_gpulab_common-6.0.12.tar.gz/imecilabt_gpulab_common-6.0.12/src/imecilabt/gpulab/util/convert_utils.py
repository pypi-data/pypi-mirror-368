"""Conversion utils."""

from imecilabt_utils.urn_util import URN, always_optional_urn

AUTHORITY_MINI_IDS = {
    "wall2.ilabt.iminds.be": "w2",
    "ilabt.imec.be": "ilabt",
    "example.com": "ex",  # used in tests
}


def urn_to_user_mini_id(urn: str | URN | None) -> str | None:
    """URN to mini id."""

    u = always_optional_urn(urn) if urn else None

    if not u or not u.authority or not u.name:
        return None

    return f"{u.name}@{AUTHORITY_MINI_IDS.get(u.authority,u.authority)}"


def urn_to_auth(urn: str | URN | None) -> str | None:
    """URN to authority."""
    u = always_optional_urn(urn) if urn else None
    if u and u.authority:
        return u.authority
    return None


def urn_to_name(urn: str | URN | None) -> str | None:
    """URN to authority."""

    u = always_optional_urn(urn) if urn else None
    if u and u.name:
        return u.name

    return None


def extract_exception_message(e: Exception):
    """Try to extract the "message" of an exception.

    (usually str(e) is enough, but this is meant to handle some edge cases as well.)
    """
    if hasattr(e, "message") and e.message:  # type: ignore
        return e.message  # type: ignore
    if hasattr(e, "msg") and e.msg:  # type: ignore
        return e.msg  # type: ignore
    res = str(e)
    if res:
        return res
    return str(type(e))
