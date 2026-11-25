# TODO — M254 KN3 Raumreservation

Status-Legende: `[ ]` offen · `[x]` erledigt

## 1. Setup & Projektgedächtnis
- [x] Originalunterlagen analysiert (Auftrags-PDF, Reservationsformular, Reservationsliste.xlsx,
      beide E-Mail-Vorlagen)
- [x] Originaldateien nach `docs/original-unterlagen/` verschoben
- [x] Git-Repository initialisiert, `.gitignore` angelegt
- [x] `CLAUDE.md` mit Architektur & Regeln erstellt
- [x] `TODO.md` erstellt
- [x] Projektgerüst angelegt (`app/`, `tests/`, `email_templates/`, `data/`, `exports/`,
      `requirements.txt`, virtuelle Umgebung `.venv/`)

## 2. Datenbank-Struktur
- [x] SQLite-Schema für Reservationen definiert (Pflicht- + optionale Felder, Status
      `bestaetigt`/`abgesagt`, Eingangszeitstempel)
- [x] `app/db.py` + `app/models.py` (Init, Insert, Query nach Raum/Datum/Status,
      Pflichtfeld-Check) — manuell per Smoke-Test verifiziert
- [ ] Commit: "Datenbank-Struktur"

## 3. Verfügbarkeits- und Konfliktprüfung
- [x] `app/availability.py`: reine Funktion für Zeit-Überschneidung pro Raum gegen bestätigte
      Reservationen
- [x] Unit-Tests (pytest): keine Überschneidung, direkte Überschneidung, Rand-an-Rand (Ende =
      Beginn, kein Konflikt), vollständig enthalten, mehrere bestehende Reservationen,
      First-come-Priorisierung bei Wettlauf (Integrationstest mit DB) — 11/11 Tests grün
- [ ] Commit: "Verfügbarkeits-/Konfliktprüfung inkl. Tests"

## 4. Formular & Backend (Flask)
- [ ] Flask-App-Grundgerüst (`app/__init__.py`, `app/routes.py`)
- [ ] Reservationsformular (HTML, alle Pflichtfelder aus dem Original-PDF 1:1 übernommen,
      optionale Felder wie Bestuhlung/Technik/Personenzahl)
- [ ] Serverseitige Pflichtfeld-Validierung (required + Validierung bei Fehlen/Format)
- [ ] Beim Absenden: Eingangszeitstempel setzen, Verfügbarkeit prüfen, Status setzen
- [ ] Sekretariats-Ansicht: Liste aller Reservationen/Anfragen mit Status
- [ ] Commit: "Formular & Backend"

## 5. E-Mail-Logik
- [ ] Original-`.eml`-Vorlagen in parametrisierte Text-Vorlagen (`email_templates/`) überführen
- [ ] `app/emails.py`: Platzhalter befüllen, Ergebnis als `.eml` in `data/outbox/` schreiben
- [ ] Reservationsbestätigung bei Verfügbarkeit automatisch auslösen
- [ ] Absage bei Konflikt automatisch auslösen
- [ ] Neue Vorlage `restaurant_info.txt` erstellen + automatischer Versand bei Verpflegung=Ja
- [ ] Commit: "E-Mail-Logik"

## 6. Excel-Export
- [ ] `app/excel_export.py`: Export bestätigter Reservationen in ein zu
      `Reservationsliste.xlsx` kompatibles Format (gleiche Spalten)
- [ ] Commit: "Excel-Export"

## 7. Tests & Qualitätssicherung
- [ ] Vollständige pytest-Suite lauffähig (Konfliktprüfung, Validierung, E-Mail-Rendering,
      Excel-Export)
- [ ] Manuelle End-to-End-Prüfung über die laufende App (Demo-Szenario mit Konflikt)
- [ ] Commit: "Tests"

## 8. Dokumentation
- [ ] `Projektdokumentation.md`: Ist-Zustand, Soll-Zustand, Funktionsweise, Anleitung,
      bewusste Abweichungen vom Original-Prozess, Testergebnisse, Fazit
- [ ] Commit: "Projektdokumentation"

## Offene Annahmen (mit Nutzer/Lehrperson klären falls nötig)
- Restaurant-Info-Mail wurde neu entworfen, da keine Original-Vorlage existiert.
- Konfliktprüfung läuft in Echtzeit statt im täglichen Batch (siehe CLAUDE.md,
  "bewusste Prozessänderung").
