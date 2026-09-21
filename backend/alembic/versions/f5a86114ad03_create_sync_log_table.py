"""create sync_log table

Revision ID: f5a86114ad03
Revises: c12a80474cec
Create Date: 2026-09-20 23:40:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
import sqlmodel.sql.sqltypes

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f5a86114ad03"
down_revision: str | Sequence[str] | None = "c12a80474cec"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sync_log",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=False),
        sa.Column("counts_json", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="app",
    )


def downgrade() -> None:
    op.drop_table("sync_log", schema="app")
