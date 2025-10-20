#!/usr/bin/env python3
# train_model.py — Entrena múltiples modelos con dataset.csv (Plástico / NoPlástico)
# Autor: Juan Luis Cueto Morelo

import os
import warnings
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier, ExtraTreesClassifier,
    GradientBoostingClassifier, AdaBoostClassifier
)
from sklearn.neural_network import MLPClassifier

warnings.filterwarnings("ignore")

# ---------------------------
# Configuración
# ---------------------------
CSV_FILE = "dataset.csv"
MODELS_DIR = "models"
BEST_MODEL_FILE = "best_model.pkl"
RANDOM_STATE = 42
CV_FOLDS = 5

os.makedirs(MODELS_DIR, exist_ok=True)

# ---------------------------
# Cargar dataset
# ---------------------------
if not os.path.exists(CSV_FILE):
    raise SystemExit(f"❌ No se encontró el archivo {CSV_FILE}")

df = pd.read_csv(CSV_FILE)

# Features esperadas
features = [
    "R", "G", "B", "Intensidad",
    "R_norm", "G_norm", "B_norm",
    "RG_ratio", "RB_ratio", "BG_ratio"
]

# Validar columnas
for f in features + ["Etiqueta"]:
    if f not in df.columns:
        raise SystemExit(f"❌ Falta la columna '{f}' en dataset.csv")

# Separar X e y
X = df[features]
y = df["Etiqueta"].astype(int)

print(f"✅ Dataset cargado correctamente ({len(X)} muestras)")
print(f"   - Features: {features}")
print(f"   - Positivos (Plástico): {y.sum()} | Negativos: {len(y)-y.sum()}")

# ---------------------------
# División train/test
# ---------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
)

# ---------------------------
# Modelos a entrenar
# ---------------------------
models = {
    "LogisticRegression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE),
    "KNN": KNeighborsClassifier(n_neighbors=5),
    "SVM_rbf": SVC(probability=True, kernel="rbf", class_weight="balanced", random_state=RANDOM_STATE),
    "DecisionTree": DecisionTreeClassifier(class_weight="balanced", random_state=RANDOM_STATE),
    "RandomForest": RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=RANDOM_STATE),
    "ExtraTrees": ExtraTreesClassifier(n_estimators=200, class_weight="balanced", random_state=RANDOM_STATE),
    "GradientBoosting": GradientBoostingClassifier(n_estimators=200, random_state=RANDOM_STATE),
    "AdaBoost": AdaBoostClassifier(n_estimators=200, random_state=RANDOM_STATE),
    "MLP": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=RANDOM_STATE),
}

# ---------------------------
# Entrenamiento y evaluación
# ---------------------------
results = []
skf = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

for name, clf in models.items():
    print(f"\n🚀 Entrenando modelo: {name}")
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", clf)
    ])

    try:
        scores = cross_val_score(pipeline, X_train, y_train, cv=skf, scoring="accuracy", n_jobs=-1)
        cv_mean = scores.mean()

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_proba = None
        try:
            y_proba = pipeline.predict_proba(X_test)[:, 1]
        except Exception:
            pass

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc = roc_auc_score(y_test, y_proba) if y_proba is not None else np.nan

        print(f"   ✔️  Accuracy: {acc:.4f} | F1: {f1:.4f} | Precision: {prec:.4f} | Recall: {rec:.4f} | AUC: {auc:.4f}")

        model_path = os.path.join(MODELS_DIR, f"{name}.pkl")
        joblib.dump(pipeline, model_path)

        results.append({
            "Modelo": name,
            "CV_mean": cv_mean,
            "Test_acc": acc,
            "Precision": prec,
            "Recall": rec,
            "F1": f1,
            "AUC": auc,
            "Ruta": model_path
        })

    except Exception as e:
        print(f"   ⚠️  Error entrenando {name}: {e}")

# ---------------------------
# Seleccionar mejor modelo
# ---------------------------
if not results:
    raise SystemExit("❌ No se logró entrenar ningún modelo correctamente.")

results_df = pd.DataFrame(results)
results_df = results_df.sort_values(by=["F1", "AUC"], ascending=False).reset_index(drop=True)

best = results_df.iloc[0]
print("\n🏆 Mejor modelo:", best["Modelo"])
print(results_df)

# Guardar mejor modelo
best_model = joblib.load(best["Ruta"])
joblib.dump(best_model, BEST_MODEL_FILE)

print(f"\n✅ Modelo guardado como {BEST_MODEL_FILE}")

# Evaluación final
y_pred_best = best_model.predict(X_test)
print("\n📊 Matriz de confusión del mejor modelo:")
print(confusion_matrix(y_test, y_pred_best))
print("\n📋 Reporte de clasificación:")
print(classification_report(y_test, y_pred_best, digits=4))

# Guardar resumen
results_df.to_csv(os.path.join(MODELS_DIR, "summary_results.csv"), index=False)
print("\n📁 Resultados guardados en models/summary_results.csv")
