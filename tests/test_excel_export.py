from openpyxl import load_workbook

from app import db, excel_export, models


def test_export_enthaelt_nur_bestaetigte_reservationen_mit_originalspalten(tmp_path):
    db_path = tmp_path / "test.db"
    db.init_db(db_path)
    conn = db.get_connection(db_path)

    models.insert_reservation(
        conn,
        {
            "kontaktperson": "Anna Test",
            "email": "anna@example.org",
            "organisation": "Firma A",
            "titel": "Teamworkshop",
            "telefonnummer": "079 000 00 00",
            "raum": "Seminarraum 1",
            "datum": "2026-12-01",
            "beginn": "09:00",
            "ende": "11:00",
            "verpflegung": True,
        },
        status="bestaetigt",
    )
    models.insert_reservation(
        conn,
        {
            "kontaktperson": "Marco Abgesagt",
            "email": "marco@example.org",
            "raum": "Seminarraum 1",
            "datum": "2026-12-01",
            "beginn": "10:00",
            "ende": "12:00",
            "verpflegung": False,
        },
        status="abgesagt",
    )

    zielpfad = tmp_path / "export.xlsx"
    excel_export.exportiere_reservationsliste(conn, zielpfad)
    conn.close()

    arbeitsmappe = load_workbook(zielpfad)
    blatt = arbeitsmappe.active

    kopfzeile = tuple(zelle.value for zelle in blatt[1])
    assert kopfzeile == excel_export.SPALTEN

    datenzeilen = list(blatt.iter_rows(min_row=2, values_only=True))
    assert len(datenzeilen) == 1, "Nur bestätigte Reservationen dürfen exportiert werden"
    zeile = datenzeilen[0]
    assert zeile[0] == "Seminarraum 1"
    assert zeile[4] == "Teamworkshop"
    assert zeile[6] == "Anna Test"
    assert zeile[9] == "Ja"
