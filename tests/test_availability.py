from app.availability import raum_ist_verfuegbar, ueberschneidung


def test_keine_ueberschneidung_getrennte_zeiten():
    assert not ueberschneidung("09:00", "10:00", "11:00", "12:00")


def test_direkte_ueberschneidung():
    assert ueberschneidung("09:00", "11:00", "10:00", "12:00")


def test_rand_an_rand_kein_konflikt():
    assert not ueberschneidung("09:00", "10:00", "10:00", "11:00")


def test_vollstaendig_enthalten_ist_konflikt():
    assert ueberschneidung("09:00", "12:00", "10:00", "11:00")


def test_identische_zeiten_sind_konflikt():
    assert ueberschneidung("09:00", "10:00", "09:00", "10:00")


def test_raum_verfuegbar_ohne_bestehende_reservationen():
    assert raum_ist_verfuegbar("09:00", "10:00", [])


def test_raum_nicht_verfuegbar_bei_konflikt():
    bestehende = [{"beginn": "09:30", "ende": "10:30"}]
    assert not raum_ist_verfuegbar("09:00", "10:00", bestehende)


def test_raum_verfuegbar_trotz_anderer_reservation_an_anderer_zeit():
    bestehende = [{"beginn": "13:00", "ende": "14:00"}]
    assert raum_ist_verfuegbar("09:00", "10:00", bestehende)


def test_raum_nicht_verfuegbar_wenn_eine_von_mehreren_reservationen_kollidiert():
    bestehende = [
        {"beginn": "07:00", "ende": "08:00"},
        {"beginn": "09:30", "ende": "10:30"},
        {"beginn": "15:00", "ende": "16:00"},
    ]
    assert not raum_ist_verfuegbar("09:00", "10:00", bestehende)
