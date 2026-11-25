"""Export bestätigter Reservationen in ein zu Reservationsliste.xlsx kompatibles Format.

Spalten entsprechen exakt der Original-Tabelle 'Reservationen' aus
docs/original-unterlagen/Reservationsliste.xlsx. Nur bestätigte Reservationen werden
exportiert, da im Original-Prozess nur diese in die Excel-Liste übertragen werden.
"""

import sqlite3
from pathlib import Path

from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo

STANDARD_ZIELPFAD = Path(__file__).resolve().parent.parent / "exports" / "Reservationsliste.xlsx"

SPALTEN = (
    "Raum",
    "Datum",
    "Beginn",
    "Ende",
    "Veranstaltung",
    "Organisation / Firma",
    "Kontaktperson",
    "E-Mail-Adresse",
    "Telefonnummer",
    "Verpflegung gewünscht",
)


def _zeile(reservation: sqlite3.Row) -> list:
    return [
        reservation["raum"],
        reservation["datum"],
        reservation["beginn"],
        reservation["ende"],
        reservation["titel"] or "",
        reservation["organisation"] or "",
        reservation["kontaktperson"],
        reservation["email"],
        reservation["telefonnummer"] or "",
        "Ja" if reservation["verpflegung"] else "Nein",
    ]


def exportiere_reservationsliste(conn: sqlite3.Connection, zielpfad: Path = STANDARD_ZIELPFAD) -> Path:
    bestaetigte = conn.execute(
        "SELECT * FROM reservationen WHERE status = 'bestaetigt' ORDER BY datum, beginn, raum"
    ).fetchall()

    arbeitsmappe = Workbook()
    blatt = arbeitsmappe.active
    blatt.title = "Reservationen"
    blatt.append(list(SPALTEN))
    for reservation in bestaetigte:
        blatt.append(_zeile(reservation))

    letzte_zeile = max(blatt.max_row, 1)
    tabelle = Table(displayName="Reservationen", ref=f"A1:J{letzte_zeile}")
    tabelle.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    blatt.add_table(tabelle)

    zielpfad.parent.mkdir(parents=True, exist_ok=True)
    arbeitsmappe.save(zielpfad)
    return zielpfad
