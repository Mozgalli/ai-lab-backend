# AI LAB Backend
![CI](https://github.com/<kullanici>/<repo>/actions/workflows/ci.yml/badge.svg)

**FastAPI + PostgreSQL + Alembic + sklearn ML baseline + Dataset Upload + Preprocess + RQ (Redis) Worker**

Bu repo, yapay zekânın kollarını (ML/NLP/CV/LLM…) **proje bazlı** ilerletebilmek için “deney takip” odaklı bir backend çekirdeğidir.  
Şu anki odak: **Makine Öğrenmesi (ML)** için uçtan uca baseline (dataset → train → metrics → artifact).

---

## Özellikler
- ✅ **FastAPI** REST API + Swagger
- ✅ **PostgreSQL** + **SQLAlchemy**
- ✅ **Alembic** migration
- ✅ Deney organizasyonu: **Project → Experiment → Run**
- ✅ **Dataset Upload (CSV)**: dosyayı kaydet + DB kaydı aç
- ✅ **ML Baseline (sklearn)**:
  - Built-in dataset: `iris`, `wine`, `breast_cancer`, `digits`
  - CSV dataset: `csv_path` + `target_col`
- ✅ **Preprocess (Tabular)**:
  - Numeric: impute (median) + (opsiyon) scaling
  - Categorical: impute (most_frequent) + OneHotEncoder
- ✅ **Metrics**:
  - accuracy, f1_macro, precision_macro, recall_macro, confusion_matrix
- ✅ **Background Training**: RQ + Redis worker (async training)
- ✅ **Model Artifact**: `joblib` ile `/app/app/ml/registry/{run_id}.joblib`

---

## Mimari
- `app/api/v1` → API endpoints  
- `app/models` → DB modelleri  
- `app/services` → iş servisleri (job enqueue, train job)  
- `app/ml/pipelines` → ML pipeline’lar  
- `app/ml/datasets/uploads` → yüklenen dataset dosyaları  
- `app/ml/registry` → model artifact’leri  

---

## Hızlı Başlangıç (Docker)
```bash
cp .env.example .env
docker compose up --build
docker compose exec api alembic upgrade head
