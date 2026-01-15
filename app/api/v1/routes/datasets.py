from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import select
import os
import uuid as uuidlib

from app.db.deps import get_db
from app.schemas.dataset import DatasetCreate, DatasetOut
from app.models.dataset import Dataset
from app.models.project import Project

router = APIRouter()

UPLOAD_DIR = "/app/app/ml/datasets/uploads"

@router.post("", response_model=DatasetOut, status_code=201)
def create_dataset(payload: DatasetCreate, db: Session = Depends(get_db)):
    p = db.get(Project, payload.project_id)
    if not p:
        raise HTTPException(status_code=404, detail="project not found")
    d = Dataset(**payload.model_dump())
    db.add(d)
    db.commit()
    db.refresh(d)
    return d

@router.get("", response_model=list[DatasetOut])
def list_datasets(project_id: str | None = None, db: Session = Depends(get_db)):
    q = select(Dataset).order_by(Dataset.created_at.desc())
    if project_id:
        q = q.where(Dataset.project_id == project_id)
    return list(db.scalars(q).all())

@router.post("/upload", response_model=DatasetOut, status_code=201)
async def upload_dataset(
    project_id: str = Form(...),
    name: str = Form(...),
    kind: str = Form("tabular"),
    description: str | None = Form(None),
    target_col: str | None = Form(None),
    meta_json: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Dataset dosyası yükler ve DB'ye kaydeder.

    Şimdilik CSV odaklı (tabular). Sonraki adım: parquet, zip (images), text.
    """
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="project not found")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1].lower()
    if not ext:
        ext = ".bin"
    safe_name = f"{name.lower().replace(' ', '_')}_{uuidlib.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, safe_name)

    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    d = Dataset(
        project_id=project_id,
        name=name,
        kind=kind,
        description=description,
        uri=path,
        target_col=target_col,
        meta_json=meta_json,
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d
