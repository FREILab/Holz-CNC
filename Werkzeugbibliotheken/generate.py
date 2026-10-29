#!/usr/bin/env python3
"""Erzeugt die Werkzeugbibliotheken (Fusion 360 + Estlcam) für die Holz-CNC.

Geometrie kommt aus der SpeTool-Fusion-Datenbank, Schnittdaten aus den
SpeTool-Feed&Speed-PDFs (Chipload), beides in Quellen/, abgemindert für unsere
riemengetriebene X-Carve mit AMB FME-1050W. Werte nur hier ändern und neu
erzeugen:  python3 Werkzeugbibliotheken/generate.py
"""

import csv
import io
import json
import math
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPETOOL_DB = HERE / "Quellen" / "SpeTool-Fusion-360-Tool-File-Database-251015.json"
NAME = "Freilab_Holz-CNC"

# Herstellerwerte Chipload (mm/Zahn) aus den SpeTool-PDFs, Holz-Materialien.
# Multiplex (Birke) = Mittel aus Weich- und Hartholz.
IN = 25.4
UPCUT_1_4 = {"mdf": 0.008 * IN, "soft": 0.007 * IN, "hard": 0.006 * IN}
UPCUT_1_8 = {"mdf": 0.0045 * IN, "soft": 0.004 * IN, "hard": 0.0035 * IN}
# O-Flute-PDF hat kein Hartholz: Verhältnis Hart/MDF aus der Spiral-Tabelle (0,75).
OFLUTE_1_4 = {"mdf": 0.01 * IN, "soft": 0.01 * IN, "hard": 0.0075 * IN}
OFLUTE_1_8 = {"mdf": 0.006 * IN, "soft": 0.006 * IN, "hard": 0.0045 * IN}
VBIT = {"mdf": 0.005 * IN, "soft": 0.002 * IN, "hard": 0.002 * IN}


def interpolate(a, b, da, db, d):
    return {k: a[k] + (b[k] - a[k]) * (d - da) / (db - da) for k in a}


def scaled(c, f):
    return {k: v * f for k, v in c.items()}


# Inventar (Reihenfolge = Werkzeugnummer). nof überschreibt fehlerhafte DB-Werte.
TOOLS = [
    {"id": "W04508", "name": "6mm Upcut 2Z", "chip": UPCUT_1_4},
    {"id": "W04901", "name": "6mm Schrupp-Upcut 3Z", "nof": 3,
     # Schruppfräser mit Spanbrecher, keine Herstellertabelle: 80 % Spiral-Chipload
     "chip": scaled(UPCUT_1_4, 0.8)},
    {"id": "W04502", "name": "4mm Upcut 2Z (8mm Schaft)",
     "chip": interpolate(UPCUT_1_8, UPCUT_1_4, 3.175, 6.35, 4.0)},
    {"id": "W03505", "name": "6mm O-Flute 1Z", "chip": OFLUTE_1_4},
    {"id": "W03501", "name": "3,175mm O-Flute 1Z", "chip": OFLUTE_1_8},
    {"id": "W06509", "name": "V-Bit 90° 3Z", "chip": VBIT, "vbit": True},
    {"id": "W06508", "name": "V-Bit 60° 3Z", "chip": VBIT, "vbit": True},
    # gerade Schneiden räumen schlechter aus: 80 % Spiral-Chipload
    {"id": "W04705", "name": "6mm Stirnfräser gerade 2Z", "chip": scaled(UPCUT_1_4, 0.8)},
]

# Maschinen-Abminderung: feed = rpm * Z * Chipload(Hersteller) * feed_factor.
# doc = Zustellung in x Durchmesser, stepover in x Durchmesser.
MATERIALS = [
    {"name": "Schaumstoff", "est": 1, "chip": "mdf", "rpm": 12000, "feed_factor": 1.0,
     "doc": 1.5, "stepover": 0.5, "plunge_max": 1000, "feed_max": 5000, "vdoc": 3.0},
    {"name": "MDF", "est": 2, "chip": "mdf", "rpm": 18000, "feed_factor": 0.4,
     "doc": 0.5, "stepover": 0.4, "plunge_max": 500, "feed_max": 3500, "vdoc": 2.0},
    {"name": "Multiplex", "est": 3, "chip": "multiplex", "rpm": 18000, "feed_factor": 0.35,
     "doc": 0.4, "stepover": 0.4, "plunge_max": 400, "feed_max": 3500, "vdoc": 1.5},
    {"name": "Hartholz", "est": 4, "chip": "hard", "rpm": 18000, "feed_factor": 0.3,
     "doc": 0.33, "stepover": 0.35, "plunge_max": 300, "feed_max": 3500, "vdoc": 1.0},
]


def chipload(tool, mat):
    c = tool["chip"]
    if mat["chip"] == "multiplex":
        return (c["soft"] + c["hard"]) / 2
    return c[mat["chip"]]


def cutting_data(tool, geo, mat):
    dc, lcf, nof = geo["DC"], geo["LCF"], geo["NOF"]
    rpm = mat["rpm"]
    fz = chipload(tool, mat) * mat["feed_factor"]
    feed = min(rpm * nof * fz, mat["feed_max"])
    feed = round(feed / 50) * 50
    plunge = round(min(feed / 3, mat["plunge_max"]) / 10) * 10
    if tool.get("vbit"):
        doc = min(mat["vdoc"], lcf)
        stepover = 0.1 * dc
    else:
        doc = min(mat["doc"] * dc, lcf - 1)
        stepover = mat["stepover"] * dc
    return {
        "rpm": rpm, "feed": feed, "plunge": plunge, "ramp": round(feed / 2 / 10) * 10,
        "doc": round(doc, 1), "stepover": round(stepover, 2), "fz": feed / (rpm * nof),
    }


def load_spetool():
    data = json.loads(SPETOOL_DB.read_text())["data"]
    found = {}
    for t in data:
        for tool in TOOLS:
            if f"SpeTool {tool['id']} " in t["description"]:
                found[tool["id"]] = t
    missing = [t["id"] for t in TOOLS if t["id"] not in found]
    if missing:
        raise SystemExit(f"nicht in SpeTool-DB: {missing}")
    return found


def fusion_preset(tool, mat, d, dc):
    return {
        "expressions": {
            "tool_coolant": "'disabled'",
            "tool_feedCutting": f"{d['feed']} mmpm",
            "tool_feedPlunge": f"{d['plunge']} mmpm",
            "tool_feedRamp": f"{d['ramp']} mmpm",
            "tool_spindleSpeed": f"{d['rpm']} rpm",
            "tool_stepdown": f"{d['doc']} mm",
            "tool_stepover": f"{d['stepover']} mm",
            "use_tool_stepdown": "true",
            "use_tool_stepover": "true",
        },
        # Fusion: f_n = Eintauchvorschub pro Umdrehung, sonst "missing required data"
        "f_n": d["plunge"] / d["rpm"],
        "f_z": d["fz"],
        "guid": str(uuid.uuid5(uuid.NAMESPACE_URL, f"freilab/{tool['id']}/{mat['name']}")),
        "material": {"category": "all", "query": "", "use-hardness": False},
        "n": d["rpm"],
        "n_ramp": d["rpm"],
        "name": mat["name"],
        "ramp-angle": 2,
        "stepdown": d["doc"],
        "stepover": d["stepover"],
        # Post-Prozessor kennt nur Flood/Off – alles andere bricht ab
        "tool-coolant": "disabled",
        "use-stepdown": True,
        "use-stepover": True,
        "v_c": math.pi * dc * d["rpm"] / 1000,
        "v_f": d["feed"],
        "v_f_leadIn": d["feed"],
        "v_f_leadOut": d["feed"],
        "v_f_plunge": d["plunge"],
        "v_f_ramp": d["ramp"],
        "v_f_transition": d["feed"],
    }


def build(db):
    fusion, rows, table = [], [], []
    for number, tool in enumerate(TOOLS, start=1):
        src = json.loads(json.dumps(db[tool["id"]]))
        # "tool-block": null aus der SpeTool-DB -> Fusion: "missing required data"
        src.pop("tool-block", None)
        geo = src["geometry"]
        if "nof" in tool:
            geo["NOF"] = tool["nof"]
        if "TA" in geo:
            geo["TA"] = round(geo["TA"], 6)
        desc = f"SpeTool {tool['id']} {tool['name']}"
        src.update({
            "BMC": "carbide",
            "vendor": "SpeTool",
            "product-id": tool["id"],
            "description": desc,
            "expressions": fusion_expressions(src, geo, desc, tool["id"]),
            "guid": str(uuid.uuid5(uuid.NAMESPACE_URL, f"freilab/{tool['id']}")),
        })
        src["post-process"].update({"number": number, "diameter-offset": number,
                                    "length-offset": number, "manual-tool-change": True})
        presets = []
        for mat in MATERIALS:
            d = cutting_data(tool, geo, mat)
            presets.append(fusion_preset(tool, mat, d, geo["DC"]))
            rows.append(estlcam_row(tool, geo, mat, d, number))
            table.append((number, tool, geo, mat, d))
        src["start-values"] = {"presets": presets}
        fusion.append(src)
    rows.sort(key=lambda r: float(r["Number"]))
    return {"data": fusion, "version": 37}, rows, table


def fusion_expressions(src, geo, desc, product_id):
    # Vollständiger Satz aus der Geometrie: fehlende Längen (z. B. W04901, W04502
    # in der SpeTool-DB) markiert Fusion sonst als "missing required data".
    mm = lambda v: f"{v:g} mm"
    expr = {
        "tool_description": f"'{desc}'",
        "tool_diameter": mm(geo["DC"]),
        "tool_shaftDiameter": mm(geo["SFDM"]),
        "tool_fluteLength": mm(geo["LCF"]),
        "tool_shoulderLength": mm(geo["shoulder-length"]),
        "tool_bodyLength": mm(geo["LB"]),
        "tool_overallLength": mm(geo["OAL"]),
        "tool_numberOfFlutes": str(geo["NOF"]),
        "tool_material": "'carbide'",
        "tool_vendor": "'SpeTool'",
        "tool_productId": f"'{product_id}'",
        "tool_productLink": f"'{src['product-link']}'",
        "tool_unit": "'millimeters'",
    }
    if "TA" in geo:
        expr["tool_taperAngle"] = f"{geo['TA']:g} degrees"
    return expr


ESTL_HEADER = ("Name;Paramset;Type;Suitability;Number;Diameter;Angle;Tip_Dia;Offset;R_Edge;"
               "H_Cut;Flutes;Dpp;Plunge_Angle;F;Fz;Rpm;Dpp_F;F_F;Fz_F;Rpm_F;Dpp_D;Peck;Fz_D;"
               "Rpm_D;Stepover;Step_Height;T_Stepover;T_Width;T_Osc;Pitch;IT_D1;OT_D1;IT_D2;"
               "OT_D2;Cool_Flood;Cool_Mist;Comment;Image").split(";")


def estlcam_row(tool, geo, mat, d, number):
    # Estlcam kennt nur einen Parametersatz pro Werkzeug: ein Eintrag je Material.
    angle = 2 * geo["TA"] if tool.get("vbit") else 90
    f = lambda v: f"{v:.5f}"
    row = dict.fromkeys(ESTL_HEADER, "")
    row.update({
        "Name": f"{mat['name']} - {tool['name']} - {tool['id']}",
        "Type": "Normal",
        "Number": f(mat["est"] * 10 + number),
        "Diameter": f(geo["DC"]),
        "Angle": f(round(angle)),
        "Tip_Dia": f(geo.get("tip-diameter", 0)),
        "Offset": f(0), "R_Edge": f(0),
        "H_Cut": f(geo["LCF"]),
        "Flutes": f(geo["NOF"]),
        "Dpp": f(d["doc"]),
        "Plunge_Angle": f(20),
        "F": f(d["feed"]),
        "Fz": f(d["plunge"]),
        "Rpm": f(d["rpm"]),
        "Peck": f(1),
        "Stepover": f(round(100 * d["stepover"] / geo["DC"])),
        "Step_Height": f(0.1), "T_Stepover": f(0), "T_Width": f(50), "T_Osc": f(0),
        "Pitch": f(1), "IT_D1": f(1), "OT_D1": f(1), "IT_D2": f(1), "OT_D2": f(1),
        "Cool_Flood": f(0), "Cool_Mist": f(0),
        "Comment": f"Fraese auf {d['rpm']} U/min stellen",
    })
    return row


def write_markdown(table):
    lines = [
        "# Schnittdaten Holz-CNC", "",
        "Erzeugt von `generate.py` – nicht von Hand bearbeiten.", "",
        "| T | Fräser | Material | U/min | Vorschub (mm/min) | Eintauchen (mm/min) "
        "| Zustellung (mm) | Seitl. Zustellung (mm) | Chipload (mm/Z) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for number, tool, geo, mat, d in table:
        lines.append(
            f"| {number} | {tool['id']} {tool['name']} | {mat['name']} | {d['rpm']} | {d['feed']} "
            f"| {d['plunge']} | {d['doc']:g} | {d['stepover']:g} | {d['fz']:.3f} |")
    (HERE / "Schnittdaten.md").write_text("\n".join(lines) + "\n")


def main():
    lib, rows, table = build(load_spetool())
    payload = json.dumps(lib, indent=2, ensure_ascii=False) + "\n"
    (HERE / f"{NAME}_Fusion.json").write_text(payload)

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=ESTL_HEADER, delimiter=";", lineterminator="\r\n")
    w.writeheader()
    w.writerows(rows)
    (HERE / f"{NAME}_Estlcam.csv").write_text(buf.getvalue(), encoding="utf-8-sig", newline="")
    write_markdown(table)
    print(f"{len(lib['data'])} Werkzeuge, {len(rows)} Estlcam-Einträge")


if __name__ == "__main__":
    main()
