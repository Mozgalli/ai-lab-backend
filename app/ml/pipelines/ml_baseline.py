"""ML Branch için sklearn tabanlı eğitim pipeline'ı (gerçek).

Özellikler:
- Built-in dataset: iris|wine|breast_cancer|digits
- CSV dataset: csv_path + target_col
- CSV doğrulama: target_col var mı, target'ta null var mı, en az 1 feature var mı
- Preprocess:
  - numeric: median impute + (opsiyon) StandardScaler
  - categorical: most_frequent impute + OneHotEncoder
- Model:
  - Logistic Regression (Pipeline)
  - Random Forest
- Metrics: accuracy, f1/precision/recall macro + confusion matrix
- Opsiyonel: modeli joblib ile kaydetme (registry)

Param örnekleri:
{
  "dataset": {"name": "iris"},
  "model": {"name": "logreg", "C": 1.0, "max_iter": 500},
  "split": {"test_size": 0.2, "random_state": 42, "stratify": true},
  "preprocess": {"scale_numeric": true, "onehot": true},
  "artifacts": {"save_model": true}
}

CSV ile:
{
  "dataset": {"csv_path": "/app/app/ml/datasets/uploads/data.csv", "target_col": "label"},
  "model": {"name": "rf", "n_estimators": 300},
  "preprocess": {"onehot": true},
  "artifacts": {"save_model": true}
}
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Tuple, Optional

import numpy as np
import pandas as pd

from sklearn.datasets import load_iris, load_wine, load_breast_cancer, load_digits
from sklearn.model_selection import train_test_split

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix,
)

import joblib
import os

REGISTRY_DIR = "/app/app/ml/registry"

@dataclass
class BaselineResult:
    metrics: dict[str, Any]

def _load_builtin(name: str) -> Tuple[np.ndarray, np.ndarray, Optional[list[str]]]:
    name = name.lower().strip()
    if name == "iris":
        ds = load_iris()
    elif name == "wine":
        ds = load_wine()
    elif name in ("breast_cancer", "cancer"):
        ds = load_breast_cancer()
    elif name == "digits":
        ds = load_digits()
    else:
        raise ValueError(f"unknown builtin dataset: {name}")
    X = ds.data
    y = ds.target
    feature_names = list(getattr(ds, "feature_names", [])) or None
    return X, y, feature_names

def _load_csv_df(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        raise ValueError(f"csv_path not found: {csv_path}")
    # default read; advanced settings can go to meta_json later
    return pd.read_csv(csv_path)

def _validate_tabular(df: pd.DataFrame, target_col: str) -> None:
    if target_col not in df.columns:
        raise ValueError(f"target_col '{target_col}' not found. columns={list(df.columns)}")
    if df[target_col].isna().any():
        raise ValueError("target column contains null/NaN values. Clean or fill them before training.")
    if len(df.columns) <= 1:
        raise ValueError("dataset must contain at least 1 feature column besides target_col")

def _build_preprocessor(df: pd.DataFrame, target_col: str, preprocess_cfg: dict[str, Any]) -> tuple[ColumnTransformer, list[str], list[str]]:
    onehot = bool(preprocess_cfg.get("onehot", True))
    scale_numeric = bool(preprocess_cfg.get("scale_numeric", True))

    X_df = df.drop(columns=[target_col])

    # detect column types
    numeric_cols = list(X_df.select_dtypes(include=["number"]).columns)
    categorical_cols = [c for c in X_df.columns if c not in numeric_cols]

    # numeric pipeline
    num_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        num_steps.append(("scaler", StandardScaler()))
    num_pipe = Pipeline(steps=num_steps)

    # categorical pipeline
    if onehot and categorical_cols:
        cat_pipe = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore")),
            ]
        )
    else:
        # if we don't onehot, drop categoricals (baseline choice)
        cat_pipe = "drop"

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipe, numeric_cols),
            ("cat", cat_pipe, categorical_cols),
        ],
        remainder="drop",
    )
    return preprocessor, numeric_cols, categorical_cols

def _build_model(model_cfg: dict[str, Any]) -> Any:
    name = (model_cfg.get("name") or "logreg").lower().strip()
    if name in ("logreg", "logistic", "logistic_regression"):
        C = float(model_cfg.get("C", 1.0))
        max_iter = int(model_cfg.get("max_iter", 500))
        solver = model_cfg.get("solver", "lbfgs")
        return LogisticRegression(C=C, max_iter=max_iter, solver=solver)
    if name in ("rf", "random_forest", "randomforest"):
        n_estimators = int(model_cfg.get("n_estimators", 200))
        random_state = model_cfg.get("random_state", 42)
        max_depth = model_cfg.get("max_depth", None)
        return RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            max_depth=max_depth,
            n_jobs=-1,
        )
    raise ValueError(f"unknown model name: {name}")

def run_baseline(params: dict[str, Any], run_id: str | None = None) -> BaselineResult:
    dataset_cfg = params.get("dataset") or {"name": "iris"}
    model_cfg = params.get("model") or {"name": "logreg"}
    split_cfg = params.get("split") or {}
    preprocess_cfg = params.get("preprocess") or {"scale_numeric": True, "onehot": True}
    artifacts_cfg = params.get("artifacts") or {"save_model": False}

    # dataset
    feature_names = None
    dataset_name = None
    is_csv = False

    if "csv_path" in dataset_cfg:
        is_csv = True
        csv_path = dataset_cfg["csv_path"]
        target_col = dataset_cfg.get("target_col") or "target"
        df = _load_csv_df(csv_path)
        _validate_tabular(df, target_col)

        y = df[target_col].values
        dataset_name = f"csv:{csv_path}"

        preprocessor, numeric_cols, categorical_cols = _build_preprocessor(df, target_col, preprocess_cfg)
        clf = _build_model(model_cfg)
        model = Pipeline(steps=[("preprocess", preprocessor), ("clf", clf)])

        X = df.drop(columns=[target_col])
        n_features_raw = int(X.shape[1])
    else:
        builtin = dataset_cfg.get("name", "iris")
        X_arr, y, feature_names = _load_builtin(builtin)
        dataset_name = f"builtin:{builtin}"
        n_features_raw = int(X_arr.shape[1])

        # builtins are numeric arrays; simple pipeline
        clf = _build_model(model_cfg)
        # for logreg, scaling helps
        if model_cfg.get("name","logreg").lower().startswith("log"):
            model = Pipeline([("scaler", StandardScaler()), ("clf", clf)])
        else:
            model = clf
        X = X_arr

    # split
    test_size = float(split_cfg.get("test_size", 0.2))
    random_state = int(split_cfg.get("random_state", 42))
    stratify = split_cfg.get("stratify", True)
    stratify_y = y if stratify else None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify_y
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    average = "macro"
    metrics = {
        "dataset": dataset_name,
        "n_samples": int(len(y)),
        "n_features_raw": n_features_raw,
        "test_size": test_size,
        "model": model_cfg,
        "preprocess": preprocess_cfg,
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "f1_macro": float(f1_score(y_test, y_pred, average=average)),
        "precision_macro": float(precision_score(y_test, y_pred, average=average, zero_division=0)),
        "recall_macro": float(recall_score(y_test, y_pred, average=average, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "feature_names": feature_names,
    }

    # save model artifact
    if artifacts_cfg.get("save_model") and run_id:
        os.makedirs(REGISTRY_DIR, exist_ok=True)
        model_path = os.path.join(REGISTRY_DIR, f"{run_id}.joblib")
        joblib.dump(model, model_path)
        metrics["artifacts"] = {"model_path": model_path}

    return BaselineResult(metrics=metrics)
