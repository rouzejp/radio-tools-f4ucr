#!/usr/bin/env python3
"""Export notes Obsidian → CSV TIDRADIO TD-H9 Ham.

Usage:
    python export-h9.py [--output fichier.csv]
    python export-h9.py --output /tmp/td-h9.csv
"""

import csv
import os
import sys
import re
import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RADIO_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
FREQ_DIR = os.path.join(RADIO_DIR, "frequences")

HEADER = [
    "Fréq RX [MHz]",
    "Fréq TX [MHz]",
    "RX CTCSS/DCS",
    "TX CTCSS/DCS",
    "Puissance",
    "Bande",
    "Brouilleur",
    "PTT ID",
    "Saut Fréq",
    "Verr Occupé",
    "Scan",
    "Mode RX",
    "Nom",
]

# CTCSS valides (Hz) — tout ce qui est ≤ 300 Hz est CTCSS, pas DCS
MAX_CTCSS_HZ = 300.0


def parse_frontmatter(content):
    """Parse le frontmatter YAML d'une note Obsidian."""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {}
    yaml_text = "\n".join(lines[1:end_idx])
    try:
        props = yaml.safe_load(yaml_text)
        return props if isinstance(props, dict) else {}
    except yaml.YAMLError:
        return {}


def tone_to_ctcss(tone_val, tone_mode="none"):
    """Convertit une tonalité en format CTCSS/DCS pour le TD-H9.

    Règles :
    - Si tone_mode = 'none' → OFF (valeur stockée non active)
    - Si la valeur est vide/nulle/0 → OFF
    - Si ≤ 300 Hz → CTCSS pur (ex: 88.5, 118.8, 210.7, 250.3)
    - Sinon → DCS (ex: 023, 047 — non présent dans nos données)
    """
    if not tone_val or str(tone_val).strip() in ("0", "OFF", "NONE", "None", "none", ""):
        return "OFF"

    if tone_mode in ("none", "", None):
        return "OFF"

    try:
        f = float(str(tone_val))
    except (ValueError, TypeError):
        return "OFF"

    # CTCSS : ≤ 300 Hz (tous les CTCSS valides sont dans cette plage)
    if f <= MAX_CTCSS_HZ:
        return f"{f:.1f}"

    # DCS : > 300 (codes 3 chiffres)
    return f"D{int(f):03d}N"


def calc_tx_freq(props):
    """Calcule la fréquence TX depuis freq + duplex + offset."""
    rx_str = props.get("freq", "")
    try:
        rx = float(str(rx_str))
    except (ValueError, TypeError):
        return rx_str

    duplex = props.get("duplex", "")
    offset_str = props.get("offset", "0")

    try:
        offset = float(str(offset_str))
    except (ValueError, TypeError):
        offset = 0.0

    if duplex in ("minus", "-"):
        tx = rx - offset
    elif duplex in ("plus", "+"):
        tx = rx + offset
    else:
        tx = rx  # simplex

    return f"{tx:.5f}"


def fmt_freq(freq_str):
    """Formate une fréquence en MHz avec exactement 5 décimales."""
    try:
        f = float(str(freq_str))
        return f"{f:.5f}"
    except (ValueError, TypeError):
        return freq_str


def map_power(power_val):
    """Map power field to TD-H9 values."""
    if not power_val:
        return "Bas"
    p = str(power_val).strip()
    if p.lower() in ("high", "haut", "hi", "5.0w", "5w", "5"):
        return "Haut"
    return "Bas"


def map_bande_passante(mode_val, freq):
    """Détermine Bande (Large/Étroit) selon le mode et la fréquence."""
    if not mode_val:
        mode_val = "FM"
    m = str(mode_val).strip().upper()
    if m == "NFM":
        return "Étroit"
    if m == "AM" or m == "FM":
        return "Large"
    # défaut
    try:
        f = float(str(freq))
        if 108 <= f <= 137:
            return "Large"
    except (ValueError, TypeError):
        pass
    return "Large"


def format_nom(nom_raw):
    """Formate le nom pour le TD-H9 (max 16 chars, caractères simples)."""
    if not nom_raw:
        return ""
    nom = re.sub(r'[^\w\s\-]', '', str(nom_raw))
    nom = nom.strip()
    return nom[:16]


def read_all_notes():
    """Lit toutes les notes du dossier frequences/."""
    notes = []
    if not os.path.exists(FREQ_DIR):
        return notes
    for fname in sorted(os.listdir(FREQ_DIR)):
        if not fname.endswith(".md") or fname == "_index.md":
            continue
        fpath = os.path.join(FREQ_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        props = parse_frontmatter(content)
        if props and props.get("id"):
            notes.append((fname, props))
    return notes


def main():
    output = None
    quiet = False

    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--output" and i + 2 < len(sys.argv):
            output = sys.argv[i + 2]
        if arg == "--quiet":
            quiet = True

    notes = read_all_notes()
    if not notes:
        print("Aucune note trouvée dans frequences/")
        sys.exit(0)

    rows = [HEADER]

    for fname, props in notes:
        rx_freq = props.get("freq", "")
        tx_freq = calc_tx_freq(props)

        # Récupérer le tone_mode pour décider si les valeurs sont actives
        tone_mode = str(props.get("tone_mode", "none")).lower().strip()
        if tone_mode in ("none", "off", ""):
            tone_mode = "none"

        # Sémantique CHIRP → TD-H9 :
        # - tone_mode "tone"  → rx_tone (rToneFreq) = TX tone actif, RX = OFF
        # - tone_mode "tsql"  → rx_tone (rToneFreq) = même ton pour TX+RX
        # - tone_mode "none"  → pas de tonalité active
        # La valeur "tx_tone" (cToneFreq) n'est utilisée qu'en mode Cross.
        primary_tone = props.get("rx_tone", "")

        if tone_mode == "tone":
            active_tone = tone_to_ctcss(primary_tone, "tone")
            rx_tone = "OFF"
            tx_tone = active_tone
        elif tone_mode == "tsql":
            active_tone = tone_to_ctcss(primary_tone, "tsql")
            rx_tone = active_tone
            tx_tone = active_tone
        elif tone_mode == "dtcs":
            active_tone = tone_to_ctcss(primary_tone, "dtcs")
            rx_tone = active_tone
            tx_tone = active_tone
        else:
            # tone_mode = "none" : valeurs stockées inertes
            rx_tone = "OFF"
            tx_tone = "OFF"

        # Puissance
        puissance = map_power(props.get("power", ""))

        # Bande passante
        bande = map_bande_passante(props.get("mode", ""), rx_freq)

        # Saut de fréquence (skip)
        skip = props.get("skip", "")
        saut = "ON" if skip and str(skip).lower() in ("skip", "s", "on", "yes", "true") else "OFF"

        # Mode RX
        mode_rx = str(props.get("mode", "FM")).strip().upper()
        if mode_rx not in ("FM", "NFM", "AM"):
            mode_rx = "FM"

        # Nom
        nom = format_nom(props.get("nom", ""))

        row = [
            fmt_freq(rx_freq),
            fmt_freq(tx_freq),
            rx_tone,
            tx_tone,
            puissance,
            bande,
            "0",                # Brouilleur
            "Arrêt",            # PTT ID
            saut,               # Saut Fréq
            "OFF",              # Verr Occupé
            "ON",               # Scan
            mode_rx,            # Mode RX
            nom,                # Nom
        ]
        rows.append(row)

    if output:
        with open(output, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerows(rows)
        if not quiet:
            print(f"✅ Fichier TD-H9 généré : {output}")
            print(f"📋 {len(notes)} fréquences exportées")
    else:
        writer = csv.writer(sys.stdout, delimiter=",")
        writer.writerows(rows)

    return 0


if __name__ == "__main__":
    sys.exit(main())