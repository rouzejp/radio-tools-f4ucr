#!/usr/bin/env python3
"""
Export notes Obsidian (format universel) → CSV pour un modèle radio.

Usage:
    python export.py <modele> [--output fichier.csv] [--filter "bande=2m"]

Exemples:
    python export.py baofeng-uv5r
    python export.py baofeng-uv5r --output /tmp/uv5r_export.csv
    python export.py tyt-md380 --filter "bande=70cm"

Le mapping du modèle est cherché dans modeles/<modele>.yaml.
"""

import csv
import os
import sys
import re
import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RADIO_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
FREQ_DIR = os.path.join(RADIO_DIR, "frequences")
MODELES_DIR = os.path.join(RADIO_DIR, "modeles")


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

    return mapping


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


def props_to_row(props, mapping):
    """Convertit les propriétés d'une note en ligne CSV selon le mapping."""
    # Déterminer le nombre de colonnes
    max_idx = 0
    for col in mapping.get("colonnes", []):
        if col["index"] > max_idx:
            max_idx = col["index"]

    row = [""] * (max_idx + 1)

    for col in mapping["colonnes"]:
        idx = col["index"]
        cible = col.get("cible", "ignore")
        col_name = col.get("nom", f"col{idx}")
        type_spec = col.get("type", "string")

        if cible == "ignore":
            # Essayer de trouver une valeur par défaut ou laisser vide
            row[idx] = ""
            continue

        # Récupérer la valeur depuis les props
        if cible in props and props[cible]:
            val = props[cible]
        else:
            row[idx] = ""
            continue

        # Application des transformations inverses
        transforms = mapping.get("transformations", {})
        if cible in transforms:
            # Inverser le mapping de transformation
            inverse = {v: k for k, v in transforms[cible].items()}
            val = inverse.get(val, val)

        # Formater selon le type
        row[idx] = format_value(val, type_spec) if val else ""

    return row


def format_value(val, type_spec):
    """Formate une valeur selon le type attendu par le modèle."""
    if type_spec == "mhz":
        # S'assurer que c'est au format décimal standard
        try:
            f = float(str(val).replace(",", "."))
            return f"{f:.6f}"
        except (ValueError, TypeError):
            return str(val)

    if type_spec == "hz_optional":
        try:
            f = float(str(val).replace(",", "."))
            return f"{f:.0f}"
        except (ValueError, TypeError):
            return str(val)

    return str(val)


def matches_filter(props, filters):
    """Vérifie si une note correspond aux filtres (clé=valeur)."""
    for f in filters:
        if "=" not in f:
            continue
        key, expected = f.split("=", 1)
        key = key.strip()
        expected = expected.strip()

        val = props.get(key, "")
        if str(val).strip() != expected:
            return False
    return True


def generate_header(mapping):
    """Génère la ligne d'en-tête CSV à partir du mapping."""
    max_idx = 0
    for col in mapping.get("colonnes", []):
        if col["index"] > max_idx:
            max_idx = col["index"]
    header = [""] * (max_idx + 1)
    for col in mapping.get("colonnes", []):
        idx = col["index"]
        header[idx] = col.get("nom", f"col{idx}")
    return header


def infer_bande(freq_str):
    """Devine la bande à partir d'une fréquence si non spécifiée."""
    if not freq_str:
        return ""
    try:
        f = float(str(freq_str).replace(",", "."))
    except ValueError:
        return ""

    if 28 <= f <= 30:
        return "10m"
    if 50 <= f <= 54:
        return "6m"
    if 108 <= f <= 137:
        return "air"
    if 144 <= f <= 148:
        return "2m"
    if 156 <= f <= 174:
        return "marine"
    if 430 <= f <= 440:
        return "70cm"
    if 446 <= f <= 447:
        return "PMR446"
    if 1200 <= f <= 1300:
        return "23cm"
    return ""


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    modele = sys.argv[1]
    output = None
    filters = []

    for i, arg in enumerate(sys.argv[2:]):
        if arg == "--output" and i + 3 < len(sys.argv):
            output = sys.argv[i + 3]
        if arg == "--filter" and i + 3 < len(sys.argv):
            filters.append(sys.argv[i + 3])

    # Charger le mapping
    mapping = load_mapping(modele)

    # Lire les notes
    notes = read_all_notes()
    if not notes:
        print("Aucune note trouvée dans frequences/")
        sys.exit(0)

    # Appliquer les filtres
    if filters:
        notes = [(f, p) for f, p in notes if matches_filter(p, filters)]
        print(f"🔍 Filtres appliqués : {', '.join(filters)}")

    if not notes:
        print("Aucune note ne correspond aux filtres.")
        sys.exit(0)

    # Construire la sortie
    has_header = mapping.get("has_header", True)
    delim = mapping.get("delimiteur", ",")

    rows = []
    if has_header:
        rows.append(generate_header(mapping))

    for fname, props in notes:
        row = props_to_row(props, mapping)
        rows.append(row)

    # Appliquer encoding
    encoding = mapping.get("encoding", "utf-8")

    if output:
        with open(output, "w", encoding=encoding, newline="") as f:
            writer = csv.writer(f, delimiter=delim)
            writer.writerows(rows)
        print(f"✅ Exporté {len(notes)} fréquences vers : {output}")
    else:
        # Sortie par défaut : générer un nom
        if not os.path.exists(os.path.join(RADIO_DIR, "exports")):
            os.makedirs(os.path.join(RADIO_DIR, "exports"), exist_ok=True)
        output = os.path.join(RADIO_DIR, "exports", f"{modele}_{len(notes)}freq.csv")
        with open(output, "w", encoding=encoding, newline="") as f:
            writer = csv.writer(f, delimiter=delim)
            writer.writerows(rows)
        print(f"✅ Exporté {len(notes)} fréquences vers : {output}")

    print(f"📋 Modèle : {mapping.get('nom', modele)}")
    print(f"🔢 Total lignes : {len(rows) - (1 if has_header else 0)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())