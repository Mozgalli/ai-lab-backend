from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
import json

from app.db.deps import get_db
from app.schemas.project import RunCreate, RunOut
from app.models.project import Run, Experiment, RunStatus
from app.models.dataset import Dataset
from app.services.projects import create_run, update_run_status
from app.services.jobs import enqueue_training
from app.ml.pipelines.ml_baseline import run_baseline

router = APIRouter()

@router.post("", response_model=RunOut, status_code=201)
def post_run(payload: RunCreate, db: Session = Depends(get_db)):
    exp = db.get(Experiment, payload.experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="experiment not found")
    return create_run(db, experiment_id=payload.experiment_id, name=payload.name, params_json=payload.params_json)

@router.get("", response_model=list[RunOut])
def list_runs(experiment_id: str | None = None, db: Session = Depends(get_db)):
    q = select(Run).order_by(Run.created_at.desc())
    if experiment_id:
        q = q.where(Run.experiment_id == experiment_id)
    return list(db.scalars(q).all())

@router.post("/{run_id}/enqueue", response_model=dict)
def enqueue_run(run_id: str, db: Session = Depends(get_db)):
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    if run.status not in (RunStatus.QUEUED, RunStatus.FAILED):
        raise HTTPException(status_code=400, detail=f"cannot enqueue run in status {run.status}")
    job_id = enqueue_training(run_id)
    return {"enqueued": True, "job_id": job_id}

@router.post("/{run_id}/start", response_model=dict)
def start_run(run_id: str, db: Session = Depends(get_db)):
    """Default: arka plan (RQ) ile başlatır."""
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    if run.status not in (RunStatus.QUEUED, RunStatus.FAILED):
        raise HTTPException(status_code=400, detail=f"cannot start run in status {run.status}")
    job_id = enqueue_training(run_id)
    return {"started": True, "mode": "async", "job_id": job_id}

@router.post("/{run_id}/start_sync", response_model=RunOut)
def start_run_sync(run_id: str, db: Session = Depends(get_db)):
    """Geliştirme için: aynı request içinde çalıştırır."""
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    if run.status not in (RunStatus.QUEUED, RunStatus.FAILED):
        raise HTTPException(status_code=400, detail=f"cannot start run in status {run.status}")

    try:
        update_run_status(db, run, RunStatus.RUNNING)
        params = json.loads(run.params_json) if run.params_json else {}

        ds_id = params.get("dataset_id")
        if ds_id:
            ds = db.get(Dataset, ds_id)
            if not ds:
                raise ValueError(f"dataset not found: {ds_id}")
            dataset_cfg = params.get("dataset") or {}
            dataset_cfg.setdefault("csv_path", ds.uri)
            if ds.target_col:
                dataset_cfg.setdefault("target_col", ds.target_col)
            params["dataset"] = dataset_cfg

        result = run_baseline(params, run_id=str(run.id))
        metrics_json = json.dumps(result.metrics, ensure_ascii=False)
        return update_run_status(db, run, RunStatus.SUCCEEDED, metrics_json=metrics_json)
    except Exception as e:
        return update_run_status(db, run, RunStatus.FAILED, error=str(e))
