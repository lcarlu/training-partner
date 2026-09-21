#!/usr/bin/env python
"""One-shot interactive Garmin Connect login.

Run this by hand once (and again whenever the refresh token expires):

    uv run --directory backend python scripts/garmin_login.py

It logs in with GARMIN_EMAIL/GARMIN_PASSWORD from backend/.env, prompting for an MFA code on
stdin if your account has two-factor auth enabled, and caches the resulting tokens in
GARMIN_TOKEN_STORE. The backend and the dlt pipeline then reuse those cached tokens without
any further interaction.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from garminconnect import Garmin  # noqa: E402

from app.core.config import get_settings  # noqa: E402


def prompt_mfa() -> str:
    return input("Code MFA Garmin Connect : ").strip()


def main() -> int:
    settings = get_settings()

    if not settings.garmin_email or not settings.garmin_password:
        print(
            "GARMIN_EMAIL / GARMIN_PASSWORD manquants dans backend/.env "
            "(copie backend/.env.example)."
        )
        return 1

    token_store = str(Path(settings.garmin_token_store).expanduser())
    client = Garmin(
        email=settings.garmin_email,
        password=settings.garmin_password,
        prompt_mfa=prompt_mfa,
    )
    client.login(token_store)
    print(f"Connecté à Garmin Connect en tant que {client.get_full_name()}.")
    print(f"Tokens mis en cache dans {token_store}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
