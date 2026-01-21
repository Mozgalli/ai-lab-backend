"""init

Revision ID: 0001_init
Revises: 
Create Date: 2026-01-15

"""
from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Enum types
    conn = op.get_bind()
    conn.execute(sa.text("CREATE TYPE aibranch AS ENUM ('ML','DL','NLP','LLM','CV','SPEECH','ROBOTICS','EXPERT','EVO','ETHICS')"))
    conn.execute(sa.text("CREATE TYPE runstatus AS ENUM ('QUEUED','RUNNING','SUCCEEDED','FAILED','CANCELED')"))

    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("branch", sa.String(length=20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_index("uq_projects_slug", "projects", ["slug"], unique=True)
    # Add CHECK constraint for branch enum
    op.execute(sa.text("ALTER TABLE projects ADD CONSTRAINT ck_projects_branch CHECK (branch::text = ANY (ARRAY['ML'::text, 'DL'::text, 'NLP'::text, 'LLM'::text, 'CV'::text, 'SPEECH'::text, 'ROBOTICS'::text, 'EXPERT'::text, 'EVO'::text, 'ETHICS'::text]))"))

    op.create_table(
        "experiments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("project_id", sa.Uuid(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
    )

    op.create_table(
        "runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("experiment_id", sa.Uuid(), sa.ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("params_json", sa.Text(), nullable=True),
        sa.Column("metrics_json", sa.Text(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
    )
    # Add CHECK constraint for status enum
    op.execute(sa.text("ALTER TABLE runs ADD CONSTRAINT ck_runs_status CHECK (status::text = ANY (ARRAY['QUEUED'::text, 'RUNNING'::text, 'SUCCEEDED'::text, 'FAILED'::text, 'CANCELED'::text]))"))

    op.create_table(
        "datasets",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("project_id", sa.Uuid(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("kind", sa.String(length=50), nullable=False, server_default="tabular"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("uri", sa.String(length=500), nullable=False),
    )

def downgrade():
    op.drop_table("datasets")
    op.execute(sa.text("ALTER TABLE runs DROP CONSTRAINT IF EXISTS ck_runs_status"))
    op.drop_table("runs")
    op.drop_table("experiments")
    op.execute(sa.text("ALTER TABLE projects DROP CONSTRAINT IF EXISTS ck_projects_branch"))
    op.drop_index("uq_projects_slug", table_name="projects")
    op.drop_table("projects")
    op.execute(sa.text("DROP TYPE IF EXISTS runstatus"))
    op.execute(sa.text("DROP TYPE IF EXISTS aibranch"))
