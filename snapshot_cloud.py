"""
snapshot_cloud.py: guarda una foto de BiciMAD en data/AAAA-MM-DD.csv (fecha UTC) y termina.
Lo ejecuta GitHub Actions cada hora. Si la API falla tras 3 intentos, termina con error (el workflow sale en rojo).
"""
import csv
import datetime as dt
import sys
import time
from pathlib import Path

import requests

URL = "https://api.citybik.es/v2/networks/bicimad"
DATA = Path(__file__).resolve().parent / "data"


def descargar():
    for intento in range(3):
        try:
            r = requests.get(URL, timeout=30)
            r.raise_for_status()
            return r.json()["network"]["stations"]
        except Exception as e:
            print(f"intento {intento + 1} fallido: {e}", file=sys.stderr)
            time.sleep(10)
    return None


def guardar(estaciones, ahora):
    DATA.mkdir(exist_ok=True)
    fichero = DATA / f"{ahora:%Y-%m-%d}.csv"
    nuevo = not fichero.exists()
    ts = ahora.isoformat(timespec="seconds")
    with open(fichero, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["station_id", "ts", "free_bikes", "empty_slots"])
        w.writerows([(s["id"], ts, s["free_bikes"], s["empty_slots"]) for s in estaciones])
    return fichero


def main():
    estaciones = descargar()
    if estaciones is None:
        sys.exit("No se pudo descargar BiciMAD")
    f = guardar(estaciones, dt.datetime.now(dt.timezone.utc))
    print(f"OK {len(estaciones)} estaciones -> {f.name}")


if __name__ == "__main__":
    main()