# Werkzeugbibliotheken

Werkzeugbibliotheken für die vorhandenen Fräser ([`Fräserinventar.md`](Fräserinventar.md))
mit vier Material-Profilen: Schaumstoff, MDF, Multiplex, Hartholz.
Alle Schnittdaten stehen in [`Schnittdaten.md`](Schnittdaten.md).

| Datei | Verwendung |
|---|---|
| `Freilab_Holz-CNC_Fusion.json` | Fusion 360: Tool Library → Import. 8 Werkzeuge (T1–T8) mit je vier Presets. |
| `Freilab_Holz-CNC_Estlcam.csv` | Estlcam 12: Werkzeuge → Import. Ein Eintrag je Werkzeug und Material (Nr. = Material × 10 + T, z. B. MDF/T1 = 21). |
| `generate.py` | Erzeugt alle drei Dateien. Werte nur hier ändern. |
| `Quellen/` | SpeTool-Fusion-Datenbank (Geometrie) und Feed&Speed-PDFs (Chipload). |

```sh
python3 Werkzeugbibliotheken/generate.py
```

## Schnittdaten

Die Herstellerwerte gelten für steife Maschinen. Für unsere riemengetriebene
Fräse sind sie abgemindert (Faktoren in `generate.py`, `MATERIALS`):

| Material | U/min | Vorschub | Zustellung | max. Vorschub | max. Eintauchen |
|---|---|---|---|---|---|
| Schaumstoff | 12.000 | 100 % | 1,5 × Ø | 5.000 mm/min | 1.000 mm/min |
| MDF | 18.000 | 40 % | 0,5 × Ø | 3.500 mm/min | 500 mm/min |
| Multiplex | 18.000 | 35 % | 0,4 × Ø | 3.500 mm/min | 400 mm/min |
| Hartholz | 18.000 | 30 % | 0,33 × Ø | 3.500 mm/min | 300 mm/min |

Vorschub = Anteil des Hersteller-Chiploads. Die Werte sind ein Startpunkt:
nach Probeschnitten die Faktoren anpassen und neu erzeugen.

Die Drehzahl wird von Hand am Stellrad der AMB FME-1050W eingestellt.

## Fallstricke

- **Coolant:** muss in Fusion `disabled` sein. `freilab-fluidnc.cps` kennt nur
  Flood/Off; SpeTools Standard `air` bricht den Post-Prozessor ab.
- **Fusion „missing required data“:** kommt von `"tool-block": null` aus der
  SpeTool-Datenbank und von `f_n` ≠ Eintauchvorschub / Drehzahl. Beides
  behandelt `generate.py`.
- **Estlcam V-Bits:** als Typ `Normal` mit Winkel eingetragen. Der CSV-Typname
  für Gravierstichel ist nicht verifiziert – nach dem Import prüfen.
