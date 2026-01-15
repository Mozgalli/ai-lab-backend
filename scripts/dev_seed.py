"""Local geliştirme için örnek veri basar."""
import json
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.projects import create_project, create_experiment, create_run
from app.models.project import AIBranch

def main():
    db: Session = SessionLocal()
    p = create_project(db, name="ML - Baseline", slug="ml-baseline", branch=AIBranch.ML, description="İlk ML projesi")
    e = create_experiment(db, project_id=p.id, name="E1: Logistic Regression", note="iris + logreg")
    params = {
        "dataset": {"name": "iris"},
        "model": {"name": "logreg", "C": 1.0, "max_iter": 500},
        "split": {"test_size": 0.2, "random_state": 42, "stratify": True},
    }
    create_run(db, experiment_id=e.id, name="Run-001", params_json=json.dumps(params))
    print("seed ok:", p.id)

if __name__ == "__main__":
    main()
