# ml/data_prep.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

CATEGORICAL_COLS = ["type"]
DROP_COLS = ["nameOrig", "nameDest"]

def load_raw_data(csv_path: str | Path) -> pd.DataFrame:
    csv_path = Path(csv_path)
    logger.info(f"Loading raw data from {csv_path}")
    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {df.shape[0]} rows, {df.shape[1]} columns")
    return df

def encode_features(df: pd.DataFrame):
    """
    Convert all feature columns to numeric codes:
    - If coercible to numeric (with non-trivial non-NaN fraction), use numeric.
    - Otherwise factorize to integer codes.
    Returns encoded df, list of feature names, and scaler fitted on encoded features.
    """
    df_enc = df.copy()
    feature_names = []

    for col in df_enc.columns:
        series = df_enc[col]
        num_series = pd.to_numeric(series, errors="coerce")
        non_na_ratio = num_series.notna().mean()
        if non_na_ratio > 0.0:
            df_enc[col] = num_series.fillna(num_series.median())
        else:
            codes, _ = pd.factorize(series.astype(str), sort=True)
            df_enc[col] = codes
        feature_names.append(col)

    # Fill NaNs
    df_enc = df_enc.fillna(df_enc.median(numeric_only=True)).fillna(-1)

    scaler = StandardScaler()
    X_array = scaler.fit_transform(df_enc)
    return X_array.astype(float), scaler, feature_names


def preprocess(
    df: pd.DataFrame,
    use_smote: bool = False,
    random_state: int = 42,
    train_ratio: float = 0.6,
    val_ratio: float = 0.2,
    feature_list: list[str] | None = None,
    high_card_threshold: int = 50,
    **kwargs,
):
    """Encode, drop IDs, scale numerics, split X/y."""
    df = df.copy()

    for col in DROP_COLS:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # Target
    target_col = "isFraud"
    if "isFraud" not in df.columns and "Fraudulent" in df.columns:
        target_col = "Fraudulent"
    
    if target_col not in df.columns:
        # Fallback: try to find a column that looks like a target
        possible = [c for c in df.columns if "fraud" in c.lower()]
        if possible:
            target_col = possible[0]
        else:
            raise KeyError("Could not find label column 'isFraud' or 'Fraudulent'")

    y = df[target_col].astype(int)
    X = df.drop(columns=[target_col])

    if feature_list:
        X = X[[c for c in feature_list if c in X.columns]]
    else:
        # Drop very high-card categorical columns by default
        high_card_cols = [
            c for c in X.columns
            if (not pd.api.types.is_numeric_dtype(X[c])) and X[c].nunique() > high_card_threshold
        ]
        if high_card_cols:
            X = X.drop(columns=high_card_cols)

    try:
        X_array, scaler, feature_names = encode_features(X)
    except Exception as e:
        logger.warning(f"Feature encoding failed ({e}); falling back to categorical factorization.")
        # Factorize all columns to codes
        X_fact = pd.DataFrame({c: pd.factorize(X[c].astype(str), sort=True)[0] for c in X.columns})
        scaler = StandardScaler()
        X_array = scaler.fit_transform(X_fact).astype(float)
        feature_names = X_fact.columns.tolist()
    else:
        # Ensure no NaNs remain
        X_array = np.nan_to_num(X_array, nan=0.0)

    # compute test ratio
    test_ratio = max(0.0, min(0.99, 1.0 - train_ratio - val_ratio))
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X_array, y, test_size=test_ratio, random_state=random_state, stratify=y
    )
    # avoid zero division if val_ratio == 0
    val_ratio_adj = val_ratio / (train_ratio + val_ratio) if (train_ratio + val_ratio) > 0 else 0.0
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval, y_trainval, test_size=val_ratio_adj, random_state=random_state, stratify=y_trainval
    )

    if use_smote:
        try:
            from imblearn.over_sampling import SMOTE  # type: ignore
        except Exception:
            logger.warning("SMOTE not available; proceeding without resampling.")
        else:
            smote = SMOTE(random_state=random_state)
            X_train, y_train = smote.fit_resample(X_train, y_train)

    return (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
        scaler,
        feature_names,
    )
