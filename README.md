# Training Partner

Dashboard local d'entraînement multi-sport, basé sur tes données Garmin Connect. Objectif principal : préparer un marathon (avril 2027), avec un journal d'entraînement et des recommandations basées sur ta forme réelle (training status/readiness Garmin, HRV, sommeil, volume).

## Architecture

- **Backend** (`backend/`) : FastAPI, architecture Controller (`app/api/routes`) / Service (`app/services`) / Repository (`app/infrastructure/db`, `app/infrastructure/warehouse`) / Database. Logique métier pure (calcul de phase, recommandations) isolée dans `app/domain/`. SQLModel + Alembic pour les tables propres à l'appli (journal, plan). Tooling : [uv](https://docs.astral.sh/uv/), [ruff](https://docs.astral.sh/ruff/), [ty](https://github.com/astral-sh/ty).
- **Pipeline data** (`data/`) : extraction Garmin incrémentale via [dlt](https://dlthub.com/) (`data/dlt/garmin_pipeline.py`) vers un schéma `raw`, transformation via [dbt](https://www.getdbt.com/) (`data/dbt/`) en `staging`/`marts`, le tout dans un seul fichier [DuckDB](https://duckdb.org/) : `data/warehouse.duckdb`.
- **Frontend** (`frontend/`) : React + Vite + TypeScript + Recharts. La page Dashboard déclenche un refresh (`POST /api/sync/refresh` → dlt puis dbt) à chaque ouverture.

## Setup (première fois)

1. **Backend** :
   ```bash
   cd backend
   uv sync
   cp .env.example .env   # puis renseigne GARMIN_EMAIL / GARMIN_PASSWORD
   ```
2. **Login Garmin** (une seule fois, gère un éventuel MFA) :
   ```bash
   uv run --directory backend python scripts/garmin_login.py
   ```
3. **Frontend** :
   ```bash
   cd frontend
   npm install
   ```

## Lancer en dev

Terminal 1 — backend (applique les migrations, démarre l'API, ouvre le navigateur) :
```bash
python dashboard.py
```

Terminal 2 — frontend (proxy Vite → API sur `localhost:8000`) :
```bash
cd frontend && npm run dev
```

Le Dashboard (`http://localhost:5173`) déclenche automatiquement un refresh des données au chargement. L'API est documentée sur `http://localhost:8000/docs`.

## Vérifications / CI

```bash
cd backend && uv run ruff check . && uv run ty check && uv run pytest
cd frontend && npm run lint && npm run build
```

La CI GitHub Actions (`.github/workflows/ci.yml`) lance ces mêmes vérifications sur chaque PR, plus `dbt parse` sur le projet data.

## Workflow Git

GitFlow : `main` (stable) / `develop` (intégration) / `feature/*` (branché sur `develop`, PR vers `develop`). Voir le plan d'origine dans `/Users/ludoviccarlu/.claude/plans/encapsulated-tumbling-reddy.md` pour le détail des décisions d'architecture.
