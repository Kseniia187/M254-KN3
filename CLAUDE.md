# CLAUDE.md — Projektgedächtnis M254 KN3 (Raumreservation Bildungszentrum)

## Kontext

Schulprojekt GIBZ, Modul M254 "Geschäftsprozesse im eigenen Berufsumfeld beschreiben", KN3
Prozessautomatisierung. Bearbeitet wird das Fallbeispiel "Raumreservation in einem
Bildungszentrum" (siehe `docs/original-unterlagen/M254_KN3_Prozessautom_Auftrag (1).pdf`,
Kapitel 6). Abgabetermin Dokumentation: 12.01.2027, 23:59 Uhr. Bewertet werden Konzept,
umgesetzte Lösung, Tests, Fazit, Dokumentationsqualität und Präsentation — siehe PDF Kapitel 4.

Die Originalunterlagen (Reservationsformular, Excel-Liste, E-Mail-Vorlagen, Auftrags-PDF)
liegen unverändert in `docs/original-unterlagen/` und sind die Quelle der Wahrheit für
Pflichtfelder, Prozessschritte und Vorlagentexte. Sie werden nicht verändert.

## Fallbeispiel in Kürze

- 3 Seminarräume, Sekretariat bearbeitet Anfragen (Mo–Fr 07:30–14:00), Hausdienst richtet
  Räume ein, internes Restaurant übernimmt Verpflegung auf Wunsch.
- Pflichtfelder bei der Anfrage: Name Kontaktperson, E-Mail, gewünschter Raum, Datum, Beginn,
  Ende, Verpflegung Ja/Nein. Alles andere (Personenzahl, Bestuhlung, Technik/Material) darf
  später nachgereicht werden.
- Konfliktregel: Bei Überschneidung im selben Raum gewinnt die Anfrage mit dem früheren
  Eingangszeitpunkt. Verglichen wird gegen bereits **bestätigte** Reservationen.
- Bei Raumkonflikt: Absage-Mail (Vorlage vorhanden), Formular wird im Original-Prozess
  vernichtet. Bei Verfügbarkeit: Eintrag in Excel-Reservationsliste + Bestätigungsmail
  (Vorlage vorhanden). Bei Verpflegung=Ja: zusätzliche Info-Mail an Restaurantleitung
  (im Original-Prozess nur beschrieben, **keine** Vorlagendatei vorhanden — siehe unten).
- Donnerstags übergibt das Sekretariat die Unterlagen der Folgewoche in Papierform an den
  Hausdienst.

## Architekturentscheide (Soll-Prozess, digitalisiert)

- **Sprache/Stack:** Python, Flask (Web-Formular + Sekretariats-Ansicht), Jinja2 für HTML und
  für die E-Mail-Vorlagen.
- **Datenhaltung:** SQLite (`data/reservationen.db`) als führendes System — robuster für die
  automatische Konfliktprüfung als eine Excel-Datei. Export in ein zur Original-Struktur
  kompatibles `Reservationsliste.xlsx`-Format (gleiche Spalten) bleibt als Funktion erhalten,
  damit das Sekretariat die gewohnte Excel-Ansicht weiterhin exportieren kann.
- **E-Mail-Versand:** Standardmässig kein echter SMTP-Versand. Gerenderte E-Mails (aus den
  Original-`.eml`-Vorlagen mit befüllten Platzhaltern) werden als `.eml`-Dateien in
  `data/outbox/` abgelegt ("Testumgebung", siehe Auftrags-PDF Kapitel 1). Echter SMTP-Versand
  ist als Erweiterung in der Projektdokumentation als "weiterer Schritt für produktiven
  Einsatz" beschrieben, nicht Teil des Umfangs.
- **Restaurant-Info-Mail:** Da keine Original-Vorlagendatei existiert, wird eine neue Vorlage
  `email_templates/restaurant_info.txt` im gleichen Stil wie die beiden Original-Vorlagen neu
  erstellt (Raum, Datum, Zeiten, Kontaktdaten der anfragenden Person). Diese Abweichung wird in
  der Projektdokumentation explizit als Annahme ausgewiesen.
- **Konfliktprüfung/Priorisierung — bewusste Prozessänderung:** Im Original-Prozess sammelt das
  Sekretariat eingehende Anfragen und wertet sie einmal täglich nach Öffnungsschluss gebündelt
  aus (Priorisierung nach Eingangszeit). In der digitalisierten Lösung erfolgt die Prüfung in
  Echtzeit bei Formulareingabe: Eingangszeitstempel = Serverzeit der Einreichung, Verfügbarkeit
  wird sofort gegen bereits bestätigte Reservationen geprüft, Bestätigung/Absage wird sofort
  generiert. Das "First-come-first-served"-Prinzip bleibt erhalten (frühere Einreichung wird
  zuerst verarbeitet), der manuelle Tagesabschluss-Batch entfällt. Diese Abweichung vom
  Ist-Prozess ist eine gewollte Prozessverbesserung und wird im Fazit der
  Projektdokumentation begründet.
- **Pflichtfeld-Erzwingung:** HTML5 `required` + serverseitige Validierung in Flask. Eine
  unvollständige Anfrage kann gar nicht erst abgeschickt werden (Verbesserung gegenüber dem
  Papierprozess, wo unvollständige Formulare erst nachträglich auffallen).

## Projektstruktur

```
M254/
  app/                    Flask-Anwendung
    __init__.py           App-Factory
    db.py                 SQLite-Setup/Verbindung
    models.py             Schema + Datenzugriff für Reservationen
    availability.py       Reine Konflikt-/Verfügbarkeitsprüfung (kein Flask-Import, gut testbar)
    emails.py             Rendering der E-Mail-Vorlagen + Outbox-Schreiben
    excel_export.py       Export in Reservationsliste.xlsx-kompatibles Format
    routes.py             Flask-Routen (Formular, Sekretariats-Ansicht)
    templates/            Jinja2-HTML-Templates
    static/               CSS
  email_templates/        Text-Vorlagen mit {{ platzhaltern }} (abgeleitet aus den .eml-Originalen)
  data/                   Laufzeitdaten (DB, Outbox) — nicht versioniert
  exports/                Excel-Exporte — nicht versioniert
  tests/                  pytest-Tests
  docs/
    original-unterlagen/  Unveränderte Originaldateien des Fallbeispiels
  CLAUDE.md
  TODO.md
  Projektdokumentation.md Abgabedokument für die Lehrperson
  requirements.txt
```

## Regeln für die Zusammenarbeit

- `TODO.md` nach jedem abgeschlossenen Schritt aktualisieren (Checkbox abhaken, bei Bedarf
  Unterpunkte ergänzen).
- Nach jedem funktionsfähigen Modul einen eigenen Git-Commit erstellen (kleine, nachvollziehbare
  Schritte statt einem Riesen-Commit am Ende).
- Verfügbarkeits-/Konfliktlogik immer mit Unit-Tests absichern, bevor sie in die Flask-Routen
  eingebaut wird.
- Keine echten E-Mails versenden, keine externen Dienste anbinden — alles lokal/Testumgebung.
- Deutsch für alle fachlichen/domänenbezogenen Texte (UI, Vorlagen, Doku), da Fallbeispiel und
  Zielgruppe (Lehrperson, Sekretariat) deutschsprachig sind.
- Abweichungen vom Original-Prozess (siehe oben) nachvollziehbar in der Projektdokumentation
  begründen, nicht stillschweigend einführen.
