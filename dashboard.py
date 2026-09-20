#!/usr/bin/env python3
"""Training Partner — launcher.

Lance le backend FastAPI (applique les migrations Alembic des tables
app-owned, puis démarre uvicorn) et ouvre le navigateur sur le dashboard.

Usage : `python dashboard.py` (ou `uv run python dashboard.py` depuis la racine).
Le frontend (Vite) doit être lancé séparément en dev : `cd frontend && npm run dev`.
"""

from __future__ import annotations

import subprocess
import sys
import webbrowser
from pathlib import Path
from threading import Timer

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:8000"


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=BACKEND_DIR, check=True, **kwargs)


def check_env_file() -> None:
    env_path = BACKEND_DIR / ".env"
    if not env_path.exists():
        print(
            f"[!] {env_path} est introuvable.\n"
            f"    Copie {BACKEND_DIR / '.env.example'} vers {env_path} et renseigne tes "
            "identifiants Garmin avant de continuer.\n"
        )
        sys.exit(1)


def apply_migrations() -> None:
    print("Application des migrations Alembic (tables app-owned)...")
    run(["uv", "run", "alembic", "upgrade", "head"])


def open_browser_later(delay_s: float = 1.5) -> None:
    def _open() -> None:
        print(f"Ouverture du navigateur sur {FRONTEND_URL}")
        print(
            f"(si rien ne s'affiche : lance le frontend dans un autre terminal avec "
            f"`cd frontend && npm run dev` — API backend dispo sur {BACKEND_URL}/docs)"
        )
        webbrowser.open(FRONTEND_URL)

    Timer(delay_s, _open).start()


def start_backend() -> None:
    print(f"Démarrage du backend FastAPI sur {BACKEND_URL} ...")
    open_browser_later()
    subprocess.run(
        [
            "uv",
            "run",
            "uvicorn",
            "app.main:app",
            "--reload",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ],
        cwd=BACKEND_DIR,
        check=True,
    )


def main() -> None:
    check_env_file()
    apply_migrations()
    start_backend()


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"\n[!] Échec de la commande : {exc}")
        sys.exit(exc.returncode)
    except KeyboardInterrupt:
        print("\nArrêt.")
