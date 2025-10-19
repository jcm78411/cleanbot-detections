import RPi.GPIO as GPIO
import time

S0, S1, S2, S3, OUT = 23, 24, 17, 27, 22
GPIO.setmode(GPIO.BCM)
GPIO.setup(S0, GPIO.OUT)
GPIO.setup(S1, GPIO.OUT)
GPIO.setup(S2, GPIO.OUT)
GPIO.setup(S3, GPIO.OUT)
GPIO.setup(OUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.output(S0, GPIO.HIGH)
GPIO.output(S1, GPIO.LOW)

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
    GPIO.output(S2, GPIO.LOW); GPIO.output(S3, GPIO.LOW)
    time.sleep(0.1)
    rojo = medir_frecuencia()
    GPIO.output(S2, GPIO.HIGH); GPIO.output(S3, GPIO.HIGH)
    time.sleep(0.1)
    verde = medir_frecuencia()
    GPIO.output(S2, GPIO.LOW); GPIO.output(S3, GPIO.HIGH)
    time.sleep(0.1)
    azul = medir_frecuencia()
    return rojo, verde, azul

try:
    while True:
        r, g, b = medir_color()
        print(f"R:{r:.1f}, G:{g:.1f}, B:{b:.1f}")
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
