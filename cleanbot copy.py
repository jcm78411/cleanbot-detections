#!/usr/bin/env python3
# cleanbot.py - Codigo revisado para Raspberry Pi 3 B+ con TCS3200 y Servo SG90
from flask import Flask, jsonify
import RPi.GPIO as GPIO
import time
import sqlite3
from datetime import datetime
import sys

# ---------------------------
# Configuracion general GPIO
# ---------------------------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # usa BCM consistentemente en todo el programa

# Pines TCS3200 (BCM)
S0 = 23
S1 = 24
S2 = 17
S3 = 27
OUT = 22

# Servo
SERVO_PIN = 18

# Configuracion pines
GPIO.setup(S0, GPIO.OUT)
GPIO.setup(S1, GPIO.OUT)
GPIO.setup(S2, GPIO.OUT)
GPIO.setup(S3, GPIO.OUT)
GPIO.setup(OUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm_servo = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz para servo
pwm_servo.start(0)
time.sleep(0.2)

# Configurar frecuencia de salida del TCS3200 (S0,S1)
# 00 - power down, 01 - 2%, 10 - 20%, 11 - 100%
# Aqui usamos 10 -> 20% (util para evitar saturacion)
GPIO.output(S0, GPIO.HIGH)
GPIO.output(S1, GPIO.LOW)

# ---------------------------
# Constantes y calibracion
# ---------------------------
# Umbrales de ejemplo para clasificar (ajustar con calibracion real)
UMBRAL_ROJO_PLA = 1200.0
UMBRAL_VERDE_PLA = 1000.0
UMBRAL_AZUL_PLA = 900.0

# ---------------------------
# Funciones auxiliares
# ---------------------------
def medir_frecuencia(pulsos=20, timeout=1.0):
    """
    Mide la frecuencia del pin OUT sin usar interrupciones.
    Cuenta los flancos descendentes manualmente, tolerante a ruido.
    """
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
    """
    Cambia S2/S3 para seleccionar canal R/G/B del TCS3200, mide frecuencia para cada canal.
    Devuelve tupla (rojo, verde, azul).
    """
    # Leer canal rojo (S2 LOW, S3 LOW)
    GPIO.output(S2, GPIO.LOW)
    GPIO.output(S3, GPIO.LOW)
    time.sleep(0.15)  # pequeÑo delay para estabilizar
    rojo = medir_frecuencia()

    # Leer canal verde (S2 HIGH, S3 HIGH)
    GPIO.output(S2, GPIO.HIGH)
    GPIO.output(S3, GPIO.HIGH)
    time.sleep(0.15)
    verde = medir_frecuencia()

    # Leer canal azul (S2 LOW, S3 HIGH)
    GPIO.output(S2, GPIO.LOW)
    GPIO.output(S3, GPIO.HIGH)
    time.sleep(0.15)
    azul = medir_frecuencia()

    return rojo, verde, azul


def clasificar_material(r, g, b):
    """
    Clasifica el material en funcion de los valores RGB medidos por el sensor TCS3200.
    Actualmente detecta PLASTICO segun los rangos y proporciones observadas.
    """

    # Evitar division por cero
    if g == 0 or b == 0:
        return "Desconocido"

    # Relaciones entre canales
    ratio_rg = r / g
    ratio_rb = r / b

    # --- Deteccion de plastico (basado en tus datos experimentales) ---
    if (
        (17000 <= r <= 26000 and 9000 <= g <= 15500 and 10000 <= b <= 17200)
        and (1.3 <= ratio_rg <= 1.7)
        and (1.2 <= ratio_rb <= 1.6)
    ):
        return "Plastico"

    # --- Otros materiales (por definir mas adelante) ---
    # Ejemplo: if ratio_rb < 1.0: return "Vidrio"
    # Ejemplo: if r < 10000 and g < 8000 and b < 8000: return "Metal"

    return "Desconocido"


def abrir_tapa(segundos=5):
    """Mueve el servo a posiciOn de apertura y vuelve a cerrar tras 'segundos'."""
    # Duty cycle aproximado para abrir (ajustar segun montaje)
    pwm_servo.ChangeDutyCycle(7.5)
    time.sleep(segundos)
    cerrar_tapa()


def cerrar_tapa():
    """Lleva servo a posiciOn cerrada y libera seÑal en forma segura."""
    pwm_servo.ChangeDutyCycle(2.5)
    time.sleep(0.5)
    pwm_servo.ChangeDutyCycle(0)  # dejar 0 para no mantener señal constante


# ---------------------------
# Util: test rApido de pin desde CLI
# ---------------------------
def test_pin_loop(pin=OUT):
    print(f"Leyendo pin {pin}... presiona Ctrl+C para salir")
    try:
        while True:
            print(GPIO.input(pin))
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("Test terminado por usuario.")


# ---------------------------
# Main
# ---------------------------
def main():
    # Soportar test rapido con argumento --test-pin
    if "--test-pin" in sys.argv:
        try:
            test_pin_loop(OUT)
        finally:
            # No cleanup masivo si solo se hizo test; dejar que termine todo
            GPIO.cleanup()
        return

    # Base de datos (SQLite local) - manejo robusto
    conn = sqlite3.connect("cleanbot.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS detecciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        material TEXT,
        frecuencia INTEGER,
        frec_roja,
        frec_verde,
        frec_azul,
        fecha_hora TEXT
    )"""
    )
    conn.commit()

    try:
        cerrar_tapa()  # posicion inicial
        while True:
            rojo, verde, azul = medir_color()
            material = clasificar_material(rojo, verde, azul)
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            frecuencia_prom = (
                int((rojo + verde + azul) / 3) if (rojo + verde + azul) > 0 else 0
            )

            # Guardar en SQLite
            c.execute(
                "INSERT INTO detecciones (material, frecuencia, frec_roja, frec_verde, frec_azul, fecha_hora) VALUES (?, ?, ?, ?, ?, ?)",
                (material, frecuencia_prom, int(rojo), int(verde), int(azul), fecha),
            )
            conn.commit()

            print(
                f"[{fecha}] Detectado: {material} (R:{rojo:.1f}, G:{verde:.1f}, B:{azul:.1f})"
            )

            if material == "Plastico":
                print("-> Plastico detectado: abriendo tapa 5s")
                abrir_tapa(segundos=5)
            else:
                print("-> No es plastico")

            time.sleep(1)

    except KeyboardInterrupt:
        print("Deteniendo programa por teclado...")
    finally:
        try:
            pwm_servo.stop()
        except Exception:
            pass
        GPIO.cleanup()
        conn.close()

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('cleanbot.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/detecciones')
def usuarios():
    conn = get_db_connection()
    usuarios = conn.execute('SELECT * FROM detecciones').fetchall()
    conn.close()
    return jsonify([dict(u) for u in usuarios])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    main()
