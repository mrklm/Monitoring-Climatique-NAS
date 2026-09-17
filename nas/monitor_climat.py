import serial
import time
import requests
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================
port_serie  = '/dev/arduino_nas'
fichier_log = '/srv/dev-disk-by-uuid-VOTRE_UUID_ICI/monitoring/climat.csv'

# Seuils d'alerte
TEMP_MAX = 30.0    # °C
HUM_MAX  = 80.0    # %

# ntfy (instance locale)
NTFY_URL = "http://localhost:8080/mon-nas-climat-alerte"

# Alerte "pas de données" : délai sans réception avant alerte
DELAI_SANS_DONNEES = 15 * 60   # 15 minutes


# ============================================================
# FONCTIONS
# ============================================================
def envoyer_ntfy(titre, message, priorite="default", tags="warning"):
    """Envoie une notification via ntfy.
    
    IMPORTANT : les emojis ne doivent JAMAIS être dans le titre (header HTTP),
    car requests encode les headers en latin-1 par défaut, ce qui fait planter
    l'envoi avec une erreur 'latin-1 codec can't encode character'.
    
    Les emojis sont OK dans le corps du message (encodé explicitement en UTF-8).
    """
    try:
        requests.post(
            NTFY_URL,
            data=message.encode('utf-8'),
            headers={
                "Title": titre,
                "Priority": priorite,
                "Tags": tags
            },
            timeout=5
        )
    except Exception as e:
        print(f"Erreur envoi ntfy: {e}")


# États : "normal" ou "alerte"
etat_temp_precedent    = "normal"
etat_hum_precedent     = "normal"
etat_donnees_precedent = "normal"

# Initialisé à None tant qu'aucune donnée n'a été reçue depuis le démarrage.
# Cela évite les fausses alertes "pas de données" au redémarrage du NAS.
derniere_reception = None


def verifier_seuils(temp, hum):
    """Compare aux seuils et envoie une notif aux transitions."""
    global etat_temp_precedent, etat_hum_precedent

    # --- Température ---
    etat_temp = "alerte" if temp > TEMP_MAX else "normal"
    if etat_temp != etat_temp_precedent:
        if etat_temp == "alerte":
            envoyer_ntfy(
                "[ALERTE] Temperature NAS",
                f"🌡️ Température élevée : {temp}°C (seuil {TEMP_MAX}°C)",
                priorite="urgent",
                tags="warning,thermometer"
            )
        else:
            envoyer_ntfy(
                "[OK] Temperature NAS revenue a la normale",
                f"🌡️ Température : {temp}°C",
                priorite="default",
                tags="white_check_mark"
            )
        etat_temp_precedent = etat_temp

    # --- Humidité ---
    etat_hum = "alerte" if hum > HUM_MAX else "normal"
    if etat_hum != etat_hum_precedent:
        if etat_hum == "alerte":
            envoyer_ntfy(
                "[ALERTE] Humidite NAS",
                f"💧 Humidité élevée : {hum}% (seuil {HUM_MAX}%)",
                priorite="urgent",
                tags="warning,droplet"
            )
        else:
            envoyer_ntfy(
                "[OK] Humidite NAS revenue a la normale",
                f"💧 Humidité : {hum}%",
                priorite="default",
                tags="white_check_mark"
            )
        etat_hum_precedent = etat_hum


def verifier_silence():
    """Alerte si plus de données reçues depuis trop longtemps.
    Ne fait rien tant qu'aucune donnée n'a jamais été reçue (démarrage)."""
    global etat_donnees_precedent
    if derniere_reception is None:
        return

    ecart = (datetime.now() - derniere_reception).total_seconds()

    if ecart > DELAI_SANS_DONNEES and etat_donnees_precedent == "normal":
        envoyer_ntfy(
            "[URGENT] Plus de donnees du capteur",
            f"🚨 Aucune donnée reçue depuis {int(ecart/60)} minutes.\n"
            f"Vérifier l'Arduino, le câble USB et le service.",
            priorite="urgent",
            tags="rotating_light,electric_plug"
        )
        etat_donnees_precedent = "alerte"

    elif ecart <= DELAI_SANS_DONNEES and etat_donnees_precedent == "alerte":
        envoyer_ntfy(
            "[OK] Capteur de nouveau operationnel",
            "✅ Les données sont de nouveau reçues.",
            priorite="default",
            tags="white_check_mark"
        )
        etat_donnees_precedent = "normal"


# ============================================================
# BOUCLE PRINCIPALE
# ============================================================
try:
    ser = serial.Serial(port_serie, 9600, timeout=1)
    print("Surveillance active (Temp + Hum).")

    try:
        with open(fichier_log, "x") as f:
            f.write("Date et Heure,Temperature_C,Humidite_Pct\n")
    except FileExistsError:
        pass

    # Notif de démarrage
    envoyer_ntfy(
        "[OK] Monitoring climatique demarre",
        "🟢 Le service de surveillance est actif.",
        priorite="low",
        tags="white_check_mark"
    )

    while True:
        if ser.in_waiting > 0:
            ligne = ser.readline().decode('utf-8').strip()
            if ligne.startswith("DATA,"):
                _, temp, hum = ligne.split(",")
                temp = float(temp)
                hum  = float(hum)
                maintenant = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                with open(fichier_log, "a") as f:
                    f.write(f"{maintenant},{temp},{hum}\n")

                # À partir d'ici, on a une donnée : le compteur de silence démarre
                derniere_reception = datetime.now()

                verifier_seuils(temp, hum)

                if temp > TEMP_MAX or hum > HUM_MAX:
                    print(f"ALERTE: Temp {temp}C | Hum {hum}%")
                else:
                    print(f"Temp: {temp}C | Hum: {hum}%")

        # Vérifie le silence même si aucune ligne n'arrive
        verifier_silence()

        time.sleep(60)

except KeyboardInterrupt:
    print("Arret du script.")
except Exception as e:
    print("Erreur: " + str(e))
    envoyer_ntfy(
        "[URGENT] Erreur du script monitoring",
        f"🚨 Le script s'est arrêté : {e}",
        priorite="urgent",
        tags="rotating_light"
    )
    raise