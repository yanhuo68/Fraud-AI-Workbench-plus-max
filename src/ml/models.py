# ml/models.py
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    precision_recall_curve,
    roc_curve,
    confusion_matrix,
)
import numpy as np
import logging

logger = logging.getLogger(__name__)

def train_isolation_forest(
    X_train,
    contamination: float = 0.02,
    n_estimators: int = 200,
    **kwargs,
):
    logger.info("Training IsolationForest...")
    iso = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=42,
        n_jobs=-1,
        **kwargs,
    )
    iso.fit(X_train)
    return iso

def predict_iforest_scores(model: IsolationForest, X):
    # Higher score -> more normal; convert to anomaly score
    scores = -model.score_samples(X)
    return scores

def train_random_forest(
    X_train,
    y_train,
    n_estimators: int = 300,
    max_depth=None,
    **kwargs,
):
    logger.info("Training RandomForestClassifier...")
    rf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        n_jobs=-1,
        random_state=42,
        class_weight="balanced_subsample",
        **kwargs,
    )
    rf.fit(X_train, y_train)
    return rf

def evaluate_classifier(model, X, y, threshold: float = 0.5):
    y_prob = model.predict_proba(X)[:, 1]
    y_pred = (y_prob >= threshold).astype(int)
    report = classification_report(y, y_pred, output_dict=True)
    auc = roc_auc_score(y, y_prob)
    cm = confusion_matrix(y, y_pred)
    precision, recall, pr_thresh = precision_recall_curve(y, y_prob)
    fpr, tpr, roc_thresh = roc_curve(y, y_prob)
    logger.info(f"Classifier AUC={auc:.4f}")
    return {
        "report": report,
        "auc": auc,
        "y_prob": y_prob,
        "y_pred": y_pred,
        "cm": cm,
        "precision": precision,
        "recall": recall,
        "pr_thresholds": pr_thresh,
        "fpr": fpr,
        "tpr": tpr,
        "roc_thresholds": roc_thresh,
    }
