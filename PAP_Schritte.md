# PAP (mit Zeilenarten + Next-ID)

Zeilenarten: `Ablauf`, `Unterprogramm`, `Verzweigung`.

## 1) Hauptablauf (`main`)

| ID | Typ | Inhalt | Nächste ID (normal) | Nächste ID (true) | Nächste ID (false) |
|---|---|---|---|---|---|
| <a id="p-01"></a>P-01 | Ablauf | Start | [P-02](#p-02) | - | - |
| <a id="p-02"></a>P-02 | Unterprogramm | Daten laden und Modelle bauen (`load_data`, `build_models`) | [P-03](#p-03) | - | - |
| <a id="p-03"></a>P-03 | Unterprogramm | Sessions erzeugen (`create_sessions`) | [P-04](#p-04) | - | - |
| <a id="p-04"></a>P-04 | Unterprogramm | Domänen erzeugen (`create_domains`) | [P-05](#p-05) | - | - |
| <a id="p-05"></a>P-05 | Unterprogramm | Planung starten (`solve_timetable`) | [P-06](#p-06) | - | - |
| <a id="p-06"></a>P-06 | Verzweigung | Lösung gefunden? | - | [P-07](#p-07) | [P-08](#p-08) |
| <a id="p-07"></a>P-07 | Unterprogramm | Lösung ausgeben + Excel exportieren | [P-09](#p-09) | - | - |
| <a id="p-08"></a>P-08 | Ablauf | "Keine Lösung" ausgeben | [P-09](#p-09) | - | - |
| <a id="p-09"></a>P-09 | Ablauf | Ende | - | - | - |

---

## 2) Algorithmus (`solve_timetable` / `_search_recursive`)

| ID | Typ | Inhalt | Nächste ID (normal) | Nächste ID (true) | Nächste ID (false) |
|---|---|---|---|---|---|
| <a id="a-01"></a>A-01 | Ablauf | Start Backtracking mit leerem Plan | [A-02](#a-02) | - | - |
| <a id="a-02"></a>A-02 | Verzweigung | Alle Sessions eingeplant? | - | [A-10](#a-10) | [A-03](#a-03) |
| <a id="a-03"></a>A-03 | Unterprogramm | Nächste Session + Werte wählen (`_select_session_and_values`) | [A-04](#a-04) | - | - |
| <a id="a-04"></a>A-04 | Verzweigung | Gibt es Kandidatenwerte? | - | [A-05](#a-05) | [A-11](#a-11) |
| <a id="a-05"></a>A-05 | Unterprogramm | Aktuellen Kandidaten auswählen (z. B. K1, dann K2, dann K3) | [A-06](#a-06) | - | - |
| <a id="a-06"></a>A-06 | Verzweigung | `constraints_ok` erfüllt? | - | [A-07](#a-07) | [A-12](#a-12) |
| <a id="a-07"></a>A-07 | Unterprogramm | Wert eintragen, optional Forward-Check | [A-08](#a-08) | - | - |
| <a id="a-08"></a>A-08 | Unterprogramm | Rekursiv weitersuchen (`_search_recursive`) | [A-09](#a-09) | - | - |
| <a id="a-09"></a>A-09 | Verzweigung | Rekursion erfolgreich? | - | [A-10](#a-10) | [A-12](#a-12) |
| <a id="a-12"></a>A-12 | Verzweigung | Gibt es einen weiteren Kandidaten? | - | [A-05](#a-05) *(nächsten Kandidaten prüfen)* | [A-11](#a-11) |
| <a id="a-10"></a>A-10 | Ablauf | Lösung zurückgeben | - | - | - |
| <a id="a-11"></a>A-11 | Ablauf | Backtrack / `None` zurückgeben | - | - | - |

---

## Kurz zum Zeichnen

- `Verzweigung`: nutze zwei ausgehende Kanten (`true` und `false`) zu den verlinkten IDs.
- Wiederholungen werden über `Verzweigung` mit Rückverweis auf frühere IDs modelliert (kein eigener Schleife-Typ).
- `Unterprogramm`: als Prozesskasten mit Funktionsnamen im Kasten beschriften.