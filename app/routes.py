from flask import Blueprint, abort, redirect, render_template, request, url_for

from . import db, models
from .availability import raum_ist_verfuegbar
from .db import RAEUME

bp = Blueprint("reservation", __name__)

PFLICHTFELD_LABELS = {
    "kontaktperson": "Name der Kontaktperson",
    "email": "E-Mail-Adresse",
    "raum": "Gewünschter Raum",
    "datum": "Veranstaltungsdatum",
    "beginn": "Beginn",
    "ende": "Ende",
    "verpflegung": "Angabe zur Verpflegung",
}


def _formular_daten(form) -> dict:
    verpflegung_wert = form.get("verpflegung")
    return {
        "kontaktperson": form.get("kontaktperson", "").strip(),
        "email": form.get("email", "").strip(),
        "organisation": form.get("organisation", "").strip() or None,
        "telefonnummer": form.get("telefonnummer", "").strip() or None,
        "titel": form.get("titel", "").strip() or None,
        "veranstaltungsart": form.get("veranstaltungsart", "").strip() or None,
        "raum": form.get("raum", "").strip(),
        "datum": form.get("datum", "").strip(),
        "beginn": form.get("beginn", "").strip(),
        "ende": form.get("ende", "").strip(),
        "anzahl_personen": form.get("anzahl_personen") or None,
        "bestuhlung": form.get("bestuhlung", "").strip() or None,
        "verpflegung": (
            True if verpflegung_wert == "ja" else False if verpflegung_wert == "nein" else None
        ),
        "bemerkungen": form.get("bemerkungen", "").strip() or None,
    }


def _validiere(daten: dict) -> list[str]:
    fehler = [
        f"{PFLICHTFELD_LABELS[feld]} ist ein Pflichtfeld."
        for feld in models.fehlende_pflichtfelder(daten)
    ]
    if daten["raum"] and daten["raum"] not in RAEUME:
        fehler.append("Bitte einen gültigen Raum auswählen.")
    if daten["beginn"] and daten["ende"] and daten["beginn"] >= daten["ende"]:
        fehler.append("Die Endzeit muss nach der Beginnzeit liegen.")
    return fehler


@bp.route("/", methods=["GET"])
def formular():
    return render_template("formular.html", raeume=RAEUME, werte={}, fehler=[])


@bp.route("/reservation", methods=["POST"])
def reservation_einreichen():
    daten = _formular_daten(request.form)
    fehler = _validiere(daten)

    if fehler:
        return render_template("formular.html", raeume=RAEUME, werte=daten, fehler=fehler), 400

    conn = db.get_connection()
    try:
        bestehende = models.get_confirmed_for_room_date(conn, daten["raum"], daten["datum"])
        verfuegbar = raum_ist_verfuegbar(daten["beginn"], daten["ende"], bestehende)
        status = "bestaetigt" if verfuegbar else "abgesagt"
        reservation_id = models.insert_reservation(conn, daten, status=status)
    finally:
        conn.close()

    return redirect(url_for("reservation.ergebnis", reservation_id=reservation_id))


@bp.route("/reservation/<int:reservation_id>")
def ergebnis(reservation_id):
    conn = db.get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM reservationen WHERE id = ?", (reservation_id,)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        abort(404)
    return render_template("ergebnis.html", reservation=row)


@bp.route("/sekretariat")
def sekretariat():
    conn = db.get_connection()
    try:
        reservationen = models.list_all(conn)
    finally:
        conn.close()
    return render_template("sekretariat.html", reservationen=reservationen)
