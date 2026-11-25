# VM-Testanleitung — Raumreservation M254 KN3

Diese Anleitung zeigt Schritt für Schritt, wie du das Projekt auf einer frischen VM
installierst, die automatisierten Tests laufen lässt und die Anwendung live vorführst —
als Beweis gegenüber der Lehrperson, dass alles wie dokumentiert funktioniert.

Die Anleitung deckt zwei Fälle ab:
- **Fall A:** VM mit grafischer Oberfläche/Browser
- **Fall B:** VM ohne grafische Oberfläche (reines Terminal, z. B. per SSH) — dort wird
  alles über `curl` geprüft, das Ergebnis ist identisch

---

## 0. Voraussetzungen

- Python 3.10 oder neuer (`python3 --version`)
- `git`
- Internetzugang, um das Repository zu klonen

Falls Python fehlt (Ubuntu/Debian-VM):
```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git
```

---

## 1. Repository klonen

```bash
git clone https://github.com/Kseniia187/M254-KN3.git
cd M254-KN3
```

## 2. Virtuelle Umgebung erstellen und Abhängigkeiten installieren

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Erwartung: Keine Fehlermeldungen. `pip list` zeigt u. a. `Flask`, `openpyxl`, `pytest`.

---

## 3. Beweis #1: Automatisierte Tests

```bash
python -m pytest -v
```

**Erwartetes Ergebnis:** 17 Tests, alle `PASSED`, letzte Zeile `17 passed in ...s`.

Diese Tests beweisen automatisiert:
- Korrekte Konflikterkennung bei Raumüberschneidungen (inkl. Randfall "Ende = Beginn")
- First-come-first-served-Priorisierung bei konkurrierenden Anfragen
- Korrekte Befüllung der E-Mail-Vorlagen (Bestätigung, Absage, Restaurant-Info)
- Korrekter Excel-Export (nur bestätigte Reservationen, identische Spalten wie Original)

Screenshot/Terminal-Ausgabe dieses Schritts eignet sich direkt als Beleg für Kapitel 5
("Überprüfung") der `Projektdokumentation.md`.

---

## 4. Beweis #2: Anwendung live vorführen

### Anwendung starten

```bash
python run.py
```

Die Konsole zeigt `Running on http://127.0.0.1:5000`. Server mit `Strg+C` beenden, wenn
fertig.

### Fall A — VM mit Browser

Browser öffnen: `http://127.0.0.1:5000/`

1. **Erste Reservationsanfrage einreichen** (Formular ausfüllen):
   - Name der Kontaktperson: `Anna Test`
   - E-Mail: `anna@example.org`
   - Raum: `Seminarraum 1`
   - Datum: ein beliebiges künftiges Datum, z. B. `2026-12-15`
   - Beginn: `09:00`, Ende: `10:30`
   - Verpflegung: `Ja`
   - Absenden → Erwartung: Seite zeigt **"Reservation bestätigt"**

2. **Zweite, überlappende Anfrage einreichen** (gleicher Raum, gleicher Tag,
   überschneidende Zeit):
   - Name: `Marco Konflikt`, E-Mail: `marco@example.org`
   - Raum: `Seminarraum 1`, Datum: `2026-12-15`, Beginn: `10:00`, Ende: `11:00`
   - Verpflegung: `Nein`
   - Absenden → Erwartung: Seite zeigt **"Reservation nicht möglich"** (Konflikt erkannt)

3. **Sekretariats-Ansicht** öffnen: `http://127.0.0.1:5000/sekretariat`
   → beide Einträge sichtbar, mit Status `bestaetigt` bzw. `abgesagt`

4. **Erzeugte E-Mails prüfen:** Ordner `data/outbox/` im Dateimanager öffnen. Es sollten
   `.eml`-Dateien liegen (Bestätigung, Restaurant-Info für Anna; Absage für Marco). Mit
   Doppelklick öffnen (Standard-Mail-Programm oder Texteditor) — Inhalt zeigt die
   eingegebenen Daten korrekt eingesetzt.

5. **Excel-Export:** Auf der Sekretariats-Ansicht auf "Reservationsliste.xlsx
   exportieren" klicken, Datei in Excel/LibreOffice öffnen → enthält nur die bestätigte
   Reservation von Anna, mit denselben Spalten wie das Original
   (`docs/original-unterlagen/Reservationsliste.xlsx`).

### Fall B — VM ohne Browser (reines Terminal/SSH)

Server im Hintergrund starten:
```bash
python run.py &
sleep 2
```

Erste Anfrage (Anna) einreichen und Ergebnis abrufen:
```bash
LOC=$(curl -s -o /dev/null -D - -X POST http://127.0.0.1:5000/reservation \
  -d "kontaktperson=Anna Test" -d "email=anna@example.org" -d "raum=Seminarraum 1" \
  -d "datum=2026-12-15" -d "beginn=09:00" -d "ende=10:30" -d "verpflegung=ja" \
  | grep -i "^location:" | tr -d '\r' | awk '{print $2}')
curl -s "http://127.0.0.1:5000$LOC" | grep -o "bestätigt\|nicht möglich"
```
Erwartung: Ausgabe `bestätigt`

Zweite, überlappende Anfrage (Marco):
```bash
LOC2=$(curl -s -o /dev/null -D - -X POST http://127.0.0.1:5000/reservation \
  -d "kontaktperson=Marco Konflikt" -d "email=marco@example.org" -d "raum=Seminarraum 1" \
  -d "datum=2026-12-15" -d "beginn=10:00" -d "ende=11:00" -d "verpflegung=nein" \
  | grep -i "^location:" | tr -d '\r' | awk '{print $2}')
curl -s "http://127.0.0.1:5000$LOC2" | grep -o "bestätigt\|nicht möglich"
```
Erwartung: Ausgabe `nicht möglich`

Sekretariats-Ansicht prüfen:
```bash
curl -s http://127.0.0.1:5000/sekretariat | grep -o "Anna Test\|Marco Konflikt"
```
Erwartung: beide Namen werden ausgegeben.

Erzeugte E-Mails auflisten und eine davon anzeigen:
```bash
ls data/outbox/
cat data/outbox/*bestaetigung.eml
```
Erwartung: 3 Dateien (Bestätigung + Restaurant-Info für Anna, Absage für Marco); der
Inhalt der Bestätigung zeigt Raum, Datum und Zeiten korrekt eingesetzt (ggf. MIME-kodiert
mit Umlauten — mit `python3 -m mailbox` oder einem Mail-Client lesbar machen, siehe unten).

Excel-Export herunterladen und Inhalt grob prüfen:
```bash
curl -s -o reservationsliste_export.xlsx http://127.0.0.1:5000/export/reservationsliste.xlsx
file reservationsliste_export.xlsx
```
Erwartung: `Microsoft Excel 2007+`. Mit `python3` + `openpyxl` lassen sich die Werte ohne
GUI auslesen:
```bash
python3 -c "
from openpyxl import load_workbook
wb = load_workbook('reservationsliste_export.xlsx')
for row in wb.active.iter_rows(values_only=True):
    print(row)
"
```

Server danach stoppen:
```bash
kill %1
```

---

## 5. Nützliche Zusatzbefehle

**Datenbank zurücksetzen** (für einen sauberen Neustart der Demo):
```bash
# Server vorher stoppen!
rm -f data/reservationen.db
rm -rf data/outbox
```
Beim nächsten Start von `python run.py` wird die Datenbank automatisch neu angelegt.

**E-Mail-Inhalt lesbar machen**, falls die `.eml`-Datei nur kodierten Text zeigt
(quoted-printable/MIME):
```bash
python3 -c "
from email import message_from_bytes, policy
import sys
with open(sys.argv[1], 'rb') as f:
    msg = message_from_bytes(f.read(), policy=policy.default)
print('Betreff:', msg['Subject'])
print('An:', msg['To'])
print(msg.get_content())
" data/outbox/<dateiname>.eml
```

---

## 6. Checkliste für die Vorführung/Beweis gegenüber der Lehrperson

- [ ] `pip install -r requirements.txt` läuft ohne Fehler
- [ ] `python -m pytest -v` → 17/17 Tests grün
- [ ] Formular erzwingt Pflichtfelder (Versuch: leeres Formular absenden → Fehlermeldung)
- [ ] Erste Anfrage wird bestätigt
- [ ] Zweite, überlappende Anfrage für denselben Raum wird abgesagt
- [ ] Sekretariats-Ansicht zeigt beide Einträge korrekt
- [ ] `data/outbox/` enthält die erwarteten E-Mails mit korrektem Inhalt
- [ ] Excel-Export funktioniert und enthält nur bestätigte Reservationen
- [ ] (Optional) Screenshots/Terminal-Ausgaben für die Projektdokumentation gesichert
