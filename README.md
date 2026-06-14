<div align="center">

# ♻️ CleanBot Detections

### Sistema inteligente de clasificación automática de residuos mediante Machine Learning e IoT

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-IoT-red)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-green)
![Flask](https://img.shields.io/badge/Flask-REST_API-black)
![Estado](https://img.shields.io/badge/Estado-Finalizado-success)

*Plataforma inteligente desarrollada para identificar materiales reciclables mediante sensores de color, clasificarlos utilizando modelos de Machine Learning y automatizar su separación física mediante actuadores controlados por Raspberry Pi.*

</div>

---

## 📋 Tabla de Contenido

- [📖 Descripción](#-descripción)
- [✨ Características](#-características)
- [🛠️ Tecnologías Utilizadas](#️-tecnologías-utilizadas)
- [🏗️ Arquitectura del Sistema](#️-arquitectura-del-sistema)
- [📂 Estructura del Proyecto](#-estructura-del-proyecto)
- [🧠 Modelos de Machine Learning](#-modelos-de-machine-learning)
- [🚀 Instalación](#-instalación)
- [▶️ Funcionamiento](#️-funcionamiento)
- [📊 Variables Utilizadas](#-variables-utilizadas)
- [🔌 Hardware Empleado](#-hardware-empleado)
- [🔮 Mejoras Futuras](#-mejoras-futuras)
- [🎓 Aprendizajes](#-aprendizajes)
- [👨‍💻 Autor](#-autor)

---

# 📖 Descripción

CleanBot Detections es el componente principal de un sistema de clasificación automática de residuos basado en Inteligencia Artificial.

El sistema utiliza un sensor de color **TCS3200** conectado a una **Raspberry Pi** para capturar información cromática de los objetos analizados.

Posteriormente:

1. Se capturan las frecuencias RGB.
2. Se generan características derivadas.
3. Un modelo de Machine Learning clasifica el material.
4. Se acciona un servomotor para dirigir el residuo al compartimento correspondiente.
5. Los eventos son almacenados en SQLite.
6. La información se expone mediante una API REST para su monitoreo remoto.

El objetivo es automatizar procesos de separación de residuos y fomentar prácticas de reciclaje inteligente.

---

# ✨ Características

✅ Lectura de frecuencias RGB mediante sensor TCS3200.

✅ Procesamiento en tiempo real sobre Raspberry Pi.

✅ Clasificación automática mediante Machine Learning.

✅ Control de servomotores para separación física.

✅ API REST para consulta de detecciones.

✅ Registro persistente mediante SQLite.

✅ Entrenamiento y comparación de múltiples modelos.

✅ Evaluación automática de desempeño.

✅ Arquitectura modular para futuras expansiones.

✅ Integración con cliente de monitoreo CleanBot.

---

# 🛠️ Tecnologías Utilizadas

| Tecnología | Función |
|------------|----------|
| Python | Desarrollo principal |
| Raspberry Pi | Computación embebida |
| Flask | API REST |
| SQLite | Persistencia local |
| Scikit-Learn | Entrenamiento de modelos |
| Pandas | Procesamiento de datos |
| NumPy | Operaciones matemáticas |
| Joblib | Serialización de modelos |
| GPIO | Control de hardware |
| TCS3200 | Sensor de color |
| Servo SG90 | Actuación mecánica |

---

# 🏗️ Arquitectura del Sistema

```text
Objeto
   │
   ▼
Sensor TCS3200
   │
   ▼
Frecuencias RGB
   │
   ▼
Extracción de Características
   │
   ▼
Modelo de Machine Learning
   │
   ▼
Clasificación
(Plástico / Otros)
   │
   ├────────► SQLite
   │
   ├────────► API Flask
   │
   ▼
Servo SG90
(Separación Física)
```

---

# 📂 Estructura del Proyecto

```text
cleanbot-detections/
│
├── cleanbot.py
├── train_model.py
├── training.py
├── testing.py
├── db.py
│
├── dataset.csv
├── dataset_copy.csv
│
├── cleanbot.db
│
├── best_model.pkl
├── best_model_trained.pkl
│
├── models/
│   ├── LogisticRegression.pkl
│   ├── KNN.pkl
│   ├── SVM_rbf.pkl
│   ├── DecisionTree.pkl
│   ├── RandomForest.pkl
│   ├── ExtraTrees.pkl
│   ├── GradientBoosting.pkl
│   ├── AdaBoost.pkl
│   ├── MLP.pkl
│   └── summary_results.csv
│
├── requirements.txt
└── README.md
```

---

# 🧠 Modelos de Machine Learning

Durante el desarrollo se evaluaron múltiples algoritmos de clasificación:

| Modelo |
|----------|
| Logistic Regression |
| K-Nearest Neighbors |
| Support Vector Machine (RBF) |
| Decision Tree |
| Random Forest |
| Extra Trees |
| Gradient Boosting |
| AdaBoost |
| Multi-Layer Perceptron |

Cada modelo fue entrenado y comparado utilizando validación cruzada para seleccionar el de mejor desempeño.

---

# 📊 Variables Utilizadas

El sistema no utiliza únicamente los valores RGB crudos.

También genera características derivadas para mejorar la capacidad predictiva:

| Variable |
|-----------|
| R |
| G |
| B |
| Intensidad |
| R_norm |
| G_norm |
| B_norm |
| RG_ratio |
| RB_ratio |
| BG_ratio |

Estas variables permiten capturar relaciones cromáticas más robustas entre los materiales analizados.

---

# 🔌 Hardware Empleado

### 🧠 Raspberry Pi

Encargada de ejecutar el sistema completo.

### 🌈 Sensor TCS3200

Utilizado para medir frecuencias asociadas a componentes:

- Rojo (R)
- Verde (G)
- Azul (B)

### ⚙️ Servo SG90

Permite dirigir físicamente los residuos hacia diferentes compartimentos según la clasificación obtenida.

---

# 🚀 Instalación

## 1️⃣ Clonar repositorio

```bash
git clone https://github.com/jcm78411/cleanbot-detections.git
cd cleanbot-detections
```

## 2️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

## 3️⃣ Ejecutar sistema principal

```bash
python cleanbot.py
```

---

# ▶️ Funcionamiento

Cuando un objeto es colocado frente al sensor:

1. Se capturan las frecuencias RGB.
2. Se calculan características derivadas.
3. El modelo entrenado realiza la predicción.
4. Se determina el tipo de material.
5. Se acciona el servomotor.
6. Se registra el evento.
7. La información queda disponible vía API.

Resultado esperado:

```text
Material detectado: Plastico
```

o

```text
Material detectado: Otros
```

---

# 🌐 API REST

El sistema expone una API desarrollada con Flask para consultar las detecciones registradas.

Esto permite integrarlo con:

- Dashboards.
- Aplicaciones móviles.
- Sistemas de monitoreo.
- Cliente Electron de CleanBot.

---

# 🔮 Mejoras Futuras

- [ ] Clasificación multiclase.
- [ ] Integración con visión por computadora.
- [ ] Uso de cámaras RGB.
- [ ] Dashboard web en tiempo real.
- [ ] Conexión con servicios cloud.
- [ ] Reentrenamiento automático.
- [ ] Detección de más materiales reciclables.
- [ ] Sistema distribuido para múltiples estaciones CleanBot.

---

# 🎓 Aprendizajes

Durante el desarrollo se fortalecieron conocimientos relacionados con:

- Internet de las Cosas (IoT).
- Raspberry Pi.
- Sensores electrónicos.
- Machine Learning.
- Clasificación supervisada.
- Automatización industrial.
- APIs REST.
- Bases de datos SQLite.
- Integración hardware-software.

---

# 👨‍💻 Autor

**Juan Luis Cueto Morelo**

Ingeniero de Sistemas

Áreas de interés:

- Inteligencia Artificial
- Internet de las Cosas (IoT)
- Machine Learning
- Automatización Industrial
- Sistemas Embebidos

GitHub:

https://github.com/jcm78411

---

<div align="center">

### ⭐ Este proyecto tiene dos partes, consulta la otra en: **[monitor_detecciones_cliente](https://github.com/jcm78411/cleanbot-detections-client)**.

♻️ Clasificando residuos • 🤖 Aplicando Inteligencia Artificial • 🚀 Construyendo soluciones sostenibles

</div>
