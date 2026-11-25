"""SQLite-Verbindung und Schema für die Raumreservationen."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "reservationen.db"

RAEUME = ("Seminarraum 1", "Seminarraum 2", "Seminarraum 3")
STATUS_WERTE = ("bestaetigt", "abgesagt")

SCHEMA_SQL = f"""
CREATE TABLE IF NOT EXISTS reservationen (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    kontaktperson       TEXT NOT NULL,
    email               TEXT NOT NULL,
    organisation        TEXT,
    telefonnummer       TEXT,
    titel               TEXT,
    veranstaltungsart   TEXT,
    raum                TEXT NOT NULL CHECK (raum IN {RAEUME!r}),
    datum               TEXT NOT NULL,
    beginn              TEXT NOT NULL,
    ende                TEXT NOT NULL,
    anzahl_personen     INTEGER,
    bestuhlung          TEXT,
    verpflegung         INTEGER NOT NULL CHECK (verpflegung IN (0, 1)),
    bemerkungen         TEXT,
    eingang_zeitpunkt   TEXT NOT NULL,
    status              TEXT NOT NULL CHECK (status IN {STATUS_WERTE!r}),
    restaurant_informiert INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_reservationen_raum_datum
    ON reservationen (raum, datum, status);
"""


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """`db_path` erlaubt Tests, eine isolierte Datenbank statt der produktiven zu verwenden."""
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path | None = None) -> None:
    conn = get_connection(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()
