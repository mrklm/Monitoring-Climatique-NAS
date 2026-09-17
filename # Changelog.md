# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [versionnage sémantique](https://semver.org/lang/fr/).

## [Non publié]

### À venir
- Support pour l'accès distant aux alertes
- AJout second capteur pour comparaison

## [0.2.0] - 2026-09-18

### Ajouté
- **Alertes push via ntfy** auto-hébergé (Docker)
  - Notifications en temps réel sur température et humidité
  - Alerte « pas de données » si le capteur ne répond plus pendant 15 minutes
  - Notification de démarrage du service
- **Fichier `LICENSE`** (GPL v3)
- **Fichier `CHANGELOG.md`** (ce fichier)
- **Règle udev** `nas/99-arduino-nas.rules` pour un port série fixe (`/dev/arduino_nas`)
- Section « Alertes ntfy » dans le README
- Section « Personnalisation des alertes » dans le README

### Modifié
- **README** : refonte complète (intro, étapes d'installation, dépannage, sécurité)
- **Licence** : passage de MIT à **GPL v3**
- **Noms de services systemd** :
  - `monitor_climat.service` → `monitor-climat.service`
  - `dashboard.service` → `dashboard-climat.service`
- **Format CSV** : `Date et Heure,Temperature_C,Humidite_Pct`
- **Lecture du port série** : lit désormais tout le buffer et garde la dernière valeur
  (corrige le décalage entre les valeurs affichées sur le LCD et celles enregistrées)

### Corrigé
- Bug d'encodage **latin-1** lors de l'envoi ntfy : les emojis ne doivent plus
  être placés dans le titre (header HTTP), mais uniquement dans le corps du message
- Décalage entre les valeurs LCD et les valeurs enregistrées dans le CSV :
  le script ne lit plus la première ligne du buffer, mais la dernière
- Bloc de code mal fermé à l'Étape 3 du README (règle udev)

## [0.1.0] - 2026-09-17

### Ajouté
- Version initiale du projet
- Code Arduino `sht31_nas_monitor.ino` (lecture SHT31 + affichage LCD)
- Script `monitor_climat.py` (lecture série → CSV)
- Script `setup_dashboard.py` (génération du dashboard Flask)
- Dashboard web avec 16 thèmes et sélection aléatoire
- Services systemd pour le démarrage automatique
- Documentation initiale (README)

[Non publié]: https://github.com/mrklm/Monitoring-Climatique-NAS/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/mrklm/Monitoring-Climatique-NAS/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mrklm/Monitoring-Climatique-NAS/releases/tag/v0.1.0