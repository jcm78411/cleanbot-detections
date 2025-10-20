#!/usr/bin/env python3
# train_model.py - Entrena varios modelos ML para clasificar materiales (Pl�stico / No Pl�stico)

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
import xgboost as xgb
import joblib

# ---------------------------
# Cargar dataset
# ---------------------------
df = pd.read_csv("dataset.csv")

# Eliminar columna 'fecha' si existe
if "fecha" in df.columns:
    df = df.drop(columns=["fecha"])

# Separar variables
X = df.drop(columns=["Etiqueta"])
y = df["Etiqueta"]

# ---------------------------
# Dividir dataset
# ---------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Escalar datos
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ---------------------------
# Modelos a probar
# ---------------------------
modelos = {
    "LogisticRegression": LogisticRegression(max_iter=1000),
    "SVM": SVC(kernel="rbf", probability=True),
    "RandomForest": RandomForestClassifier(n_estimators=200, random_state=42),
    "KNN": KNeighborsClassifier(n_neighbors=5),
    "XGBoost": xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss"),
    "GradientBoosting": GradientBoostingClassifier(),
    "MLP": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=5000)
}

resultados = {}

# ---------------------------
# Entrenamiento y evaluaci�n
# ---------------------------
print("\n?? Entrenando modelos...\n")

for nombre, modelo in modelos.items():
    modelo.fit(X_train_scaled, y_train)
    y_pred = modelo.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    resultados[nombre] = acc
    print(f"{nombre}: {acc:.4f}")

# ---------------------------
# Mejor modelo
# ---------------------------
mejor_modelo = max(resultados, key=resultados.get)
print("\n? Mejor modelo:", mejor_modelo)
print(f"?? Precisi�n: {resultados[mejor_modelo]:.4f}\n")

# Reporte detallado
best_model = modelos[mejor_modelo]
y_pred = best_model.predict(X_test_scaled)
print(classification_report(y_test, y_pred))

# Guardar modelo y escalador
joblib.dump(best_model, "best_model_trained.pkl")
joblib.dump(scaler, "scaler_trained.pkl")

print("?? Modelo y escalador guardados (best_model_trained.pkl, scaler_trained.pkl)")
