---
titre: APRS sur Tidradio TD-H9 — Guide complet
indicatif: F4UCR
mode: portable
date: 2026-06-11
tags:
  - radio
  - aprs
  - td-h9
  - tidradio
  - hardware
---

Voir aussi : [[documentation/tidradio-td-h3|TIDRADIO TD-H3]], [[frequences/_index|Index des fréquences]]

# APRS sur Tidradio TD-H9 — Guide complet pour F4UCR en portable

> Documentation basée sur les recommandations IARU, France APRS, et le manuel officiel TIDRADIO TD-H9.

---

## 1. Qu'est-ce que l'APRS ?

**APRS** (Automatic Packet Reporting System) = protocole numérique radioamateur développé par Bob Bruninga (WB4APR) dans les années 1980 pour transmettre :

- **Position GPS** — votre localisation en temps réel
- **Messages texte** — SMS-like entre stations
- **Données météo**, alertes, télémesure

Fonctionne en **AFSK 1200 bauds** sur **144.800 MHz** en Europe.

Les paquets sont relayés par des **digipeaters** (relais numériques) et remontent vers des **iGates** (passerelles Internet) visibles sur [aprs.fi](https://aprs.fi).

Le TD-H9 intègre l'APRS nativement : GPS + modem TNC + Bluetooth KISS, le tout dans un seul boîtier. Pas de matériel externe nécessaire.

---

## 2. Fréquences APRS

Conformément aux recommandations IARU Région 1 :

| Bande | Fréquence | Débit | Usage |
|-------|-----------|-------|-------|
| **2m (VHF)** | **144.800 MHz** | 1200 bauds FM | **APRS principal Europe** |
| 70cm (UHF) | 430.825 MHz | 9600 bauds FM | APRS secondaire (moins de couverture) |
| 40m | 7.035 MHz | 300 bauds LSB | APRS HF |
| 30m | 10.150 MHz | 300 bauds LSB | APRS HF |
| 20m | 14.105 MHz | 300 bauds LSB | APRS HF |
| 10m | 29.250 MHz | 300 bauds LSB | APRS HF |

> **Pour F4UCR en portable : utilise 144.800 MHz exclusivement.** La couverture 70cm APRS est trop faible pour un usage mobile/portable. Les bandes HF nécessitent un équipement spécifique.

---

## 3. Configuration APRS du TD-H9

### 3.1 Accès au menu APRS

Depuis l'écran principal : **Menu → APRS** (7 sous-menus numérotés).

#### MENU 1 — APRS Switch

| Paramètre | Valeur | Explication |
|-----------|--------|-------------|
| **APRS Switch** | **ON** | Active le module APRS |

#### MENU 2 — Beacon Set (paramètres de balise)

| Paramètre | Valeur F4UCR | Explication |
|-----------|--------------|-------------|
| **Call Sign** | `F4UCR` | Indicatif (max 6 car., majuscules + chiffres) |
| **SSID** | `7` | **SSID 7 = portable/pédestre** (voir §4) |
| **SSID Symbol** | `/` | Séparateur standard entre indicatif et SSID |
| **Custom Information** | `F4UCR - Portable QRV` | Texte libre (visible sur aprs.fi) |
| **Icon Settings** | `/>` | Icône **portable** (marcheur/pédestre) |
| **MIC Type** | `M0` | M0 = Repos. M1 = En route, M7 = Urgence |
| **Route 1 & 2** | (vide) | Itinéraires avec compteurs — laisser vide |
| **Report Voltage** | OFF | Économise la batterie |
| **Report Sats** | OFF | Pas pertinent en portable |
| **Report Mileage** | OFF | Pas pertinent |

#### MENU 3 — Beacon Type (type et intervalle)

| Paramètre | Valeur | Explication |
|-----------|--------|-------------|
| **PTT Linkage** | OFF | Ne pas envoyer de balise à chaque PTT |
| **Timed Beacon** | ON | Balise automatique à intervalle régulier |
| **Timing** | `0300` | **300 secondes = 5 minutes** (bon compromis portable) |

> **Astuce portable** : 5 min économise la batterie. En randonnée, passe à 600 (10 min). Pour les tests, mets 0030 (30s) puis repasse à 0300.

#### MENU 4 — Relay Set (DIGI / relais numérique)

| Paramètre | Valeur | Explication |
|-----------|--------|-------------|
| **DIGI Forward CH** | CH A | Canal de rediffusion = canal APRS |
| **DIGI1 Enable** | OFF | Pas de digipeat en portable (économie) |
| **DIGI2 Enable** | OFF | Idem |
| **DIGI1 Name** | `WIDE1` | Nom du relais 1 (par défaut) |
| **DIGI2 Name** | `WIDE2` | Nom du relais 2 (par défaut) |
| **Wait Before Forwarding** | `0` | Pas de temporisation |
| **Remote Password** | `123456` | Mot de passe pour activation à distance (défaut) |

> En portable, tu es client APRS, pas relais. Laisse DIGI1/DIGI2 sur OFF.

#### MENU 5 — Advanced Set (paramètres avancés)

| Paramètre | Valeur | Explication |
|-----------|--------|-------------|
| **APRS RX CH** | CH-A | Réception APRS sur canal A |
| **APRS TX CH** | CH-A | Émission APRS sur canal A |
| **PTT Priority** | Talk | Priorité à la voix (APRS émet entre les conversations) |
| **RX Decode Tone** | ON | Bip quand un message APRS est bien décodé |
| **TX Tone** | ON | Bip à l'envoi d'une balise |
| **Beacon Auto Popup** | ON | Affiche automatiquement les balises reçues |

#### MENU 6 — Beacon List

Gère les balises stockées (jusqu'à 100). Laisse vide par défaut — les balises sont générées automatiquement.

#### MENU 7 — APRS Reset

Restaurer les paramètres APRS d'usine. Ne pas toucher en usage normal.

---

## 4. SSID — Bien choisir le sien

Le **SSID** (Secondary Station ID) identifie le type de station. Conformément aux recommandations France APRS / IARU :

| SSID | Usage | Pour F4UCR |
|------|-------|-------------|
| (aucun) | Station principale fixe | Non |
| 1-4 | Station secondaire fixe | Non |
| 5 | Autres réseaux (DMR, D-STAR, Android, iPhone) | Non |
| 6 | Activité spéciale (satellite, camping, DX, contest) | Non |
| **7** | **Portable / pédestre** | **✅ OUI — à utiliser** |
| 8 | Mobile spécial (bateau, camping-car) | Non |
| 9 | Station mobile principale (voiture) | Non |
| 10 | iGate | Non |
| 11 | Mobile aérien (ballon, avion, planeur) | Non |
| 12 | Tracker léger (APRStt, DTMF, RFID) | Non |
| 13 | Station météo | Non |
| 14 | Camion / professionnel de la route | Non |
| 15 | Générique secondaire | Non |

> **F4UCR-7** = votre signature APRS en portable. Visible sur aprs.fi comme `F4UCR-7`.

---

## 5. Chemin APRS (Path) — WIDEn-N

Le **chemin** détermine combien de sauts votre balise peut faire via les digipeaters. Depuis 2008, l'IARU Région 1 a adopté le **paradigme n-N** pour réduire la congestion du réseau.

| Chemin | Sauts | Usage recommandé |
|--------|-------|------------------|
| `WIDE1-1` | 1 saut | Fixe en zone dense (grande ville, plusieurs digis) |
| `WIDE2-2` | 2 sauts | Fixe par défaut |
| **`WIDE1-1,WIDE2-1`** | **1 saut fill-in + 1 saut WIDE** | **Mobile/portable par défaut** |
| `WIDE1-1,WIDE2-2` | 1 + 2 sauts | Mobile en zone isolée ou montagne |

> **Pour F4UCR portable : `WIDE1-1,WIDE2-1`** — le chemin standard recommandé par France APRS pour les stations mobiles. Le premier saut (WIDE1-1) permet aux digipeaters fill-in locaux de capter, le second (WIDE2-1) relaye vers le réseau large.

---

## 6. Configuration des canaux APRS

Le TD-H9 permet d'assigner un **canal APRS** et un **canal voix** indépendamment.

### Méthode recommandée pour portable :

| Canal | Fonction | Fréquence | Usage |
|-------|----------|-----------|-------|
| **CH-A** | **APRS** | **144.800 MHz** | Balises + messages |
| **CH-B** | **Voix** | Variable | Communication vocale |

### Configuration :

1. Programme le canal A : `144.800 MHz`, pas de tone, nom `APRS`
2. Programme le canal B : ta fréquence de travail (ex: 145.500 simplex, ou un relais local)
3. Dans MENU 5 : APRS TX CH = CH-A, APRS RX CH = CH-A
4. En usage : bascule entre CH-A (APRS) et CH-B (voix) avec le bouton A/B

> La radio gère les deux canaux en parallèle. L'APRS émet automatiquement sur CH-A pendant que tu parles sur CH-B.

---

## 7. Utilisation pratique en portable

### 7.1 Avant de partir

1. **Batterie chargée** (2400 mAh — une journée en 5W/5min suffit)
2. **GPS activé** : mets la radio en extérieur 2 min avant de partir
3. **Vérifie l'icône GPS** sur l'écran (fixe = position acquise)
4. **APRS Switch = ON**
5. **Antenne** : utilise l'antenne d'origine ou une meilleure (Nagoya NA-771, etc.)

### 7.2 Pendant la sortie

- La radio émet une balise toutes les **5 minutes** automatiquement
- Tu peux **parler normalement** sur le canal B (voix)
- Les messages APRS entrants s'affichent à l'écran
- **Bip** = message APRS reçu et décodé

### 7.3 Vérifier sa position

- Sur [aprs.fi](https://aprs.fi) : cherche `F4UCR-7`
- Application **Odmaster** (Android) : connexion Bluetooth → carte en temps réel
- Application **APRSdroid** (Android) : peut aussi afficher les stations

### 7.4 Envoyer un message APRS

1. Menu → APRS → Messages
2. Saisir l'indicatif destinataire (ex: `F1ABC`)
3. Composer le message (max 160 car.)
4. Envoyer

> **Passerelle SMSGTE** : envoie `@SMSGTE` suivi du numéro de téléphone et du message pour envoyer un vrai SMS via APRS.

---

## 8. Économie d'énergie en portable

| Action | Gain |
|--------|------|
| Intervalle beacon à 10 min (600s) | ÷2 consommation APRS |
| Report Voltage/Sats/Mileage = OFF | Évite des TX supplémentaires |
| Puissance 5W (HIGH) | Pas de Low — la portée APRS est déjà limite |
| Écran en veille | Rétroéclairage bas |
| GPS OFF si pas besoin | Économie majeure (mais pas de position) |

---

## 9. Dépannage

| Problème | Solution |
|----------|----------|
| **GPS ne s'allume pas** | Extérieur, ciel dégagé, attendre 2 min. Vérifier GPS activé dans les paramètres système. |
| **Pas de position sur aprs.fi** | Vérifier fréquence 144.800, APRS ON, chemin WIDE1-1,WIDE2-1. Tester avec intervalle 30s. |
| **Balise émise mais pas relayée** | Passer à WIDE1-1,WIDE2-2. Vérifier qu'un digipeater est dans le secteur (carte aprs.fi). |
| **Messages non reçus** | Vérifier APRS RX CH = CH-A. RX Decode Tone = ON pour confirmer. |
| **Batterie faible** | Passer intervalle à 10 min. Désactiver les rapports. |
| **Bluetooth ne connecte pas** | Oublier l'appareil dans les paramètres BT du téléphone et réappairer. |
| **CPS ne voit pas la radio** | Vérifier pilote CP210x installé. Essayer un autre câble USB-C. |
| **Le CPS ne lit pas la radio** | Essayer un autre port USB. Redémarrer la radio. |

---

## 10. Couverture APRS en France

### Digipeaters principaux

La France dispose d'un réseau dense de digipeaters APRS sur 144.800 MHz. En portable avec 5W et antenne d'origine, tu touches les digis dans un rayon de **10-30 km** selon le terrain. En hauteur (colline, belvédère), la portée peut doubler.

Pour trouver les digipeaters près de chez toi :
- [aprs.fi](https://aprs.fi) → cocher **Digipeaters** dans la légende
- [franceaprs.net](https://franceaprs.net) → carte des iGates français

### Portée typique

| Configuration | Portée estimée |
|---------------|----------------|
| 5W + antenne d'origine, terrain plat | 10-15 km |
| 5W + antenne d'origine, en hauteur | 20-30 km |
| 5W + Nagoya NA-771, en hauteur | 30-50 km |
| 10W (boost TD-H9) + bonne antenne | 40-60 km |

---

## 11. Configuration via CPS (logiciel Tidradio)

Alternative plus confortable que le menu radio :

1. Télécharge le CPS sur [tidradio.com/pages/download](https://tidradio.com/pages/download)
2. Installe sur Windows (ou Wine sous Linux)
3. Connecte le TD-H9 en USB-C (pilote **CP210x** nécessaire)
4. **Read from Radio**
5. Onglet **APRS** → configure tous les paramètres ci-dessus
6. **Write to Radio** → redémarre la radio

---

## 12. Configuration via Odmaster (Android)

Programmation sans fil par Bluetooth :

1. Active Bluetooth sur le téléphone
2. Ouvre **Odmaster** (Play Store)
3. Scan → sélectionne le TD-H9
4. Navigue dans les paramètres APRS
5. Configure les mêmes valeurs qu'au §3
6. Synchronise

---

## 13. Bluetooth KISS TNC (usage avancé)

Le TD-H9 peut servir de **modem TNC** via Bluetooth KISS pour :

- **Dire Wolf** (Linux/Windows) → iGate ou digipeater
- **APRSIS32** (Windows) → visualisation carte
- **Xastir** (Linux) → carte APRS temps réel
- **APRSdroid** (Android) → affichage + logging

> Utile si tu veux faire un iGate fixe à la maison avec un Raspberry Pi + TD-H9.

### Compression MIC-E

Le TD-H9 utilise le format **MIC-E** (Microphone-Encoder) pour compresser les données de balise avant transmission. Cela réduit le temps d'antenne, diminue les interférences et améliore le taux de décodage.

---

## 14. Récapitulatif — Fiche mémo portable F4UCR

```
┌─────────────────────────────────────────────┐
│         APRS PORTABLE — F4UCR-7              │
├─────────────────────────────────────────────┤
│ Fréquence      : 144.800 MHz                 │
│ Indicatif      : F4UCR-7                     │
│ Chemin         : WIDE1-1,WIDE2-1             │
│ Intervalle     : 300s (5 min)                │
│ Puissance      : 5W (HIGH)                   │
│ Canal APRS     : CH-A                        │
│ Canal voix     : CH-B                        │
│ Icône          : /> (portable/pédestre)      │
│ Commentaire    : "F4UCR - Portable QRV"      │
│ GPS            : ON (extérieur 2 min)        │
│ APRS Switch    : ON                          │
│ PTT Linkage    : OFF                         │
│ DIGI1/DIGI2    : OFF                         │
└─────────────────────────────────────────────┘
```

---

## 15. Ressources

- [aprs.fi](https://aprs.fi) — Carte mondiale APRS en temps réel
- [franceaprs.net](https://franceaprs.net) — Wiki APRS France (recommandations, aide)
- [tidradio.com/pages/download](https://tidradio.com/pages/download) — CPS, firmware, manuels
- [Odmaster Web](https://web.odmaster.net) — Programmation en ligne
- [APRS France — Recommandations](https://franceaprs.net/doku.php?id=aide:recommandations)
- [Guide APRS (PDF)](https://adrasec08.fr/wp-content/uploads/2022/01/Guide-APRS-beta.pdf)
- [Symboles APRS officiels](http://www.aprs.org/symbols/symbols-new.txt)
- [Article blog Rouzé — APRS sur TD-H9](https://rouze.eu/programmer-et-utiliser-laprs-sur-le-tidradio-td-h9/)
