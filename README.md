# Kuluhaldur

Pythoni projekt kulude ja tulude haldamiseks.

## Käivitamine

```
python main.py
```

Python 3.10 või uuem peab olema installitud.

## Mida programm teeb

- saab lisada kulutusi ja tulusid
- salvestab andmed andmebaasi (SQLite)
- näitab kuukokkuvõtet
- saab seada eelarve limiite
- ekspordi andmed CSV faili (exceliga avamiseks)

## Failid

- main.py - peaprogramm, kõik klassid ja menüü ühes failis

## Kasutatud tehnoloogiad

- Python
- SQLite (andmebaas)
- csv moodul (eksport)

## Tööajatabel

| Kuupäev | Tegevus | Kirjeldus | Aeg / h |
|---|---|---|---|
| 07.04 | Planeerimine | Projekti ulatuse määramine, klasside (Transaction, Category) struktuuri visandamine paberil. | 3 |
| 10.04 | Andmebaasi kiht | database/db_manager.py loomine. SQLite tabelite loomine ja ühenduse testimine. | 5 |
| 13.04 | Mudelite arendus | models/ kausta failide loomine. Andmete valideerimise loogika (nt et kulu ei oleks negatiivne). | 6 |
| 16.04 | Äriloogika | budget.py arendamine – saldo arvutamine, sissetulekute ja väljaminekute grupeerimine. | 5 |
| 19.04 | Kasutajaliides (CLI) | main.py ja peamenüü ehitamine. input() kontrollid, et programm sisendi peale kokku ei jookseks. | 7 |
| 22.04 | Andmete eksport | utils/csv_export.py funktsionaalsus. CSV faili kirjatamise ja andmete formaatimise testimine. | 4 |
| 26.04 | Refaktoreerimine | Koodi korrastamine, korduvate osade funktsioonidesse tõstmine, vigade jahtimine. | 6 |
| 02.05 | Lõpetamine | Viimased parandused, README.md vormistamine ja projekti ettevalmistus kaitsmiseks. | 6 |
| | **Kokku** | | **42 h** |
