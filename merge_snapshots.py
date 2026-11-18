"""
merge_snapshots.py: vuelca los CSV de la nube (carpeta data/) en bicimad_history.db, sin duplicar.
Uso (desde la carpeta del repositorio, tras 'git pull'):  python merge_snapshots.py
"""
import sqlite3
from pathlib import Path

import pandas as pd

DB = Path("bicimad_history.db")
CSVS = sorted(Path("data").glob("*.csv"))

con = sqlite3.connect(DB)
con.execute("""CREATE TABLE IF NOT EXISTS station_status_history(
                 station_id TEXT, ts TEXT, free_bikes INTEGER, empty_slots INTEGER)""")
existentes = {r[0] for r in con.execute("SELECT DISTINCT ts FROM station_status_history")}
nuevas = 0
for c in CSVS:
    df = pd.read_csv(c, dtype={"station_id": str})
    df = df[~df["ts"].isin(existentes)]
    if len(df):
        df.to_sql("station_status_history", con, if_exists="append", index=False)
        existentes |= set(df["ts"])
        nuevas += len(df)
con.commit()
print(f"Filas nuevas: {nuevas} | fotos distintas en total: {len(existentes)}")