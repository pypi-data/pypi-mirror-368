"""
Machine Learning Models for Genomic Data
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

def extract_features(sequences):
    """Extract numeric features from DNA sequences for ML (GC content, length, etc)."""
    features = []
    for seq in sequences:
        gc = sum(1 for base in seq.upper() if base in ["G", "C"])
        length = len(seq)
        features.append([gc / length if length else 0, length])
    return np.array(features)

def to_dataframe(features, labels=None):
    """Convert features (and optional labels) to pandas DataFrame."""
    df = pd.DataFrame(features, columns=["gc_content", "length"])
    if labels is not None:
        df["label"] = labels
    return df

def train_classifier(X, y):
    """Train and evaluate a RandomForest classifier."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    clf = RandomForestClassifier()
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)
    report = classification_report(y_test, preds)
    return clf, acc, report

def save_model(model, path):
    """Save trained model to disk."""
    joblib.dump(model, path)

def load_model(path):
    """Load trained model from disk."""
    return joblib.load(path)
