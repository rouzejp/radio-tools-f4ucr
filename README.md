# Radio Tools F4UCR

> Outils de gestion de fréquences radioamateurs — import/export CSV multi-format, carnet de trafic, et base de connaissances Obsidian.

Un ensemble d'outils pour gérer, convertir et documenter les fréquences radio, quel que soit le modèle d'émetteur. Chaque radio a son propre format CSV (Baofeng, TIDRADIO TD-H3, TD-H9, Odmaster…) — ces scripts unifient le tout.

## Fonctionnalités

### 🔄 Import/Export CSV multi-format

Chaque modèle radio a son propre format de fichier CSV. Au lieu de réécrire les scripts à chaque changement de radio, une architecture à deux couches :

- **Fichiers de mapping YAML** (`modeles/`) — décrivent la structure CSV de chaque modèle (colonnes, séparateur, ordre)
- **Scripts Python** (`scripts/`) — lisent ces mappings et transforment automatiquement

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  import.py   │────▶│  Fichier     │────▶│  export.py   │
│  (CSV → YAML)│     │  YAML        │     │  (YAML → CSV)│
└──────────────┘     │  unifié      │     └──────────────┘
                     └──────────────┘
```

**Modèles supportés :**

| Modèle | Mapping | Script d'export |
|--------|---------|-----------------|
| Baofeng UV-5R | `baofeng-uv5r.yaml` | `export.py` |
| TIDRADIO TD-H3 | `tidradio-td-h3.yaml` | `export.py` |
| TIDRADIO TD-H9 | `tidradio-td-h9.yaml` | `export-h9.py` |
| TIDRADIO TD-H9 (Odmaster) | `tidradio-td-h9.yaml` | `export-odmaster-h9.py` |

### 📖 Carnet de trafic

Un carnet de trafic au format Markdown, conçu pour être utilisé avec un assistant IA (Hermes). Les entrées se font par message structuré :

```
SWL: 145.637, FM, F5KTR, Relais R1 du Neulois — reçu 59
OM:  145.750, FM, F1NBC, QSO sur le relais de Sorède
CB:  19, AM, Momo, Bon traffic sur la nationale
```

L'assistant parse automatiquement, horodate, et crée les wikilinks vers les fiches OM et fréquences.

### 🗂️ Base de fréquences

126 fiches de fréquences individuelles au format Markdown avec frontmatter YAML structuré :

```yaml
---
id: td3-063
source: tidradio-td-h3
created: 2026-06-11
tags: [2m, rrf, relais]
freq: 145.287
mode: FM
name: RRF 09
loc: Perpignan
---
```

Chaque fiche est liée par wikilinks aux autres notes (carnet, OM, documentation).

## Structure du dépôt

```
radio-tools-f4ucr/
├── README.md
├── scripts/
│   ├── import.py              # Import CSV → YAML unifié
│   ├── export.py              # Export YAML → CSV (UV-5R, TD-H3)
│   ├── export-h9.py           # Export TD-H9
│   ├── export-odmaster-h9.py  # Export Odmaster TD-H9
│   ├── test_baofeng.csv       # Exemple CSV Baofeng
│   ├── tidradio-td-h3.csv     # Exemple CSV TD-H3
│   ├── baofeng-uv5r_7freq.csv # Export exemple (7 fréquences)
│   ├── tidradio-td-h9_115freq.csv
│   └── odmaster-td-h9_115freq.csv
├── modeles/
│   ├── baofeng-uv5r.yaml
│   ├── tidradio-td-h3.yaml
│   └── tidradio-td-h9.yaml
├── frequences/
│   ├── _index.md              # Index Dataview
│   ├── 145637-relais-f5ktr-2m-f-001.md
│   ├── 145750-f1nbc-2m-f-002.md
│   ├── 146520-simpa-2m-f-003.md
│   ├── 431050-f1zfg-70cm-f-004.md
│   ├── 145525-urgence-2m-f-005.md
│   ├── 144863-f5kff-2m-f-006.md
│   ├── 433400-f1zhp-70cm-f-007.md
│   └── ... (126 fiches dans le vault complet)
├── carnet-de-trafic/
│   └── carnet-de-trafic.md    # Template de carnet
└── docs/
    ├── tidradio-td-h3.md      # Documentation TD-H3
    └── APRS-TD-H9-F4UCR.md    # APRS sur TD-H9
```

## Utilisation

### Importer un CSV dans le format unifié

```bash
python3 scripts/import.py mon_fichier.csv
```

Le script détecte automatiquement le modèle d'après la structure du CSV et le mapping YAML correspondant.

### Exporter vers un format spécifique

```bash
python3 scripts/export.py --modele tidradio-td-h3 --sortie frequences_td-h3.csv
```

### Ajouter une entrée au carnet de trafic

Via l'assistant Hermes, un simple message suffit :

```
SWL: 145.637, FM, F5KTR, Reçu 59 depuis Sorède
```

## Prérequis

- Python 3.8+
- Optionnel : [Hermes Agent](https://hermes-agent.nousresearch.com) pour le parsing automatique du carnet de trafic
- Optionnel : [Obsidian](https://obsidian.md) pour la base de connaissances

## Licence

Projet personnel — librement réutilisable et adaptable.

## Auteur

**F4UCR** (Jean-Paul Rouzé) — radioamateur, indicatif F4UCR.
