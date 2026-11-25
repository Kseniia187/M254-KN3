"""Rendering der E-Mail-Vorlagen und Ablage als .eml-Dateien im lokalen Outbox-Ordner.

Es wird bewusst kein echter SMTP-Versand vorgenommen (Testumgebung, siehe CLAUDE.md).
"""

from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "email_templates"
OUTBOX_DIR = Path(__file__).resolve().parent.parent / "data" / "outbox"

ABSENDER = "Sekretariat <sekretariat@bildungszentrum.example>"
RESTAURANT_EMPFAENGER = "restaurantleitung@bildungszentrum.example"

_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(disabled_extensions=("txt",)),
    keep_trailing_newline=True,
)


def _render(template_name: str, kontext: dict) -> tuple[str, str]:
    """Rendert eine Vorlage und gibt (betreff, text) zurück."""
    text = _env.get_template(template_name).render(**kontext)
    erste_zeile, _, rest = text.partition("\n\n")
    betreff = erste_zeile.removeprefix("SUBJECT:").strip()
    return betreff, rest.strip() + "\n"


def _schreibe_outbox(empfaenger: str, betreff: str, text: str, dateiname_praefix: str) -> Path:
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    nachricht = EmailMessage()
    nachricht["From"] = ABSENDER
    nachricht["To"] = empfaenger
    nachricht["Subject"] = betreff
    nachricht.set_content(text)

    zeitstempel = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    pfad = OUTBOX_DIR / f"{zeitstempel}_{dateiname_praefix}.eml"
    pfad.write_bytes(bytes(nachricht))
    return pfad


def sende_bestaetigung(reservation) -> Path:
    betreff, text = _render(
        "bestaetigung.txt",
        {
            "kontaktperson": reservation["kontaktperson"],
            "raum": reservation["raum"],
            "datum": reservation["datum"],
            "beginn": reservation["beginn"],
            "ende": reservation["ende"],
        },
    )
    return _schreibe_outbox(reservation["email"], betreff, text, "bestaetigung")


def sende_absage(reservation) -> Path:
    betreff, text = _render(
        "absage.txt",
        {
            "kontaktperson": reservation["kontaktperson"],
            "titel": reservation["titel"] or "Ihre Veranstaltung",
            "raum": reservation["raum"],
            "datum": reservation["datum"],
            "beginn": reservation["beginn"],
            "ende": reservation["ende"],
        },
    )
    return _schreibe_outbox(reservation["email"], betreff, text, "absage")


def sende_restaurant_info(reservation) -> Path:
    betreff, text = _render(
        "restaurant_info.txt",
        {
            "raum": reservation["raum"],
            "datum": reservation["datum"],
            "beginn": reservation["beginn"],
            "ende": reservation["ende"],
            "kontaktperson": reservation["kontaktperson"],
            "email": reservation["email"],
            "telefonnummer": reservation["telefonnummer"] or "nicht angegeben",
        },
    )
    return _schreibe_outbox(RESTAURANT_EMPFAENGER, betreff, text, "restaurant_info")
