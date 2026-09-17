
# 🌡️ Monitoring Climatique NAS

Un système complet et robuste de surveillance de la température et de l'humidité, connecté à un NAS OpenMediaVault (OMV). Ce projet combine un capteur Arduino, un stockage sécurisé sur RAID et un tableau de bord web personnalisé avec thèmes dynamiques et alertes.

![License](https://img.shields.io/badge/License-MIT-blue)

## 📸 Aperçu du projet

<table>
  <tr>
    <td align="center"><img src="assets/1.jpeg" alt="SHT31" width="400"/><br><i>Capteur SHT31</i></td>
    <td align="center"><img src="assets/2.jpg" alt="NAS" width="400"/><br><i>Installation sur le NAS</i></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/3.jpg" alt="Prototype" width="400"/><br><i>Prototype de test</i></td>
    <td align="center"><img src="assets/4.png" alt="Interface" width="400"/><br><i>Interface Web Dashboard</i></td>
  </tr>
</table>

---

## ✨ Fonctionnalités

- **Acquisition fiable** : Lecture du capteur SHT31 (Température + Humidité) via Arduino.
- **Stockage robuste** : Enregistrement continu des données dans un fichier CSV sur le volume de stockage.
- **Dashboard Web** : Interface légère en Flask + Chart.js, accessible sur tout le réseau local.
- **Thèmes personnalisés** : 16 thèmes intégrés (Sombres, Clairs, et "Pouêt-Pouêt") avec sélection aléatoire au chargement.
- **Système d'alerte** : Notification visuelle (cadre rouge pulsant) si l'humidité dépasse 80%.
- **Démarrage automatique** : Gestion via `systemd` pour une exécution en arrière-plan au démarrage du NAS.

---

## 🛠️ Matériel requis

- 1x Arduino (Uno, Nano ou compatible)
- 1x Capteur de température et d'humidité **SHT31** (interface I2C)
- 1x Écran LCD I2C 16x2 (optionnel, pour affichage local sur l'Arduino)
- 1x Câble USB **de données** (Attention : beaucoup de câbles USB ne font que la charge !)
- 1x NAS sous OpenMediaVault (OMV) avec un dossier partagé configuré

---

## 🔌 Câblage

| Composant | Broche | Connexion Arduino |
| :--- | :---: | :--- |
| **SHT31** | VIN | 3.3V |
| | GND | GND |
| | SCL-T | A5 (SCL) |
| | SAA-RH | A4 (SDA) |
| **LCD I2C** | VCC | 5V |
| | GND | GND |
| | SDA | A4 (SDA) |
| | SCL | A5 (SCL) |

*(Les broches AL/AD du SHT31 doivent rester non connectées pour utiliser l'adresse I2C par défaut `0x44`)*.

---

## 💻 Installation

### Étape 1 : Configuration Arduino
1. Installe les bibliothèques suivantes via le gestionnaire de bibliothèques de l'IDE Arduino :
   - `LiquidCrystal I2C` (par Frank de Brabander)
   - `SHT31` (par Rob Tillaart)
2. Téléverse le code situé dans `arduino/sht31_nas_monitor.ino`.
3. Ouvre le moniteur série à **9600 bauds** pour vérifier que les données `DATA,Temp,Hum` s'affichent.

### Étape 2 : Préparation du NAS (OpenMediaVault)
1. Crée un dossier partagé nommé `monitoring` sur ton volume de stockage principal via l'interface OMV.
2. Note le chemin réel de ce dossier. Tu peux le trouver via l'interface OMV ou en tapant `lsblk -f` dans le terminal.

### Étape 3 : Règle Udev (Port Série Fixe)
Pour éviter que le nom du port Arduino (`/dev/ttyUSB0`) ne change au redémarrage :
1. Copie le fichier `nas/99-arduino-nas.rules` dans `/etc/udev/rules.d/` sur le NAS.
2. Recharge les règles et redémarre le service udev :
   ```bash
   sudo udevadm control --reload-rules
   sudo udevadm trigger

---

### Étape 4 : Préparation du script de dashboard

Le repo fournit un générateur : `nas/setup_dashboard.py`. Il faut l'exécuter **avant** de démarrer le service dashboard, car il génère le fichier `dashboard.py` attendu par `nas/dashboard.service`.

```bash
cd /srv/dev-disk-by-uuid-VOTRE_UUID_ICI/monitoring/
python3 setup_dashboard.py
```

> 💡 Vérifiez ensuite que `dashboard.py` a bien été créé : `ls -l dashboard.py`

---

### Étape 5 : Installation des dépendances Python

En SSH sur le NAS :

```bash
# Outils de base (si non installés)
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Dépendances nécessaires (adapter selon les imports réels)
sudo pip3 install pyserial flask
```

> ⚠️ Les services fournis dans `nas/*.service` utilisent `User=root` et `/usr/bin/python3` (Python système, pas de venv). C'est fonctionnel mais peu élégant côté sécurité. Pour un usage domestique sur réseau local, ça reste acceptable.

---

### Étape 6 : Déploiement des scripts sur le volume de stockage

Les services systemd pointent vers `/srv/dev-disk-by-uuid-VOTRE_UUID_ICI/monitoring/`. Il faut donc :

**1. Trouver l'UUID de votre volume :**

```bash
lsblk -f
```

Repérez la ligne correspondant à votre disque/RAID, et copiez la valeur dans la colonne `UUID`.

**2. Copier les scripts au bon endroit :**

```bash
# Créer le dossier monitoring sur le volume
sudo mkdir -p /srv/dev-disk-by-uuid-VOTRE_UUID_ICI/monitoring

# Copier les scripts depuis le repo cloné
sudo cp ~/Monitoring-Climatique-NAS/nas/monitor_climat.py \
        ~/Monitoring-Climatique-NAS/nas/setup_dashboard.py \
        /srv/dev-disk-by-uuid-VOTRE_UUID_ICI/monitoring/

# Générer dashboard.py
cd /srv/dev-disk-by-uuid-VOTRE_UUID_ICI/monitoring/
sudo python3 setup_dashboard.py

# Vérifier
ls -la
```

**3. Adapter les services systemd :**

Éditez les deux fichiers `.service` du repo **avant** de les installer, pour remplacer `VOTRE_UUID_ICI` par la vraie valeur :

```bash
cd ~/Monitoring-Climatique-NAS/nas/
sed -i "s/VOTRE_UUID_ICI/VOTRE_VRAI_UUID/g" monitor_climat.service dashboard.service
```

> 💡 Vous pouvez aussi éditer à la main avec `nano monitor_climat.service`.

---

### Étape 7 : Test manuel avant systemd

**Toujours tester à la main avant d'activer les services** — sinon on débogue à l'aveugle.

```bash
cd /srv/dev-disk-by-uuid-VOTRE_UUID_ICI/monitoring/

# Terminal 1 : collecteur (lecture série → CSV)
sudo python3 monitor_climat.py

# Terminal 2 : dashboard Flask
sudo python3 dashboard.py
```

Puis depuis un navigateur du réseau : `http://IP-DU-NAS:5000`

Si tout fonctionne → passez à systemd. Sinon → inspectez les erreurs affichées.

---

### Étape 8 : Installation des services systemd

Les fichiers sont fournis dans `nas/`. Il faut les copier dans `/etc/systemd/system/` :

```bash
sudo cp ~/Monitoring-Climatique-NAS/nas/monitor_climat.service /etc/systemd/system/
sudo cp ~/Monitoring-Climatique-NAS/nas/dashboard.service /etc/systemd/system/

# Recharger systemd
sudo systemctl daemon-reload

# Activer + démarrer
sudo systemctl enable --now monitor_climat.service
sudo systemctl enable --now dashboard.service

# Vérifier l'état
systemctl status monitor_climat.service
systemctl status dashboard.service

# Logs en direct
journalctl -u monitor_climat.service -f
journalctl -u dashboard.service -f
```

---

### Étape 9 : Accès au dashboard

Depuis un navigateur sur le réseau local :

```
http://IP-DU-NAS:5000
```

Pour trouver l'IP du NAS :

```bash
hostname -I
```

**Optionnel** — accès depuis l'extérieur : passez **obligatoirement** par un reverse-proxy (nginx d'OMV) avec HTTPS et une authentification. ⚠️ **N'exposez jamais Flask directement sur Internet.**

---

### Étape 10 : Vérification du bon fonctionnement

Checklist après installation :

- [ ] Le fichier CSV se remplit bien
- [ ] Le dashboard affiche les données
- [ ] Les valeurs changent si on souffle sur le capteur
- [ ] Après `sudo reboot`, les deux services redémarrent seuls
- [ ] L'alerte humidité > 80 % se déclenche (souffler sur le capteur)

---

## 🔧 Dépannage

| Symptôme | Piste à explorer |
|---|---|
| Port série absent | Vérifier `/dev/ttyUSB*` / `/dev/ttyACM*`, `lsusb`, `dmesg \| tail` |
| Données illisibles | Baudrate 9600 ? Droits série ? |
| CSV vide | `journalctl -u monitor_climat -n 50` |
| `dashboard.py` introuvable | Relancer `sudo python3 setup_dashboard.py` |
| Dashboard inaccessible | Bonne IP ? Pare-feu OMV ? Port 5000 ouvert ? |
| Thème ne change pas | Vider le cache navigateur (Ctrl+F5) |
| Service ne démarre pas | `journalctl -u <monitor_climat\|dashboard> -xe` |
| Erreur "UUID not found" | Vérifier que `VOTRE_UUID_ICI` a bien été remplacé |

---

## 🔐 Sécurité

- ❌ Ne **jamais** exposer Flask directement sur Internet
- ✅ Ajouter une **authentification** (`flask-httpauth` ou via reverse-proxy)
- ✅ Restreindre l'accès au **LAN** via pare-feu
- ✅ Les services tournent en `root` — acceptable en LAN, à durcir (user dédié) si exposé
- ✅ Garder le système à jour (`sudo apt update && sudo apt upgrade`)

---

## 📄 Format du fichier CSV

```csv
timestamp,temperature,humidite
2026-09-17 19:15:00,22.4,47.2
2026-09-17 19:16:00,22.5,47.0
```

---

## 📜 Licence

Ce projet est placé sous licence **GNU General Public License v3.0** — voir le fichier [`LICENSE`](./LICENSE).

### 💡 Pourquoi ce projet est-il sous licence libre ?

Ce projet s'inscrit dans la philosophie du logiciel libre, promue par des associations comme [April](https://www.april.org/).

Le partage des connaissances et des outils est essentiel pour une société numérique plus juste et transparente.

---

## 🤝 Contribution

Les PR sont bienvenues ! Ouvrez d'abord une *issue* pour discuter de votre idée avant de coder.

---

## 🙏 Remerciements

- [Rob Tillaart](https://github.com/RobTillaart/SHT31) pour la bibliothèque `SHT31`
- [Frank de Brabander](https://github.com/johnrickman/LiquidCrystal_I2C) pour `LiquidCrystal I2C`
- La communauté OpenMediaVault pour la documentation
