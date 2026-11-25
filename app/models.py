"""Datenzugriff für Reservationen (Insert/Query), keine Geschäftslogik."""

import sqlite3
from datetime import datetime, timezone

PFLICHTFELDER = ("kontaktperson", "email", "raum", "datum", "beginn", "ende", "verpflegung")


def insert_reservation(conn: sqlite3.Connection, daten: dict, status: str) -> int:
    """Legt eine neue Reservation an. `daten` enthält bereits validierte Formularwerte."""
    cur = conn.execute(
        """
        INSERT INTO reservationen (
            kontaktperson, email, organisation, telefonnummer, titel, veranstaltungsart,
            raum, datum, beginn, ende, anzahl_personen, bestuhlung, verpflegung,
            bemerkungen, eingang_zeitpunkt, status, restaurant_informiert
        ) VALUES (
            :kontaktperson, :email, :organisation, :telefonnummer, :titel, :veranstaltungsart,
            :raum, :datum, :beginn, :ende, :anzahl_personen, :bestuhlung, :verpflegung,
            :bemerkungen, :eingang_zeitpunkt, :status, 0
        )
        """,
        {
            "kontaktperson": daten["kontaktperson"],
            "email": daten["email"],
            "organisation": daten.get("organisation"),
            "telefonnummer": daten.get("telefonnummer"),
            "titel": daten.get("titel"),
            "veranstaltungsart": daten.get("veranstaltungsart"),
            "raum": daten["raum"],
            "datum": daten["datum"],
            "beginn": daten["beginn"],
            "ende": daten["ende"],
            "anzahl_personen": daten.get("anzahl_personen"),
            "bestuhlung": daten.get("bestuhlung"),
            "verpflegung": 1 if daten["verpflegung"] else 0,
            "bemerkungen": daten.get("bemerkungen"),
            "eingang_zeitpunkt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": status,
        },
    )
    conn.commit()
    return cur.lastrowid


def get_confirmed_for_room_date(conn: sqlite3.Connection, raum: str, datum: str) -> list[sqlite3.Row]:
    """Alle bestätigten Reservationen für einen Raum an einem Datum (für die Konfliktprüfung)."""
    return conn.execute(
        "SELECT id, beginn, ende FROM reservationen WHERE raum = ? AND datum = ? AND status = 'bestaetigt'",
        (raum, datum),
    ).fetchall()


def mark_restaurant_informiert(conn: sqlite3.Connection, reservation_id: int) -> None:
    conn.execute(
        "UPDATE reservationen SET restaurant_informiert = 1 WHERE id = ?", (reservation_id,)
    )
    conn.commit()


def list_all(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM reservationen ORDER BY datum, beginn, raum"
    ).fetchall()


def fehlende_pflichtfelder(daten: dict) -> list[str]:
    """Liefert die Namen aller nicht ausgefüllten Pflichtfelder."""
    fehlend = []
    for feld in PFLICHTFELDER:
        wert = daten.get(feld)
        if wert is None or (isinstance(wert, str) and not wert.strip()):
            fehlend.append(feld)
    return fehlend
