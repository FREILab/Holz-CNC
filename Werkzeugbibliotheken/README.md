# Werkzeugbibliotheken

Werkzeugbibliotheken für die vorhandenen Fräser ([`Fräserinventar.md`](Fräserinventar.md))
mit vier Material-Profilen: Hartholz, Multiplex, MDF, Schaumstoff (in dieser
Reihenfolge – das erste Preset ist in Fusion der Standard).
Alle Schnittdaten stehen in [`Schnittdaten.md`](Schnittdaten.md).

| Datei | Verwendung |
|---|---|
| `Freilab_Holz-CNC_Fusion.json` | Fusion 360: Tool Library → Import. 14 Werkzeuge (T1–T14) mit je vier Presets. T9/T10 sind generische Kugelfräser (8 und 6 mm), T11–T14 von HC-Maschinentechnik (Kugelfräser R0,5 / R1,5 / R5 und Hohlkehlfräser D22 R11). „Manual tool change“ ist aus, damit der Post `Tn M6` schreibt. |
| `Freilab_Holz-CNC_Estlcam.csv` | Estlcam 12: Werkzeuge → Import. Ein Eintrag je Werkzeug und Material (Nr. = Material × 100 + T; Hartholz = 1, Multiplex = 2, MDF = 3, Schaumstoff = 4; z. B. MDF/T1 = 301). |
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
| Hartholz | 18.000 | 38 % | 0,33 × Ø | 4.000 mm/min | 400 mm/min |
| Multiplex | 18.000 | 45 % | 0,4 × Ø | 4.000 mm/min | 500 mm/min |
| MDF | 18.000 | 50 % | 0,5 × Ø | 4.000 mm/min | 600 mm/min |
| Schaumstoff | 12.000 | 100 % | 1,5 × Ø | 5.000 mm/min | 1.000 mm/min |

Vorschub = Anteil des Hersteller-Chiploads. Die Werte sind ein Startpunkt:
nach Probeschnitten die Faktoren anpassen und neu erzeugen. (2026-11: Holz-Werte
nach Probeschnitten um ca. 25–30 % angehoben, vorher 30 / 35 / 40 %.)

Kugelfräser (T9/T10): generische Geometrie, seitliche Zustellung 10 % × Ø fürs
3D-Schlichten. Längen am echten Fräser prüfen.

HC-Maschinentechnik (T11–T14): Maße von den Produktseiten, Schnittdaten ohne
Herstellertabelle abgeleitet – vorsichtig anfahren. T11/T12 brauchen die
4-mm-Spannzange, T13 eine 10-mm-Spannzange. Beim Hohlkehlfräser (T14) ist die
Gesamtlänge (48 mm) nicht angegeben, nachmessen.

Die Drehzahl wird von Hand am Stellrad der AMB FME-1050W eingestellt.

## Fallstricke

- **Coolant:** muss in Fusion `disabled` sein. `freilab-fluidnc.cps` kennt nur
  Flood/Off; SpeTools Standard `air` bricht den Post-Prozessor ab.
- **Fusion „missing required data“:** kommt von `"tool-block": null` aus der
  SpeTool-Datenbank und von `f_n` ≠ Eintauchvorschub / Drehzahl. Beides
  behandelt `generate.py`.
- **Estlcam V-Bits:** als Typ `Normal` mit Winkel eingetragen. Der CSV-Typname
  für Gravierstichel ist nicht verifiziert – nach dem Import prüfen.
