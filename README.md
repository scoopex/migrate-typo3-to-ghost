# migrate-typo3-to-ghost

Ein sehr simples script das ich zum migrieren unserer Website von Typo3 auf Ghost genutzt habe.
Das ist alles ein bisschen "schmutzig", aber es war deutlich besser als das von Hand zu machen :-)

```
<checkout>
├── exported_ghost
│   └── exported-ghost.json
├── exported_typo3
│   ├── antrag-export.json
│   ├── buergerbeteiligung-export.json
│   ├── energie-export.json
│   ├── kinderfamilie-export.json
│   ├── media
│   │   └── <file>
│   ├── oekologieumwelt-export.json
│   ├── stadtplanung-export.json
│   ├── stellungnahme-export.json
│   ├── verkehr-export.json
│   ├── weiterethemen-export.json
│   └── witschaftfinanzen-export.json
├── import_ghost
│   ├── antrag.zip
│   └── stellungnahme.zip
├── LICENSE
└── README.md
```

# Migration

1. Auf dem bestehenden Ghost System die Tags anlegen
2. Einen Export via "Ghost"→"Labs"→"Settings"→"Export your Content" machen und diesen in `exported_ghost/exported-ghost.json` speichern
3. In Typo3 die Beiträge exportieren in einzelne Files: "Typo3"→"Liste"→"Kategorie"
   * "Download"→"All columns"→"JSON Format"→"full Metaformat"
   * Als Beitrags Export speichern in `exported_typo3/<typ>-export.json`
4. Die im Export eferenzierten Bilder downloaden
   * "Dateiliste"→"Ordner"→"Download"
5. Konvertierung vorbereiten
   * In der Datei "contenttypes.py" einen Typ implementieren (Klassenname: "<typ>" aus Schritt 3, Captitalize
   *  Den Typ in `convert.py`imporieren
6. Konvertieren
   ```
   # Reduktion auf einen aktuellen Beitrag
   ./convert.py -t antrag --limit 1
   # Reduktion auf einen bestimmten Beitrag
   ./convert.py -t antrag --slug-filter ".*Stellenplan.*"
   ```
7. Die erstellte ZIP Datei importieren:
   Einen Export via "Ghost"→"Labs"→"Settings"→"Import content"
8. Das Ergebnis prüfen, dannach die imporierten Artikel wieder löschen
9. Wenn alles passt, Schritte 6-7 ohne Limit ausführen
