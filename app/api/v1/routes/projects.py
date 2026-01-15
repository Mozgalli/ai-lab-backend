from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.deps import get_db
from app.schemas.project import ProjectCreate, ProjectOut, ExperimentCreate, ExperimentOut
from app.models.project import Project, Experiment
from app.services.projects import list_projects, create_project, create_experiment

router = APIRouter()

@router.get("", response_model=list[ProjectOut])
def get_projects(db: Session = Depends(get_db)):
    return list_projects(db)

@router.post("", response_model=ProjectOut, status_code=201)
def post_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    # slug unique check
    exists = db.scalar(select(Project).where(Project.slug == payload.slug))
    if exists:
        raise HTTPException(status_code=409, detail="slug already exists")
    return create_project(db, name=payload.name, slug=payload.slug, branch=payload.branch, description=payload.description)

@router.post("/experiments", response_model=ExperimentOut, status_code=201)
def post_experiment(payload: ExperimentCreate, db: Session = Depends(get_db)):
    # project exists?
    p = db.get(Project, payload.project_id)
    if not p:
        raise HTTPException(status_code=404, detail="project not found")
    return create_experiment(db, project_id=payload.project_id, name=payload.name, note=payload.note)

@router.get("/{project_id}/experiments", response_model=list[ExperimentOut])
def list_experiments(project_id: str, db: Session = Depends(get_db)):
    exps = db.scalars(select(Experiment).where(Experiment.project_id == project_id).order_by(Experiment.created_at.desc())).all()
    return list(exps)
