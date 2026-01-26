# reemplaza la función dashboard() por esto

from flask import Flask, render_template
from flask_mysqldb import MySQL
import os, logging
from datetime import datetime

logging.basicConfig(format='%(asctime)s - Dashboard - %(levelname)s - %(message)s', level=logging.INFO)

app = Flask(__name__)

app.config["MYSQL_USER"] = os.environ["MYSQL_USER"]
app.config["MYSQL_PASSWORD"] = os.environ["MYSQL_PASSWORD"]
app.config["MYSQL_DB"] = os.environ["MYSQL_DB"]
app.config["MYSQL_HOST"] = os.environ["MYSQL_HOST"]
mysql = MySQL(app)

@app.route('/')
def dashboard():
    cur = mysql.connection.cursor()

    # Traer consumos (ahora también con prioridad)
    cur.execute("SELECT nodo, consumo, fecha, prioridad FROM consumos ORDER BY fecha ASC;")
    rows = cur.fetchall()

    # nodo -> list of (ts_ms, consumo, fecha_dt)
    data_por_nodo_temp = {}
    consumos_ts = set()

    for nodo, consumo, fecha, prioridad in rows:
        ts_ms = int(fecha.timestamp() * 1000)
        consumos_ts.add(ts_ms)

        # Inicializa si no existe el nodo
        if nodo not in data_por_nodo_temp:
            data_por_nodo_temp[nodo] = {
                "fechas": [],
                "consumos": [],
                "prioridad": prioridad  # guardamos prioridad una sola vez
            }

        data_por_nodo_temp[nodo]["fechas"].append(ts_ms)
        data_por_nodo_temp[nodo]["consumos"].append(float(consumo))


    # Traer totales
    cur.execute("SELECT potencia, corriente, tension, consumo_total, fecha FROM totales ORDER BY fecha ASC;")
    rows_totales = cur.fetchall()
    totales_temp = []
    totales_ts = set()
    for potencia, corriente, tension, consumo_total, fecha in rows_totales:
        ts_ms = int(fecha.timestamp() * 1000)
        totales_ts.add(ts_ms)
        totales_temp.append({
            "ts": ts_ms,
            "potencia": float(potencia),
            "corriente": float(corriente),
            "tension": float(tension),
            "consumo_total": float(consumo_total),
            "fecha_dt": fecha
        })

    # Intersección de timestamps (solo los que están en ambas tablas)
    intersection_ts = sorted(list(consumos_ts.intersection(totales_ts)))

    if not intersection_ts:
        logging.warning("No hay timestamps coincidentes entre consumos y totales. intersection_ts vacío.")

    # Construir data_por_nodo con prioridad incluida
    data_por_nodo = {}
    for nodo, info in data_por_nodo_temp.items():
        fechas_list = []
        consumos_list = []
        for ts in info["fechas"]:
            if ts in intersection_ts:
                # Convertimos el timestamp a formato legible
                from datetime import datetime
                fecha_dt = datetime.fromtimestamp(ts / 1000)
                fechas_list.append(fecha_dt.strftime("%Y-%m-%dT%H:%M:%S"))

        # Ya tenemos consumos filtrados por los timestamps que cruzan
        for ts, val_ts in zip(info["fechas"], info["consumos"]):
            if ts in intersection_ts:
                consumos_list.append(val_ts)

        data_por_nodo[nodo] = {
            "fechas": fechas_list,
            "consumos": consumos_list,
            "prioridad": info.get("prioridad", None)
        }

    # Construir totales en formato original: dict con listas paralelas
    totales = {
        "fechas": [],
        "potencia": [],
        "corriente": [],
        "tension": [],
        "consumo_total": []
    }
    # iterar sobre intersection_ts en orden y para cada ts tomar el registro de totales correspondiente
    ts_to_totales = { item["ts"]: item for item in totales_temp }
    for ts in intersection_ts:
        t = ts_to_totales.get(ts)
        if t:
            # mantener el mismo formato de fecha ISO usado en nodos (opcional)
            totales["fechas"].append(t["fecha_dt"].strftime("%Y-%m-%dT%H:%M:%S"))
            totales["potencia"].append(t["potencia"])
            totales["corriente"].append(t["corriente"])
            totales["tension"].append(t["tension"])
            totales["consumo_total"].append(t["consumo_total"])

    cur.close()
    return render_template('index.html', data_por_nodo=data_por_nodo, totales=totales)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
