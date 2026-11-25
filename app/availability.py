"""Reine Verfügbarkeits-/Konfliktprüfung – keine Datenbank- oder Flask-Abhängigkeit."""

from datetime import time


def _parse(zeit: str) -> time:
    stunden, minuten = zeit.split(":")
    return time(int(stunden), int(minuten))


def ueberschneidung(beginn_a: str, ende_a: str, beginn_b: str, ende_b: str) -> bool:
    """True, wenn sich zwei Zeitintervalle echt überlappen.

    Ein Intervall, das genau dort endet, wo das andere beginnt (Ende = Beginn),
    gilt gemäss Fallbeispiel nicht als Konflikt.
    """
    a_beginn, a_ende = _parse(beginn_a), _parse(ende_a)
    b_beginn, b_ende = _parse(beginn_b), _parse(ende_b)
    return a_beginn < b_ende and b_beginn < a_ende


def raum_ist_verfuegbar(beginn: str, ende: str, bestehende_reservationen) -> bool:
    """`bestehende_reservationen`: bereits auf denselben Raum, dasselbe Datum und den
    Status 'bestaetigt' gefilterte Einträge mit den Schlüsseln 'beginn' und 'ende'
    (z. B. sqlite3.Row oder dict)."""
    return not any(
        ueberschneidung(beginn, ende, reservation["beginn"], reservation["ende"])
        for reservation in bestehende_reservationen
    )
