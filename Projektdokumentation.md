# Projektdokumentation — M254 KN3 Prozessautomatisierung

**Fallbeispiel:** Raumreservation in einem Bildungszentrum (Auftrags-PDF Kapitel 6)
**Quelle:** `docs/original-unterlagen/M254_KN3_Prozessautom_Auftrag (1).pdf`

## 1. Einleitung

Bearbeitet wurde das im Auftrag vorgegebene Fallbeispiel "Raumreservation in einem
Bildungszentrum", da es für dieses Projekt anstelle eines eigenen Onboarding-Prozesses
verwendet werden durfte (siehe Auftrags-PDF, Kapitel 1 und 6). Ein Bildungszentrum vermietet
drei Seminarräume an externe Kundinnen und Kunden. Das Sekretariat bearbeitet eingehende
Reservationsanfragen papierbasiert und pflegt eine Excel-Liste mit den bestätigten
Reservationen. Ziel dieses Projekts ist es, die administrativ aufwändigsten Teile dieses
Prozesses zu digitalisieren und zu automatisieren.

## 2. Ist-Zustand

Der bisherige Prozess läuft wie folgt ab (zusammengefasst aus dem Fallbeispiel):

1. Eine Kundin/ein Kunde füllt das `Reservationsformular.pdf` digital oder handschriftlich
   aus und sendet es per E-Mail oder persönlich ans Sekretariat.
2. Das Sekretariat (Mo–Fr, 07:30–14:00 Uhr) nimmt das Formular entgegen, vermerkt
   Eingangsdatum/-zeit und die entgegennehmende Person von Hand und legt es im Ablagefach
   "Eingang" ab.
3. Nach Büroschluss prüft eine Mitarbeiterin/ein Mitarbeiter gesammelt alle eingegangenen
   Formulare: zuerst auf Vollständigkeit der Pflichtangaben, danach manuell gegen die
   Excel-Reservationsliste auf Raumverfügbarkeit. Bei mehreren konkurrierenden Anfragen für
   denselben Raum/Zeitraum entscheidet der früheste Eingangszeitpunkt.
4. Ist der Raum belegt, wird eine Absage-E-Mail anhand der Vorlage verschickt, das Formular
   vernichtet. Ist der Raum frei, wird die Reservation manuell in die Excel-Liste übertragen
   und eine Bestätigungs-E-Mail verschickt.
5. Bei gewünschter Verpflegung informiert das Sekretariat die Restaurantleitung per E-Mail
   (ohne feste Vorlage).
6. Montags bereitet das Sekretariat die Veranstaltungen der Folgewoche vor, klärt fehlende
   Angaben telefonisch oder per E-Mail und aktualisiert die Formulare handschriftlich.
   Donnerstags werden die aktualisierten Formulare in Papierform an den Hausdienst übergeben.

**Probleme laut Auftrag:** steigende Veranstaltungszahl, hoher administrativer Aufwand,
Schwierigkeiten, alle benötigten Angaben rechtzeitig einzuholen und an den Hausdienst
weiterzugeben.

## 3. Soll-Zustand / Umsetzungskonzept

### 3.1 Ausgangslage und Ziel

Aufgegriffen wird der Teilprozess von der Reservationsanfrage bis zur verbindlichen
Bestätigung bzw. Absage inklusive Information der Restaurantleitung. Dies ist der Teil mit
dem grössten manuellen, fehleranfälligen und zeitkritischen Aufwand (Pflichtfeld-Kontrolle,
manueller Abgleich mit der Excel-Liste, Erstellen der E-Mails von Hand). Ziel: Diese Schritte
laufen digital und automatisiert in Echtzeit statt papierbasiert und als täglicher
Sammel-Batch ab.

### 3.2 Umfang und Abgrenzung

**Teil des Umsetzungsumfangs:**
- Digitales Reservationsformular mit erzwungenen Pflichtfeldern
- Automatische Verfügbarkeits-/Konfliktprüfung inkl. First-come-first-served-Priorisierung
- Automatische Erstellung und Ablage von Bestätigungs-, Absage- und Restaurant-Info-E-Mails
- Digitale Datenhaltung (SQLite) mit Sekretariats-Übersicht
- Export der bestätigten Reservationen in ein zur Original-Excel-Liste kompatibles Format

**Ausdrücklich nicht Teil des Umsetzungsumfangs:**
- Die Vorbereitung der Folgewoche (montags) und die Übergabe an den Hausdienst (donnerstags)
  bleiben unverändert manuell/papierbasiert. Eine Digitalisierung dieses Teils wäre eine
  sinnvolle Erweiterung, war aber für den vereinbarten Umfang dieses Projekts zu umfangreich.
- Kein echter E-Mail-Versand (SMTP) und keine Anbindung an ein reales E-Mail-Postfach.
- Keine Benutzer-Authentifizierung für die Sekretariats-Ansicht (interne Testumgebung).
- Keine produktive Einführung im Bildungszentrum (gemäss Auftrags-PDF Kapitel 1 nicht
  gefordert).

### 3.3 Funktionale Anforderungen

| # | Anforderung |
|---|---|
| FR1 | Das Formular erzwingt alle im Fallbeispiel definierten Pflichtfelder (Name Kontaktperson, E-Mail, Raum, Datum, Beginn, Ende, Verpflegung Ja/Nein); unvollständige Anfragen können nicht abgeschickt werden. |
| FR2 | Bei jeder Anfrage wird automatisch geprüft, ob der gewünschte Raum im gewünschten Zeitraum bereits durch eine bestätigte Reservation belegt ist. |
| FR3 | Bei konkurrierenden, sich überschneidenden Anfragen für denselben Raum gewinnt die zuerst eingegangene Anfrage. |
| FR4 | Ist der Raum verfügbar, wird automatisch eine Reservationsbestätigung erzeugt und abgelegt sowie die Reservation gespeichert. |
| FR5 | Ist der Raum belegt, wird automatisch eine Absage erzeugt und abgelegt; die Reservation wird nicht gespeichert. |
| FR6 | Wurde Verpflegung gewünscht, wird automatisch eine Information an die Restaurantleitung erzeugt und abgelegt. |
| FR7 | Alle Reservationen (bestätigt und abgesagt) sind in einer Sekretariats-Ansicht einsehbar. |
| FR8 | Die bestätigten Reservationen können in ein zur Original-`Reservationsliste.xlsx` kompatibles Format (identische Spalten) exportiert werden. |

### 3.4 Nicht-funktionale Anforderungen

| # | Anforderung |
|---|---|
| NFR1 | Benutzbarkeit: Formularstruktur und Feldbezeichnungen orientieren sich am Original-PDF, Pflichtfelder sind klar markiert, Fehlermeldungen sind verständlich auf Deutsch formuliert. |
| NFR2 | Zuverlässigkeit: Die Konflikt-/Verfügbarkeitslogik ist durch automatisierte Tests abgesichert (Randfälle wie "Ende = Beginn"); Datenbank-Constraints verhindern inkonsistente Datensätze (z. B. ungültiger Raum). |
| NFR3 | Verarbeitungsgeschwindigkeit: Rückmeldung an die anfragende Person erfolgt in Echtzeit (deutlich unter 1 Sekunde) statt wie bisher erst nach dem täglichen Sammel-Batch. |

### 3.5 Technische Umsetzung und Rahmenbedingungen

- **Sprache/Framework:** Python 3.12, Flask (Web-Formular, Sekretariats-Ansicht), Jinja2
  (HTML- und E-Mail-Templates)
- **Datenhaltung:** SQLite als führendes System; Export in ein Excel-kompatibles Format über
  `openpyxl`
- **E-Mail:** Gerenderte `.eml`-Dateien werden lokal in `data/outbox/` abgelegt statt über
  SMTP versendet (Testumgebung)
- **Tests:** `pytest`
- **Rahmenbedingung:** Umsetzung und Verifikation erfolgten in einer rein lokalen
  Testumgebung ohne Browser-Zugriff; die UI wurde über den Flask-Test-Client und zusätzlich
  über `curl` gegen den echten Flask-Dev-Server geprüft (siehe Kapitel 5).

## 4. Realisierung

### 4.1 Ergebnis der Umsetzung

Es wurde eine lauffähige Flask-Anwendung erstellt. Projektstruktur:

```
M254/
  app/
    db.py              SQLite-Schema (Pflicht-/optionale Felder, Status, Eingangszeitstempel)
    models.py           Insert/Query, Pflichtfeld-Prüfung
    availability.py      Reine Konflikt-/Verfügbarkeitsprüfung (ohne DB-/Flask-Abhängigkeit)
    emails.py            Rendering der E-Mail-Vorlagen, Ablage in data/outbox/
    excel_export.py      Export in Reservationsliste.xlsx-kompatibles Format
    routes.py            Flask-Routen: Formular, Ergebnis, Sekretariats-Ansicht, Export
    templates/, static/  HTML/CSS
  email_templates/       Parametrisierte Vorlagen (aus den Original-.eml abgeleitet)
  tests/                 17 pytest-Tests
  docs/original-unterlagen/  Unveränderte Originaldateien des Fallbeispiels
  run.py                 Startpunkt der Anwendung
```

**Ablauf einer Reservationsanfrage:**

1. Kundin/Kunde füllt das Formular unter `/` aus (Felder identisch zum Original-PDF).
2. Beim Absenden (`POST /reservation`) werden die Pflichtfelder serverseitig geprüft; bei
   fehlenden/ungültigen Angaben wird das Formular mit Fehlermeldung und bereits eingegebenen
   Werten erneut angezeigt.
3. Sind alle Pflichtangaben vorhanden, wird sofort gegen alle bereits **bestätigten**
   Reservationen für denselben Raum und dasselbe Datum geprüft (`app/availability.py`).
4. Verfügbar → Status `bestaetigt`, Bestätigungs-E-Mail wird erzeugt; zusätzlich bei
   Verpflegung=Ja eine Info an die Restaurantleitung.
   Nicht verfügbar → Status `abgesagt`, Absage-E-Mail wird erzeugt.
5. Ergebnisseite informiert die anfragende Person sofort über Bestätigung oder Absage.
6. Das Sekretariat sieht unter `/sekretariat` alle Anfragen mit Status und kann unter
   `/export/reservationsliste.xlsx` jederzeit eine zur Originalstruktur kompatible Excel-Datei
   herunterladen.

**Beispiel einer automatisch erzeugten Bestätigungsmail** (`data/outbox/*.eml`, Inhalt nach
MIME-Dekodierung):

```
Von: Sekretariat <sekretariat@bildungszentrum.example>
An: anna@example.org
Betreff: Reservationsbestätigung – Seminarraum 3, 2026-12-10

Guten Tag Anna Demo

Gerne bestätigen wir Ihnen die Reservation des folgenden Seminarraums:

Raum: Seminarraum 3
Datum: 2026-12-10
Beginn: 09:00 Uhr
Ende: 10:30 Uhr

Ihre Reservation ist hiermit verbindlich bestätigt. ...
```

Hinweis: In dieser Umgebung steht kein Browser zur Verfügung, daher wurden keine
Screenshots der Weboberfläche erstellt. Beim lokalen Ausführen (siehe Kapitel 6) ist die
Oberfläche unter `http://127.0.0.1:5000/` einsehbar.

### 4.2 Bewusste Abweichungen vom Original-Prozess

- **Echtzeit- statt Batch-Verarbeitung:** Im Original prüft das Sekretariat alle
  Tagesanfragen gesammelt nach Büroschluss. Die digitale Lösung prüft und entscheidet jede
  Anfrage sofort bei Eingabe. Das First-come-first-served-Prinzip bleibt erhalten (anhand des
  Zeitpunkts, an dem eine Anfrage als bestätigt gespeichert wird); der tägliche Sammel-Batch
  entfällt vollständig. Dies ist eine gewollte Prozessverbesserung (siehe Fazit).
- **Neue Vorlage für die Restaurant-Info:** Im Original existiert keine E-Mail-Vorlagendatei
  für die Information der Restaurantleitung, nur eine textliche Prozessbeschreibung. Die
  Vorlage `email_templates/restaurant_info.txt` wurde im gleichen Stil wie die beiden
  Original-Vorlagen neu erstellt.
- **Kein Vernichten/Archivieren von Papierformularen:** Da keine Papierformulare mehr
  entstehen, entfällt dieser Schritt ersatzlos.

## 5. Überprüfung

Automatisierte Tests (`pytest`, 17 Tests, alle grün):

| Testbereich | Datei | Geprüfte Anforderung |
|---|---|---|
| Zeit-Überschneidung | `tests/test_availability.py` | FR2/FR3: korrekte Konflikterkennung inkl. Randfall "Ende = Beginn" (kein Konflikt), vollständige Überlappung, mehrere bestehende Reservationen |
| First-come-first-served | `tests/test_konfliktpruefung_integration.py` | FR3: zuerst eingegangene Anfrage wird bestätigt, später eingegangene überlappende Anfrage abgesagt |
| E-Mail-Rendering | `tests/test_emails.py` | FR4/FR5/FR6: korrekte Platzhalter-Befüllung, Fallback-Text bei fehlendem Titel/fehlender Telefonnummer, korrekter Empfänger |
| Excel-Export | `tests/test_excel_export.py` | FR8: identische Spaltenstruktur wie Original, nur bestätigte Reservationen werden exportiert |

Zusätzlich manuell verifiziert:
- Über den Flask-Test-Client: Pflichtfeld-Validierung (FR1), vollständiger Antrags-Ablauf
  inkl. Weiterleitung auf die Ergebnisseite.
- Über den echten Flask-Dev-Server mit `curl`: zwei sich überschneidende Reservationsanfragen
  wurden eingereicht; die erste wurde bestätigt, die zweite abgesagt; Sekretariats-Ansicht,
  Outbox (3 E-Mails: Bestätigung, Restaurant-Info, Absage) und Excel-Export wurden live
  geprüft und funktionieren wie erwartet.

**Erfüllungsgrad:** Alle acht funktionalen Anforderungen (FR1–FR8) sind vollständig erfüllt
und automatisiert getestet. Die nicht-funktionalen Anforderungen (NFR1–NFR3) sind durch die
gewählte Umsetzung erfüllt, wurden aber nicht mit einer echten Nutzergruppe (Usability-Test)
oder unter Lastbedingungen verifiziert — das war für den vereinbarten Umfang nicht vorgesehen.

## 6. Anleitung

Voraussetzung: Python 3.12 (oder neuer).

```bash
cd M254
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Anwendung starten
python run.py
# Browser öffnen: http://127.0.0.1:5000/

# Tests ausführen
python -m pytest
```

- Reservationsformular: `http://127.0.0.1:5000/`
- Sekretariats-Ansicht (alle Anfragen inkl. Status): `http://127.0.0.1:5000/sekretariat`
- Excel-Export: Link auf der Sekretariats-Ansicht bzw. `http://127.0.0.1:5000/export/reservationsliste.xlsx`
- Erzeugte E-Mails liegen als `.eml`-Dateien in `data/outbox/` und lassen sich mit jedem
  E-Mail-Programm (z. B. Outlook) öffnen.
- Die SQLite-Datenbank liegt unter `data/reservationen.db`. Zum Zurücksetzen auf einen leeren
  Zustand genügt es, diese Datei bei gestopptem Server zu löschen — sie wird beim nächsten
  Start automatisch neu angelegt.

## 7. Fazit

**Beitrag zur Prozessverbesserung:** Die Lösung automatisiert exakt den Teil des Prozesses,
der laut Auftrag den höchsten administrativen Aufwand verursacht: die Pflichtfeld-Kontrolle,
den manuellen Abgleich mit der Excel-Liste und das Erstellen der drei E-Mail-Typen von Hand.
Anfragende Personen erhalten jetzt innert Sekunden statt erst am nächsten Tag eine
verbindliche Rückmeldung, und das Sekretariat muss keine Formulare mehr manuell auf
Vollständigkeit prüfen oder Reservationsdaten von Hand übertragen.

**Nicht/teilweise erfüllte Anforderungen:** Alle vereinbarten funktionalen Anforderungen
(FR1–FR8) wurden vollständig umgesetzt. Nicht umgesetzt wurde die Digitalisierung der
Montags-/Donnerstags-Abläufe (Vorbereitung der Folgewoche, Übergabe an den Hausdienst) — das
wurde von Beginn an bewusst aus dem Umfang ausgeschlossen (siehe 3.2), da es den
vereinbarten Rahmen des Projekts gesprengt hätte.

**Abweichungen vom ursprünglichen Konzept:** Die wichtigste Abweichung ist der Wechsel von
der täglichen Batch-Prüfung zur Echtzeit-Prüfung bei Formulareingabe (siehe 4.2). Diese
Abweichung wurde bewusst und frühzeitig getroffen, weil sie sowohl die Benutzererfahrung
(schnellere Rückmeldung) als auch die Umsetzung vereinfacht (kein separater
Batch-Verarbeitungsjob nötig), ohne das fachliche Prinzip "First come, first served" zu
verletzen.

**Weitere Schritte für einen produktiven Einsatz:**
- Anbindung an einen echten SMTP-Server statt lokaler Outbox-Dateien
- Benutzer-Authentifizierung für die Sekretariats-Ansicht
- Digitalisierung der Montags-/Donnerstags-Abläufe inkl. Übergabe an den Hausdienst
  (z. B. eigene Ansicht für den Hausdienst statt Papierübergabe)
- Eingabemöglichkeit für die "weiteren Angaben" (Personenanzahl, Bestuhlung, Technik), die
  laut Fallbeispiel erst nach der Bestätigung eintreffen können, direkt über ein Webformular
  statt handschriftlicher Ergänzung
- Produktive Datensicherung/Backup-Strategie für die SQLite-Datenbank

**Erkenntnisse für zukünftige Projekte:** Die reine, von Datenbank und Web-Framework
entkoppelte Verfügbarkeitsprüfung (`app/availability.py`) liess sich unabhängig und mit
wenigen, klar benannten Testfällen (insbesondere Randfällen wie "Ende = Beginn") sehr robust
absichern. Dieses Vorgehen — Kernlogik zuerst isoliert testen, danach erst in Web-Routen
integrieren — hat sich bewährt und reduzierte die Zahl der Fehler bei der späteren
Integration deutlich.
