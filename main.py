# Kuluhaldur - kulude ja tulude jalgimise programm
# autor: h7zqc

import sqlite3
import csv
import os
from datetime import datetime


#  KLASSID 

class Transaction:
    def __init__(self, summa, kirjeldus, kategooria, tyup, kuupaev, id=None):
        self.id = id
        self.summa = summa
        self.kirjeldus = kirjeldus
        self.kategooria = kategooria
        self.tyup = tyup
        self.kuupaev = kuupaev

    def getSumma(self):
        if self.tyup == "kulu":
            return "-" + str(self.summa) + " €"
        else:
            return "+" + str(self.summa) + " €"

    def __str__(self):
        return self.kuupaev + " | " + self.kirjeldus + " | " + self.kategooria + " | " + self.getSumma()


class Category:
    def __init__(self, nimi, tyup="kulu", id=None):
        self.id = id
        self.nimi = nimi
        self.tyup = tyup

    def __str__(self):
        return self.nimi + " (" + self.tyup + ")"


class Budget:
    def __init__(self, kategooria, limiit, id=None):
        self.id = id
        self.kategooria = kategooria
        self.limiit = limiit

    def getJaak(self, kulutatud):
        return self.limiit - kulutatud

    def kontrolli(self, kulutatud):
        jaak = self.getJaak(kulutatud)
        if jaak < 0:
            print("HOIATUS: eelarve on ületatud! üle läinud: " + str(abs(round(jaak, 2))) + " €")
        elif self.limiit > 0 and kulutatud / self.limiit >= 0.8:
            print("HOIATUS: eelarve on peaaegu täis! jääk: " + str(round(jaak, 2)) + " €")
        else:
            print("Eelarve ok, jääk: " + str(round(jaak, 2)) + " €")

    def __str__(self):
        return self.kategooria + " eelarve: " + str(self.limiit) + " €"


#  ANDMEBAAS 

class DatabaseManager:

    def __init__(self, db_tee="kulud.db"):
        self.db_tee = db_tee
        self.looTabelid()

    def looTabelid(self):
        conn = sqlite3.connect(self.db_tee)
        conn.execute("""CREATE TABLE IF NOT EXISTS tehingud (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summa REAL,
            kirjeldus TEXT,
            kategooria TEXT,
            tyup TEXT,
            kuupaev TEXT
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS kategoriad (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nimi TEXT,
            tyup TEXT
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS eelarved (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kategooria TEXT,
            limiit REAL
        )""")
        conn.commit()
        arv = conn.execute("SELECT COUNT(*) FROM kategoriad").fetchone()[0]
        if arv == 0:
            vaikimisi = [("Toit", "kulu"), ("Transport", "kulu"),
                         ("Eluase", "kulu"), ("Meelelahutus", "kulu"),
                         ("Palk", "tulu"), ("Muu", "kulu")]
            for nimi, tyup in vaikimisi:
                conn.execute("INSERT INTO kategoriad (nimi, tyup) VALUES (?, ?)", (nimi, tyup))
            conn.commit()
        conn.close()

    def lisaTehing(self, t):
        conn = sqlite3.connect(self.db_tee)
        cursor = conn.execute(
            "INSERT INTO tehingud (summa, kirjeldus, kategooria, tyup, kuupaev) VALUES (?, ?, ?, ?, ?)",
            (t.summa, t.kirjeldus, t.kategooria, t.tyup, t.kuupaev)
        )
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def kustutaTehing(self, id):
        conn = sqlite3.connect(self.db_tee)
        conn.execute("DELETE FROM tehingud WHERE id = ?", (id,))
        conn.commit()
        conn.close()

    def kõikTehingud(self, tyup=None, kuu=None):
        conn = sqlite3.connect(self.db_tee)
        if tyup and kuu:
            read = conn.execute(
                "SELECT * FROM tehingud WHERE tyup=? AND kuupaev LIKE ? ORDER BY kuupaev DESC",
                (tyup, kuu + "%")
            ).fetchall()
        elif tyup:
            read = conn.execute(
                "SELECT * FROM tehingud WHERE tyup=? ORDER BY kuupaev DESC", (tyup,)
            ).fetchall()
        elif kuu:
            read = conn.execute(
                "SELECT * FROM tehingud WHERE kuupaev LIKE ? ORDER BY kuupaev DESC",
                (kuu + "%",)
            ).fetchall()
        else:
            read = conn.execute("SELECT * FROM tehingud ORDER BY kuupaev DESC").fetchall()
        conn.close()
        tehingud = []
        for r in read:
            tehingud.append(Transaction(r[1], r[2], r[3], r[4], r[5], r[0]))
        return tehingud

    def leidTehing(self, id):
        conn = sqlite3.connect(self.db_tee)
        r = conn.execute("SELECT * FROM tehingud WHERE id=?", (id,)).fetchone()
        conn.close()
        if r:
            return Transaction(r[1], r[2], r[3], r[4], r[5], r[0])
        return None

    def lisaKategooria(self, k):
        conn = sqlite3.connect(self.db_tee)
        conn.execute("INSERT INTO kategoriad (nimi, tyup) VALUES (?, ?)", (k.nimi, k.tyup))
        conn.commit()
        conn.close()

    def kustutaKategooria(self, nimi):
        conn = sqlite3.connect(self.db_tee)
        conn.execute("DELETE FROM kategoriad WHERE nimi=?", (nimi,))
        conn.commit()
        conn.close()

    def kõikKategooriad(self, tyup=None):
        conn = sqlite3.connect(self.db_tee)
        if tyup:
            read = conn.execute("SELECT * FROM kategoriad WHERE tyup=? ORDER BY nimi", (tyup,)).fetchall()
        else:
            read = conn.execute("SELECT * FROM kategoriad ORDER BY nimi").fetchall()
        conn.close()
        kategoriad = []
        for r in read:
            kategoriad.append(Category(r[1], r[2], r[0]))
        return kategoriad

    def seaEelarve(self, b):
        conn = sqlite3.connect(self.db_tee)
        olemas = conn.execute("SELECT id FROM eelarved WHERE kategooria=?", (b.kategooria,)).fetchone()
        if olemas:
            conn.execute("UPDATE eelarved SET limiit=? WHERE kategooria=?", (b.limiit, b.kategooria))
        else:
            conn.execute("INSERT INTO eelarved (kategooria, limiit) VALUES (?, ?)", (b.kategooria, b.limiit))
        conn.commit()
        conn.close()

    def leidEelarve(self, kategooria):
        conn = sqlite3.connect(self.db_tee)
        r = conn.execute("SELECT * FROM eelarved WHERE kategooria=?", (kategooria,)).fetchone()
        conn.close()
        if r:
            return Budget(r[1], r[2], r[0])
        return None

    def kõikEelarved(self):
        conn = sqlite3.connect(self.db_tee)
        read = conn.execute("SELECT * FROM eelarved").fetchall()
        conn.close()
        eelarved = []
        for r in read:
            eelarved.append(Budget(r[1], r[2], r[0]))
        return eelarved

    def saldo(self, kuu=None):
        conn = sqlite3.connect(self.db_tee)
        if kuu:
            tulu = conn.execute("SELECT SUM(summa) FROM tehingud WHERE tyup='tulu' AND kuupaev LIKE ?", (kuu+"%",)).fetchone()[0]
            kulu = conn.execute("SELECT SUM(summa) FROM tehingud WHERE tyup='kulu' AND kuupaev LIKE ?", (kuu+"%",)).fetchone()[0]
        else:
            tulu = conn.execute("SELECT SUM(summa) FROM tehingud WHERE tyup='tulu'").fetchone()[0]
            kulu = conn.execute("SELECT SUM(summa) FROM tehingud WHERE tyup='kulu'").fetchone()[0]
        conn.close()
        if tulu is None:
            tulu = 0
        if kulu is None:
            kulu = 0
        return tulu - kulu


#  RAPORT 

class Report:
    def __init__(self, db):
        self.db = db

    def kuuKokkuvote(self, kuu):
        tehingud = self.db.kõikTehingud(kuu=kuu)
        if len(tehingud) == 0:
            print("Selle kuu kohta pole tehinguid")
            return
        tulu = 0
        kulu = 0
        for t in tehingud:
            if t.tyup == "tulu":
                tulu = tulu + t.summa
            else:
                kulu = kulu + t.summa
        saldo = tulu - kulu
        print("=== KOKKUVÕTE " + kuu + " ===")
        print("Tulu:  " + str(round(tulu, 2)) + " €")
        print("Kulu:  " + str(round(kulu, 2)) + " €")
        print("---")
        print("Saldo: " + str(round(saldo, 2)) + " €")

    def viimased(self, n=10):
        tehingud = self.db.kõikTehingud()
        if len(tehingud) == 0:
            print("Tehinguid pole")
            return
        print("\nViimased tehingud:")
        for i in range(min(n, len(tehingud))):
            print(str(tehingud[i].id) + ". " + str(tehingud[i]))


#  CSV 

class CSVExporter:
    def ekspordi(self, tehingud, failinimi="eksport.csv"):
        f = open(failinimi, "w", newline="", encoding="utf-8-sig")
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["id", "kuupäev", "kirjeldus", "kategooria", "tüüp", "summa"])
        for t in tehingud:
            writer.writerow([t.id, t.kuupaev, t.kirjeldus, t.kategooria, t.tyup, t.summa])
        f.close()
        print("Eksporditud " + str(len(tehingud)) + " tehingut faili: " + failinimi)


#  MENÜÜ 

def hetkKuu():
    return datetime.today().strftime("%Y-%m")

def küsiArv(tekst):
    while True:
        try:
            arv = float(input(tekst).replace(",", "."))
            return arv
        except:
            print("Palun sisesta number!")

def valiKategooria(db, tyup=None):
    kategoriad = db.kõikKategooriad(tyup)
    print("\nKategooriad:")
    for i in range(len(kategoriad)):
        print(str(i+1) + ". " + kategoriad[i].nimi)
    while True:
        try:
            nr = int(input("Vali number: "))
            if nr >= 1 and nr <= len(kategoriad):
                return kategoriad[nr-1].nimi
        except:
            pass
        print("Vale valik, proovi uuesti")

def lisaTehing(db):
    print("\n--- LISA TEHING ---")
    tyup = input("Tüüp (kulu/tulu): ").strip()
    if tyup != "kulu" and tyup != "tulu":
        print("Vale tüüp!")
        return
    summa = küsiArv("Summa: ")
    kirjeldus = input("Kirjeldus: ")
    kategooria = valiKategooria(db, tyup)
    kuupaev = input("Kuupäev (YYYY-MM-DD), enter = täna: ").strip()
    if kuupaev == "":
        kuupaev = datetime.today().strftime("%Y-%m-%d")
    t = Transaction(summa, kirjeldus, kategooria, tyup, kuupaev)
    uusId = db.lisaTehing(t)
    print("Tehing lisatud! id=" + str(uusId))
    if tyup == "kulu":
        eelarve = db.leidEelarve(kategooria)
        if eelarve != None:
            kuu = kuupaev[:7]
            tehingud = db.kõikTehingud(tyup="kulu", kuu=kuu)
            kokku = 0
            for x in tehingud:
                if x.kategooria == kategooria:
                    kokku = kokku + x.summa
            eelarve.kontrolli(kokku)

def vaataTehinguid(db):
    print("\n--- TEHINGUD ---")
    print("1. Kõik")
    print("2. Kulud")
    print("3. Tulud")
    print("4. Kindel kuu")
    v = input("Vali: ")
    tyup = None
    kuu = None
    if v == "2":
        tyup = "kulu"
    elif v == "3":
        tyup = "tulu"
    elif v == "4":
        kuu = input("Kuu (YYYY-MM): ").strip()
    tehingud = db.kõikTehingud(tyup, kuu)
    if len(tehingud) == 0:
        print("Tehinguid ei leitud")
        return
    for t in tehingud:
        print(str(t.id) + ". " + str(t))
    print("\nKokku: " + str(len(tehingud)) + " tehingut")

def kustutaTehing(db):
    print("\n--- KUSTUTA TEHING ---")
    try:
        id = int(input("Tehingu ID: "))
        t = db.leidTehing(id)
        if t == None:
            print("Tehingut ei leitud")
            return
        print("Kustutan: " + str(t))
        kinnitus = input("Kindel? (jah/ei): ")
        if kinnitus == "jah":
            db.kustutaTehing(id)
            print("Kustutatud!")
    except:
        print("Viga!")

def haldaKategooriad(db):
    print("\n--- KATEGOORIAD ---")
    kategoriad = db.kõikKategooriad()
    for k in kategoriad:
        print("- " + str(k))
    print("\n1. Lisa uus")
    print("2. Kustuta")
    print("3. Tagasi")
    v = input("Vali: ")
    if v == "1":
        nimi = input("Nimi: ")
        tyup = input("Tüüp (kulu/tulu): ")
        db.lisaKategooria(Category(nimi, tyup))
        print("Lisatud!")
    elif v == "2":
        nimi = input("Kustuta: ")
        db.kustutaKategooria(nimi)
        print("Kustutatud!")

def haldaEelarvet(db):
    print("\n--- EELARVE ---")
    eelarved = db.kõikEelarved()
    if len(eelarved) == 0:
        print("Eelarved pole seatud")
    else:
        for b in eelarved:
            print("- " + str(b))
    print("\n1. Sea eelarve")
    print("2. Tagasi")
    v = input("Vali: ")
    if v == "1":
        kat = valiKategooria(db, "kulu")
        limiit = küsiArv("Limiit (€/kuu): ")
        db.seaEelarve(Budget(kat, limiit))
        print("Eelarve seatud!")

def raportid(db):
    print("\n--- RAPORTID ---")
    print("1. Kuukokkuvõte")
    print("2. Viimased 10 tehingut")
    v = input("Vali: ")
    r = Report(db)
    if v == "1":
        kuu = input("Kuu (YYYY-MM), enter = praegune: ").strip()
        if kuu == "":
            kuu = hetkKuu()
        r.kuuKokkuvote(kuu)
    elif v == "2":
        r.viimased(10)

def ekspordiCSV(db):
    print("\n--- CSV EKSPORT ---")
    tehingud = db.kõikTehingud()
    if len(tehingud) == 0:
        print("Pole midagi eksportida")
        return
    failinimi = input("Failinimi (enter = eksport.csv): ").strip()
    if failinimi == "":
        failinimi = "eksport.csv"
    e = CSVExporter()
    e.ekspordi(tehingud, failinimi)

def main():
    db = DatabaseManager()
    while True:
        print("\n============================")
        kuu_saldo = db.saldo(hetkKuu())
        print("  KULUHALDUR | saldo: " + str(round(kuu_saldo, 2)) + " €")
        print("============================")
        print("1. Lisa tehing")
        print("2. Vaata tehinguid")
        print("3. Kustuta tehing")
        print("4. Kategooriad")
        print("5. Eelarve")
        print("6. Raportid")
        print("7. Ekspordi CSV")
        print("0. Välju")
        valik = input("\nVali: ").strip()
        if valik == "1":
            lisaTehing(db)
        elif valik == "2":
            vaataTehinguid(db)
        elif valik == "3":
            kustutaTehing(db)
        elif valik == "4":
            haldaKategooriad(db)
        elif valik == "5":
            haldaEelarvet(db)
        elif valik == "6":
            raportid(db)
        elif valik == "7":
            ekspordiCSV(db)
        elif valik == "0":
            print("Nägemist!")
            break
        else:
            print("Vale valik!")
        input("\nEnter jätkamiseks...")

main()
