from __future__ import annotations

import json
import os

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.project import Run, RunStatus
from app.models.dataset import Dataset
from app.services.projects import update_run_status
from app.ml.pipelines.ml_baseline import run_baseline

def execute_train_job(run_id: str) -> None:
    """Worker içinde çalışır.

    - Run status: RUNNING -> SUCCEEDED/FAILED
    - dataset_id shortcut çözümü
    """
    db: Session = SessionLocal()
    try:
        run = db.get(Run, run_id)
        if not run:
            return

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
        update_run_status(db, run, RunStatus.SUCCEEDED, metrics_json=metrics_json)
    except Exception as e:
        run = db.get(Run, run_id)
        if run:
            update_run_status(db, run, RunStatus.FAILED, error=str(e))
    finally:
        db.close()
