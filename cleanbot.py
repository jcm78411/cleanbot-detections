#!/usr/bin/env python3
# cleanbot.py - C�digo revisado para Raspberry Pi 3 B+ con TCS3200 y Servo SG90

from flask import Flask, jsonify
import RPi.GPIO as GPIO
import time
import sqlite3
from datetime import datetime
import sys
import threading

# ---------------------------
# Configuracion GPIO
# ---------------------------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

S0, S1, S2, S3, OUT = 23, 24, 17, 27, 22
SERVO_PIN = 18

GPIO.setup(S0, GPIO.OUT)
GPIO.setup(S1, GPIO.OUT)
GPIO.setup(S2, GPIO.OUT)
GPIO.setup(S3, GPIO.OUT)
GPIO.setup(OUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm_servo = GPIO.PWM(SERVO_PIN, 50)
pwm_servo.start(0)
time.sleep(0.2)

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


def clasificar_material(r, g, b):
    if g == 0 or b == 0:
        return "Desconocido"

    ratio_rg = r / g
    ratio_rb = r / b

    if (
        (17000 <= r <= 26000 and 9000 <= g <= 15500 and 10000 <= b <= 17200)
        and (1.3 <= ratio_rg <= 1.7)
        and (1.2 <= ratio_rb <= 1.6)
    ):
        return "Plastico"

    return "Desconocido"

def abrir_tapa(segundos=5):
    pwm_servo.ChangeDutyCycle(7.5)
    time.sleep(segundos)
    cerrar_tapa()


def cerrar_tapa():
    pwm_servo.ChangeDutyCycle(2.5)
    time.sleep(0.5)
    pwm_servo.ChangeDutyCycle(0)

# ---------------------------
# Ciclo principal de lectura
# ---------------------------
def ciclo_medicion():
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
        cerrar_tapa()
        while True:
            rojo, verde, azul = medir_color()
            material = clasificar_material(rojo, verde, azul)
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            frecuencia_prom = int((rojo + verde + azul) / 3)

            c.execute(
                "INSERT INTO detecciones (material, frecuencia, frec_roja, frec_verde, frec_azul, fecha_hora) VALUES (?, ?, ?, ?, ?, ?)",
                (material, frecuencia_prom, int(rojo), int(verde), int(azul), fecha),
            )
            conn.commit()

            print(f"[{fecha}] Detectado: {material} (R:{rojo:.1f}, G:{verde:.1f}, B:{azul:.1f})")

            if material == "Plastico":
                print("-> Plastico detectado: abriendo tapa 5s")
                abrir_tapa(5)
            else:
                print("-> No es plastico")

            time.sleep(1)

    except KeyboardInterrupt:
        print("?? Deteniendo ciclo de medici�n...")
    finally:
        pwm_servo.stop()
        GPIO.cleanup()
        conn.close()


# ---------------------------
# Servidor Flask
# ---------------------------
app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('cleanbot.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/detecciones')
def mostrar_detecciones():
    conn = get_db_connection()
    registros = conn.execute('SELECT * FROM detecciones').fetchall()
    conn.close()
    return jsonify([dict(r) for r in registros])


# ---------------------------
# Ejecucion principal
# ---------------------------
if __name__ == "__main__":
    print("?? Iniciando CleanBot...")
    print("?? Iniciando hilo de lectura del sensor y base de datos...")
    hilo_sensor = threading.Thread(target=ciclo_medicion, daemon=True)
    hilo_sensor.start()

    print("?? Servidor Flask corriendo en http://0.0.0.0:5000/detecciones")
    print("?? Presiona CTRL + C para detener todo")
    app.run(host='0.0.0.0', port=5000)