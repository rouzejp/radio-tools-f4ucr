#!/usr/bin/env python3
"""
Import CSV radio → notes Obsidian (format universel).

Usage:
    python import.py <fichier_csv> <modele> [--prefix f] [--start 1]

Exemples:
    python import.py chirp_export.csv baofeng-uv5r
    python import.py tyt.csv tyt-md380 --prefix tyt- --start 100

Le mapping du modèle est cherché dans modeles/<modele>.yaml.
"""

import csv
import os
import sys
import re
import yaml
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RADIO_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
FREQ_DIR = os.path.join(RADIO_DIR, "frequences")
MODELES_DIR = os.path.join(RADIO_DIR, "modeles")
VAULT_DIR = os.path.normpath(os.path.join(RADIO_DIR, "..", ".."))

# Dossier par défaut pour les notes dans le vault
NOTE_DIR = FREQ_DIR


def slugify(text):
    """Simplifier un texte pour nom de fichier."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\-\s]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text[:60] or "freq"


def load_mapping(name):
    """Charge un fichier YAML de mapping depuis modeles/."""
    if name.endswith(".yaml"):
        path = name
    else:
        path = os.path.join(MODELES_DIR, f"{name}.yaml")

    if not os.path.exists(path):
        print(f"ERREUR: Mapping introuvable: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        mapping = yaml.safe_load(f)

    # Validation de base
    required = ["modele", "colonnes"]
    for key in required:
        if key not in mapping:
            print(f"ERREUR: Clé manquante '{key}' dans {path}", file=sys.stderr)
            sys.exit(1)

    return mapping


def get_next_id(prefix="f", start=1):
    """Trouve le prochain ID disponible dans le dossier frequences."""
    max_num = start - 1
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)")
    if os.path.exists(NOTE_DIR):
        for fname in os.listdir(NOTE_DIR):
            m = pattern.match(fname)
            if m:
                num = int(m.group(1))
                if num > max_num:
                    max_num = num
    return max_num + 1


def transform_value(key, value, mapping):
    """Applique les transformations définies dans le mapping."""
    transforms = mapping.get("transformations", {})
    if key in transforms and value in transforms[key]:
        return transforms[key][value]
    return value


def convert_type(raw, type_spec, cible):
    """Convertit une valeur selon le type attendu."""
    raw = raw.strip()

    if not raw:
        if cible in ("tone", "rx_tone", "tx_tone"):
            return ""
        return ""

    if type_spec == "mhz":
        # Normaliser le format fréquence: 146.520000 → 146.520, 146,52 → 146.520
        val = raw.replace(",", ".").strip()
        try:
            f = float(val)
            return f"{f:.3f}"
        except ValueError:
            return val

    if type_spec == "hz_optional":
        # CTCSS: peut être vide, "123.0", "0000", "T123"
        val = raw.strip().upper()
        val = val.replace("T", "").replace("D", "").strip()
        if not val or val in ("0", "0000", "OFF", "NONE"):
            return ""
        try:
            f = float(val)
            return f"{f:.1f}"
        except ValueError:
            return raw

    if type_spec == "float":
        try:
            return str(float(raw.replace(",", ".")))
        except ValueError:
            return raw

    if type_spec == "int":
        try:
            return str(int(raw))
        except ValueError:
            return raw

    # string par défaut
    return raw.strip()


def row_to_note(row, mapping, freq_id):
    """Convertit une ligne CSV en dictionnaire de propriétés YAML."""
    props = {
        "id": freq_id,
        "source": mapping.get("modele", "unknown"),
        "created": datetime.now().strftime("%Y-%m-%d"),
        "tags": [f"radio/{mapping.get('modele', 'unknown')}"],
    }

    # Appliquer les colonnes du mapping
    for col in mapping["colonnes"]:
        idx = col["index"]
        cible = col.get("cible", "ignore")
        nom_col = col.get("nom", f"col{idx}")
        type_spec = col.get("type", "string")

        if cible == "ignore":
            continue

        raw = row[idx] if idx < len(row) else ""
        val = convert_type(raw, type_spec, cible)
        val = transform_value(cible, val, mapping)
        if val or val == "0":
            props[cible] = val

    # Auto-détection de la bande depuis la fréquence
    freq = props.get("freq", "")
    if freq and "bande" not in props:
        try:
            f = float(str(freq).replace(",", "."))
            if 28 <= f <= 30:     props["bande"] = "10m"
            elif 50 <= f <= 54:   props["bande"] = "6m"
            elif 108 <= f <= 137: props["bande"] = "air"
            elif 144 <= f <= 148: props["bande"] = "2m"
            elif 156 <= f <= 174: props["bande"] = "marine"
            elif 430 <= f <= 440: props["bande"] = "70cm"
            elif 446 <= f <= 447: props["bande"] = "PMR446"
            elif 1200 <= f <= 1300: props["bande"] = "23cm"
        except ValueError:
            pass

    # Appliquer les valeurs par défaut du modèle (ne surcharge PAS les valeurs déjà définies)
    defauts = mapping.get("defauts", {})
    for key, val in defauts.items():
        if key not in props or not props.get(key):
            props[key] = val

    return props


def props_to_frontmatter(props):
    """Génère le frontmatter YAML depuis les propriétés."""
    lines = ["---"]
    for key, val in props.items():
        if isinstance(val, list):
            lines.append(f"{key}:")
            for item in val:
                lines.append(f"  - {item!r}")
        elif isinstance(val, str):
            if any(c in val for c in [":", "#", "[", "]", "{", "}", ">", "|", "'", '"']):
                lines.append(f'{key}: "{val}"')
            else:
                lines.append(f"{key}: {val}")
        else:
            lines.append(f"{key}: {val}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def slug_from_props(props):
    """Génère un slug de nom de fichier depuis les propriétés."""
    nom = props.get("nom", props.get("freq", props["id"]))
    freq = props.get("freq", "")
    bande = props.get("bande", "")
    return slugify(f"{freq} {nom} {bande}-{props['id']}")


def write_note(props):
    """Écrit une note Obsidian dans le dossier frequences."""
    slug = slug_from_props(props)
    fname = f"{slug}.md"
    fpath = os.path.join(NOTE_DIR, fname)

    frontmatter = props_to_frontmatter(props)
    body = f"# {props.get('nom', props.get('freq', 'Fréquence'))}\n\n"
    body += f"**Fréquence :** {props.get('freq', '')}\n\n"

    # Champs optionnels
    for key, label in [("mode", "Mode"), ("tone", "Tonalité"),
                        ("bande", "Bande"), ("usage", "Usage"),
                        ("dep", "Département"), ("power", "Puissance"),
                        ("step", "Step"), ("offset", "Offset"),
                        ("notes", "Notes")]:
        if key in props and props[key]:
            body += f"**{label} :** {props[key]}\n"

    body += f"\n_Source : {props.get('source', 'inconnue')}_\n"

    content = frontmatter + body + "\n"

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)

    return fname


def main():
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    csv_path = sys.argv[1]
    modele = sys.argv[2]

    # Options
    prefix = "f"
    start = 1
    for i, arg in enumerate(sys.argv[3:]):
        if arg == "--prefix" and i + 4 < len(sys.argv):
            prefix = sys.argv[i + 4]
        if arg == "--start" and i + 4 < len(sys.argv):
            start = int(sys.argv[i + 4])

    if not os.path.exists(csv_path):
        print(f"ERREUR: Fichier CSV introuvable: {csv_path}", file=sys.stderr)
        sys.exit(1)

    # Charger le mapping
    mapping = load_mapping(modele)
    delim = mapping.get("delimiteur", ",")
    encoding = mapping.get("encoding", "utf-8")
    has_header = mapping.get("has_header", True)

    # Lire le CSV
    with open(csv_path, "r", encoding=encoding) as f:
        reader = csv.reader(f, delimiter=delim)
        rows = list(reader)

    if not rows:
        print("ERREUR: CSV vide", file=sys.stderr)
        sys.exit(1)

    if has_header:
        header = rows[0]
        data = rows[1:]
    else:
        header = []
        data = rows

    print(f"📄 CSV lu : {csv_path}")
    print(f"📋 Mapping : {mapping.get('nom', modele)}")
    print(f"🔢 Lignes de données : {len(data)}")
    print()

    next_id = get_next_id(prefix, start)
    created = []

    for i, row in enumerate(data):
        if not any(cell.strip() for cell in row):
            continue  # ligne vide

        freq_id = f"{prefix}-{next_id:03d}"
        props = row_to_note(row, mapping, freq_id)
        fname = write_note(props)
        created.append(fname)
        print(f"  ✓ {freq_id} → {fname}")
        next_id += 1

    print()
    print(f"✅ {len(created)} notes créées dans {NOTE_DIR}")
    print("Pense à lancer un scan Syncthing si besoin.")
    return 0


if __name__ == "__main__":
    sys.exit(main())