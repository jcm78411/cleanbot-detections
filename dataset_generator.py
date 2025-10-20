#!/usr/bin/env python3
# dataset_generator.py - Genera dataset binario (Plastico / NoPlastico) para CleanBot

import RPi.GPIO as GPIO
import time
import csv
from datetime import datetime

# ---------------------------
# Configuracion GPIO
# ---------------------------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

S0, S1, S2, S3, OUT = 23, 24, 17, 27, 22

GPIO.setup(S0, GPIO.OUT)
GPIO.setup(S1, GPIO.OUT)
GPIO.setup(S2, GPIO.OUT)
GPIO.setup(S3, GPIO.OUT)
GPIO.setup(OUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Configuracion TCS3200 (20%)
GPIO.output(S0, GPIO.HIGH)
GPIO.output(S1, GPIO.LOW)

# ---------------------------
# Funciones del sensor
# ---------------------------
def medir_frecuencia(pulsos=20, timeout=1.0):
    start = time.time()
    count = 0
    last_state = GPIO.input(OUT)

    while (time.time() - start) < timeout and count < pulsos:
        current = GPIO.input(OUT)
        if last_state == GPIO.HIGH and current == GPIO.LOW:
            count += 1
        last_state = current

    duration = time.time() - start
    return (count / duration) if duration > 0 else 0.0


def medir_color():
    GPIO.output(S2, GPIO.LOW)
    GPIO.output(S3, GPIO.LOW)
    time.sleep(0.15)
    rojo = medir_frecuencia()

    GPIO.output(S2, GPIO.HIGH)
    GPIO.output(S3, GPIO.HIGH)
    time.sleep(0.15)
    verde = medir_frecuencia()

    GPIO.output(S2, GPIO.LOW)
    GPIO.output(S3, GPIO.HIGH)
    time.sleep(0.15)
    azul = medir_frecuencia()

    return rojo, verde, azul


# ---------------------------
# Funcion para registrar lecturas
# ---------------------------
def registrar_dato(etiqueta, r, g, b, archivo="dataset.csv"):
    intensidad = r + g + b
    r_norm = r / intensidad if intensidad != 0 else 0
    g_norm = g / intensidad if intensidad != 0 else 0
    b_norm = b / intensidad if intensidad != 0 else 0
    rg_ratio = r / g if g != 0 else 0
    rb_ratio = r / b if b != 0 else 0
    bg_ratio = b / g if g != 0 else 0

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(archivo, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            fecha, r, g, b, intensidad,
            round(r_norm, 3), round(g_norm, 3), round(b_norm, 3),
            round(rg_ratio, 3), round(rb_ratio, 3), round(bg_ratio, 3),
            etiqueta
        ])


# ---------------------------
# Bucle principal
# ---------------------------
if __name__ == "__main__":
    print("?? Generador de dataset CleanBot (Plastico / No Plastico)")
    print("Coloca el material frente al sensor.")
    print("Escribe '1' si es PLASTICO o '0' si NO lo es.")
    print("Escribe 'salir' para terminar.\n")

    # Cabecera del CSV (solo si el archivo esta vacio)
    with open("dataset.csv", mode="a", newline="") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow([
                "fecha", "R", "G", "B", "Intensidad",
                "R_norm", "G_norm", "B_norm",
                "RG_ratio", "RB_ratio", "BG_ratio",
                "Etiqueta"  # 1 = plastico, 0 = no plastico
            ])

    try:
        while True:
            entrada = input("??  Es plastico? (1=Si, 0=No, salir=terminar): ").strip()
            if entrada.lower() == "salir":
                break
            elif entrada not in ["0", "1"]:
                print("??  Entrada invalida. Solo 1, 0 o salir.")
                continue

            etiqueta = int(entrada)
            r, g, b = medir_color()
            registrar_dato(etiqueta, r, g, b)
            print(f"? Lectura guardada -> R:{r:.1f} G:{g:.1f} B:{b:.1f} | Etiqueta: {etiqueta}\n")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n?? Cancelado por el usuario.")
    finally:
        GPIO.cleanup()
        print("GPIO limpio. Dataset guardado en dataset.csv")
