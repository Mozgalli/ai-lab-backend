from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.project import Project, Experiment, Run, RunStatus

def list_projects(db: Session) -> list[Project]:
    return list(db.scalars(select(Project).order_by(Project.created_at.desc())).all())

def create_project(db: Session, *, name: str, slug: str, branch, description: str | None):
    p = Project(name=name, slug=slug, branch=branch, description=description)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def create_experiment(db: Session, *, project_id, name: str, note: str | None):
    e = Experiment(project_id=project_id, name=name, note=note)
    db.add(e)
    db.commit()
    db.refresh(e)
    return e

def create_run(db: Session, *, experiment_id, name: str, params_json: str | None):
    r = Run(experiment_id=experiment_id, name=name, params_json=params_json, status=RunStatus.QUEUED)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

def update_run_status(db: Session, run: Run, status: RunStatus, metrics_json: str | None = None, error: str | None = None):
    run.status = status
    if metrics_json is not None:
        run.metrics_json = metrics_json
    if error is not None:
        run.error = error
    db.add(run)
    db.commit()
    db.refresh(run)
    return run
