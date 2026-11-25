from app import emails

RESERVATION = {
    "kontaktperson": "Anna Test",
    "email": "anna@example.org",
    "telefonnummer": "079 000 00 00",
    "titel": "Teamworkshop",
    "raum": "Seminarraum 1",
    "datum": "2026-12-01",
    "beginn": "09:00",
    "ende": "11:00",
}


def _lies_eml(pfad):
    from email import message_from_bytes, policy

    return message_from_bytes(pfad.read_bytes(), policy=policy.default)


def test_bestaetigung_wird_mit_platzhaltern_gerendert(tmp_path, monkeypatch):
    monkeypatch.setattr(emails, "OUTBOX_DIR", tmp_path)

    pfad = emails.sende_bestaetigung(RESERVATION)

    assert pfad.exists()
    nachricht = _lies_eml(pfad)
    assert "Seminarraum 1" in nachricht["Subject"]
    assert "2026-12-01" in nachricht["Subject"]
    assert nachricht["To"] == "anna@example.org"

    text = nachricht.get_content()
    assert "Anna Test" in text
    assert "Seminarraum 1" in text
    assert "09:00" in text and "11:00" in text
    assert "{{" not in text and "[" not in text


def test_absage_enthaelt_raum_datum_und_zeitraum(tmp_path, monkeypatch):
    monkeypatch.setattr(emails, "OUTBOX_DIR", tmp_path)

    pfad = emails.sende_absage(RESERVATION)
    text = _lies_eml(pfad).get_content()

    assert "Seminarraum 1" in text
    assert "2026-12-01" in text
    assert "09:00" in text and "11:00" in text
    assert "Teamworkshop" in text
    assert "{{" not in text


def test_absage_ohne_titel_verwendet_platzhalter_text(tmp_path, monkeypatch):
    monkeypatch.setattr(emails, "OUTBOX_DIR", tmp_path)
    ohne_titel = dict(RESERVATION, titel=None)

    pfad = emails.sende_absage(ohne_titel)
    text = _lies_eml(pfad).get_content()

    assert "Ihre Veranstaltung" in text


def test_restaurant_info_wird_an_restaurantleitung_gesendet(tmp_path, monkeypatch):
    monkeypatch.setattr(emails, "OUTBOX_DIR", tmp_path)

    pfad = emails.sende_restaurant_info(RESERVATION)
    nachricht = _lies_eml(pfad)

    assert nachricht["To"] == emails.RESTAURANT_EMPFAENGER
    text = nachricht.get_content()
    assert "Anna Test" in text
    assert "anna@example.org" in text
    assert "079 000 00 00" in text


def test_restaurant_info_ohne_telefonnummer(tmp_path, monkeypatch):
    monkeypatch.setattr(emails, "OUTBOX_DIR", tmp_path)
    ohne_telefon = dict(RESERVATION, telefonnummer=None)

    pfad = emails.sende_restaurant_info(ohne_telefon)
    text = _lies_eml(pfad).get_content()

    assert "nicht angegeben" in text
