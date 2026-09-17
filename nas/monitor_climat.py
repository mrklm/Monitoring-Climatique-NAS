import serial
import time
from datetime import datetime

port_serie = '/dev/arduino_nas'
# Remplace TON_UUID_ICI par l'UUID de ton disque (ex: 4a6d87ff-3fee-405f-a4ef-313d1775bb47)
fichier_log = '/srv/dev-disk-by-uuid-TON_UUID_ICI/monitoring/climat.csv'
TEMP_MAX = 30.0

try:
    ser = serial.Serial(port_serie, 9600, timeout=1)
    print("Surveillance active (Temp + Hum).")
    
    try:
        with open(fichier_log, "x") as f:
            f.write("Date et Heure,Temperature_C,Humidite_Pct\n")
    except FileExistsError:
        pass

    while True:
        if ser.in_waiting > 0:
            ligne = ser.readline().decode('utf-8').strip()
            if ligne.startswith("DATA,"):
                _, temp, hum = ligne.split(",")
                maintenant = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                with open(fichier_log, "a") as f:
                    f.write(f"{maintenant},{temp},{hum}\n")
                
                if float(temp) > TEMP_MAX:
                    print(f"ALERTE: Temp {temp}C | Hum {hum}%")
                else:
                    print(f"Temp: {temp}C | Hum: {hum}%")
        time.sleep(60)
except KeyboardInterrupt:
    print("Arret du script.")
except Exception as e:
    print("Erreur: " + str(e))
