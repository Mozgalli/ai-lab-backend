"""add dataset target_col and meta_json

Revision ID: 0002_add_dataset_meta
Revises: 0001_init
Create Date: 2026-01-15

"""
from alembic import op
import sqlalchemy as sa

revision = "0002_add_dataset_meta"
down_revision = "0001_init"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("datasets", sa.Column("target_col", sa.String(length=200), nullable=True))
    op.add_column("datasets", sa.Column("meta_json", sa.Text(), nullable=True))

def downgrade():
    op.drop_column("datasets", "meta_json")
    op.drop_column("datasets", "target_col")
