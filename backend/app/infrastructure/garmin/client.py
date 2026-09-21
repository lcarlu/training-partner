"""Thin wrapper around garminconnect.Garmin handling cached-token auth.

At runtime (FastAPI server / dlt pipeline) no interactive MFA prompt is possible, so
`build_client` only ever tries: 1) cached tokens in GARMIN_TOKEN_STORE, 2) a non-interactive
email/password login (works only if the account has no MFA). If both fail, it raises
`GarminAuthError` pointing at `scripts/garmin_login.py`, which supports an interactive MFA
prompt and is meant to be run once by hand to seed the token cache.
"""

from collections.abc import Callable
from pathlib import Path

from garminconnect import Garmin

from app.core.config import Settings, get_settings

LOGIN_HELP = (
    "Impossible de se connecter à Garmin Connect (ni tokens en cache valides, ni login "
    "email/mot de passe non-interactif réussi). Si ton compte a la double authentification "
    "(MFA), lance une fois `uv run --directory backend python scripts/garmin_login.py` pour "
    "un login interactif qui gère le prompt MFA, puis relance."
)


class GarminAuthError(RuntimeError):
    pass


def build_client(
    settings: Settings | None = None,
    prompt_mfa: Callable[[], str] | None = None,
) -> Garmin:
    settings = settings or get_settings()
    token_store = str(Path(settings.garmin_token_store).expanduser())

    client = Garmin(
        email=settings.garmin_email or None,
        password=settings.garmin_password or None,
        prompt_mfa=prompt_mfa,
    )
    try:
        client.login(token_store)
    except Exception as exc:
        raise GarminAuthError(LOGIN_HELP) from exc
    return client
