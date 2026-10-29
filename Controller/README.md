# Steuerung: PiBot V5.88 Ultra mit FluidNC

FluidNC-Konfiguration der Holz-CNC (Inventables X-Carve 1000 mm, XYYZ) auf einem
PiBot V5.88 Ultra mit 4× PiBot SilentStep TMC5160 V5 (SPI unabhängig, eigene
CS-Leitung pro Achse). Fräse: AMB FME-1050W, ein/aus über die Relaiskette im
Schaltkasten.

Verdrahtung und Schnittstelle zum Schaltkasten:
[`../HW/Verdrahtung.md`](../HW/Verdrahtung.md).

## Dateien

| Datei/Ordner | Inhalt |
|---|---|
| `config.yaml` | Produktiv-Konfiguration, Referenzfahrt über Endschalter, OLED/I2C entfernt |
| `config_door.yaml` | Variante mit Schutztür (`gpio.48`, ohne `:low`) und Z-Parken |
| `examples/` | Inbetriebnahme-Entwürfe, Bisect-/Recovery-Konfigurationen, Beispiel von PiBot |
| `postprocessors/` | Fusion-Postprozessoren; `freilab-fluidnc.cps` ist unserer |
| `tools/` | FluidNC-Validator und JSON-Schema (aus bdring/FluidNC) |
| `firmware/` | Firmware-Builds, Recovery, TMC-SPI-Patch, Issue-Texte (englisch) |
| `tests/` | Regressionstest für den TMC-SPI-Patch (braucht `FluidNC/`-Checkout) |
| `legacy/` | GRBL-1.1h-Einstellungen der alten X-Carve-Steuerung |
| `AGENTS.md` | Arbeitsnotizen für KI-Agenten (englisch) |

Nicht in diesem Repo (eigene Klone, werden separat gepflegt): der
FluidNC-Firmware-Checkout `FluidNC/`, `fluidnc-config-files`, FluidDial und
FigUI. Pfade wie `FluidNC/.pio/...` in `firmware/` und `AGENTS.md` beziehen
sich auf diese lokalen Checkouts.

## Kinematik (16 Mikroschritte)

| Achse | Schritte/mm | Verfahrweg | max. Geschwindigkeit | Beschleunigung |
|---|---|---|---|---|
| X | 53,333 | 760 mm | 10000 mm/min | 300 mm/s² |
| Y | 53,333 | 940 mm | 10000 mm/min | 300 mm/s² |
| Z | 408 | 156 mm | 1500 mm/min | 150 mm/s² |

## Referenzfahrt

Zyklus 1 = Z (nach oben, +Z), Zyklus 2 = X und Y (nach −X/−Y, vorne links).
`soft_limits: true`; nach dem Referenzieren X/Y = 0 und Z = 156.
`must_home: false` – trotzdem **vor jedem Job und nach jedem Not-Aus `$H`**.
Soft-Limits umschalten: `$20=0/1`.

## Spindel

Spindeltyp `Relay` auf `gpio.46` (5-V-Header) → X9 → K5 im Schaltkasten.
`M3 S>0` = ein, `M5` = aus, aus bei Alarm (`off_on_alarm: true`). Die
Drehzahl der AMB FME-1050W wird am Stellrad der Fräse eingestellt.

Niemals über `gpio.6` schalten: das ist der 0–10-V-Analogausgang für VFDs
(Op-Amp-Stufe), kein Logikausgang.

## Schutztür und Z-Parken

**Nur in `config_door.yaml`.** `config.yaml` hat keinen Tür-Eingang und
keine Parkfunktion; die Spindel-Verzögerungen stehen dort auf `0.000`.

`control.safety_door_pin: gpio.48` nutzt den freien C-Endschalter-Eingang.
Im spannungslosen Zustand einen potentialfreien Kontakt zwischen **Signal**
und **GND** dieses Eingangs anschließen: geschlossen bei geschlossener Tür,
offen bei offener Tür. SW-VCC am Header frei lassen, den SW-VCC-Jumper auf der
Platine gesteckt lassen. Der Optokoppler invertiert, daher `gpio.48` ohne
`:low`. Ein abgezogenes Kabel löst ebenfalls einen Tür-Stopp aus.

Ablauf beim Öffnen: nach dem Feed-Hold fährt Z bei laufender Fräse bis zu 5 mm
mit 250 mm/min hoch, dann wird die Fräse abgeschaltet, die Auslaufzeit
abgewartet und Z mit 800 mm/min auf **Maschinen-Z = 150 mm** gefahren. X/Y
bleiben stehen. Ab Z ≥ 150 wird nur abgeschaltet. **Geparkt wird nur, wenn Z
referenziert ist.**

Tür schließen allein setzt nicht fort; erst **Cycle Start / Resume**: Z fährt
zurück, die Fräse läuft mit Anlaufzeit an, dann geht es langsam auf die
unterbrochene Position und der Job läuft weiter. An- und Auslaufzeit sind auf
je **5000 ms** bei `S1000` eingestellt. FluidNC skaliert die Zeiten mit S, daher
für Zeittests `M3 S1000` verwenden und die tatsächlichen Zeiten messen.

Vor dem Fräsen:

1. Bei getrennter Fräse prüfen: Tür zu → Eingang inaktiv; Tür offen oder Kabel
   ab → aktiv.
2. Referenzieren, sicher unter Z = 150 positionieren und einen Luftschnitt mit
   Tür auf/Resume fahren. Richtung, Parkhöhe und Rückweg prüfen.
3. Bei geschlossener Einhausung Abschalten/Wiederanlauf der Fräse prüfen. Eine
   Wartezeit beweist keinen Stillstand: vor dem Eingreifen warten, bis das
   Werkzeug steht.

Das ist eine Firmware-Verriegelung, **kein sicherheitsgerichteter Not-Halt und
keine Zuhaltung**.

## Firmware-Stand (2026-10-24)

Installiert ist upstream FluidNC `main` Commit `c82d217` (`wifi_s3`, meldet
`v4.1.1 (HEAD-c82d217)`). Der TMC-SPI-Startfehler ist upstream behoben; alle
vier Treiber-Tests laufen durch, die Konfiguration lädt.

**Bekanntes Problem:** Das Laden von ca. 1 MB G-Code von der SD-Karte über das
Web-UI (WebDAV) bringt die Steuerung zum Absturz. Danach läuft sie im Fallback
`Default (Test Drive)` / Alarm. Gemeldet als
[bdring/FluidNC#1931](https://github.com/bdring/FluidNC/issues/1931). Den
Fallback-Alarm nicht mit `$X` umgehen; nach sauberer Wiederherstellung neu
referenzieren. Als Rückfallebene ist die offizielle v4.0.3 dokumentiert, mit
der das Laden von SD funktioniert hat.

Details, Prüfsummen, Backups und Historie: [`firmware/README.md`](firmware/README.md).

## Änderungen validieren

Nach jeder Änderung prüfen:

```sh
cd Controller
python3 -m venv .venv && .venv/bin/pip install pyyaml jsonschema   # einmalig
.venv/bin/python tools/validate_fluidnc_config.py --no-auto-install \
  --schema tools/fluidnc-config-schema.json --permissive config.yaml
```

Regeln für den Parser auf dem Gerät (das Schema prüft sie nicht):

- Keine Kommentare hinter Werten, nur in eigenen Zeilen.
- Zahlenwerte mit Dezimalstellen schreiben (`5000.000`, nicht `5000`).
- Vor dem Hochladen eine funktionierende Konfiguration auf dem Gerät behalten.

## Links

- FluidNC-Wiki: http://wiki.fluidnc.com/en/config/overview
- PiBot V5.88 Ultra: https://wiki.pibot.com/doku.php?id=pibot_cnc_laser_series:v588_ultra:introduction:start
- TMC5160 SilentStep V5: https://wiki.pibot.com/doku.php?id=pibot_cnc_laser_series:silentstep_tmc5160_v5:start
- Pendant V4.2: https://wiki.pibot.com/doku.php?id=pibot_cnc_laser_series:cnc_pendant_v42:start
