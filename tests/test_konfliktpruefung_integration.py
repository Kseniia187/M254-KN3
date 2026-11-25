"""Testet das Zusammenspiel von Datenbank, Pflichtfeld-Prüfung und Verfügbarkeitsprüfung:
die erste vollständige Anfrage für einen Zeitraum gewinnt (First-come-first-served)."""

import pytest

from app import db, models
from app.availability import raum_ist_verfuegbar

RAUM = "Seminarraum 1"
DATUM = "2026-12-01"


@pytest.fixture
def conn(tmp_path):
    db_path = tmp_path / "test.db"
    db.init_db(db_path)
    connection = db.get_connection(db_path)
    yield connection
    connection.close()


def bearbeite_anfrage(conn, beginn, ende, kontaktperson):
    """Simuliert die automatische Prüfung einer Anfrage: verfügbar -> bestaetigt, sonst abgesagt."""
    bestehende = models.get_confirmed_for_room_date(conn, RAUM, DATUM)
    status = "bestaetigt" if raum_ist_verfuegbar(beginn, ende, bestehende) else "abgesagt"
    daten = {
        "kontaktperson": kontaktperson,
        "email": f"{kontaktperson}@example.org",
        "raum": RAUM,
        "datum": DATUM,
        "beginn": beginn,
        "ende": ende,
        "verpflegung": False,
    }
    return models.insert_reservation(conn, daten, status=status)


def test_zuerst_eingegangene_anfrage_gewinnt_bei_ueberschneidung(conn):
    bearbeite_anfrage(conn, "09:00", "11:00", "Anna")
    zweite_id = bearbeite_anfrage(conn, "10:00", "12:00", "Marco")

    alle = {row["kontaktperson"]: row["status"] for row in models.list_all(conn)}
    assert alle["Anna"] == "bestaetigt"
    assert alle["Marco"] == "abgesagt"
    assert conn.execute(
        "SELECT status FROM reservationen WHERE id = ?", (zweite_id,)
    ).fetchone()["status"] == "abgesagt"


def test_nicht_ueberschneidende_anfragen_werden_beide_bestaetigt(conn):
    bearbeite_anfrage(conn, "09:00", "10:00", "Anna")
    bearbeite_anfrage(conn, "10:00", "11:00", "Marco")

    alle = {row["kontaktperson"]: row["status"] for row in models.list_all(conn)}
    assert alle["Anna"] == "bestaetigt"
    assert alle["Marco"] == "bestaetigt"
