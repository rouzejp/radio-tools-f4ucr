---
title: Index des fréquences radio
type: index
source: radio
created: 2026-06-11
tags:
  - radio
  - hardware
---

Équipements : [[documentation/tidradio-td-h3|TIDRADIO TD-H3]], [[documentation/APRS-TD-H9-F4UCR|TIDRADIO TD-H9]]


# 📻 Index des fréquences radio

> `$= dv.current().file.name`

```dataview
TABLE
  freq as "Fréquence",
  nom as "Nom",
  bande as "Bande",
  usage as "Usage",
  dep as "Dépt",
  mode as "Mode",
  tone as "Tonalité",
  source as "Source"
FROM "84_Radio/frequences"
WHERE file.name != "_index"
SORT freq ASC
```

## Par bande

```dataview
TABLE rows.freq as "Fréquences", rows.nom as "Noms"
FROM "84_Radio/frequences"
WHERE file.name != "_index" AND bande
GROUP BY bande
SORT bande ASC
```

## Par usage

```dataview
TABLE rows.freq as "Fréquences", rows.nom as "Noms"
FROM "84_Radio/frequences"
WHERE file.name != "_index" AND usage
GROUP BY usage
SORT usage ASC
```

**Total :** `$= dv.pages('"84_Radio/frequences"').length - 1` fréquences référencées