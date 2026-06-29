# reemplaza la función dashboard() por esto

from flask import Flask, render_template, request
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
    window = request.args.get('window', 'all')
    
    intervals = {
        '5m': '5 MINUTE',
        '15m': '15 MINUTE',
        '1h': '1 HOUR',
        '24h': '24 HOUR'
    }
    
    filter_sql = ""
    if window in intervals:
        filter_sql = f"WHERE fecha >= NOW() - INTERVAL {intervals[window]} "

    cur = mysql.connection.cursor()

    # Traer consumos (filtrados por tiempo)
    cur.execute(f"SELECT nodo, consumo, fecha, prioridad FROM consumos {filter_sql}ORDER BY fecha ASC;")
    rows = cur.fetchall()

    data_por_nodo = {}
    for nodo, consumo, fecha, prioridad in rows:
        fecha_str = fecha.strftime("%Y-%m-%dT%H:%M:%S")
        if nodo not in data_por_nodo:
            data_por_nodo[nodo] = {
                "puntos": [],
                "prioridad": prioridad
            }
        data_por_nodo[nodo]["puntos"].append({"x": fecha_str, "y": float(consumo)})

    # Traer totales (filtrados por tiempo)
    cur.execute(f"SELECT potencia, corriente, tension, consumo_total, fecha FROM totales {filter_sql}ORDER BY fecha ASC;")
    rows_totales = cur.fetchall()

    totales = {
        "fechas": [],  # Se mantiene para la compatibilidad general
        "potencia": [],
        "corriente": [],
        "tension": [],
        "consumo_total": []
    }
    for potencia, corriente, tension, consumo_total, fecha in rows_totales:
        fecha_str = fecha.strftime("%Y-%m-%dT%H:%M:%S")
        totales["fechas"].append(fecha_str)
        totales["potencia"].append({"x": fecha_str, "y": float(potencia)})
        totales["corriente"].append({"x": fecha_str, "y": float(corriente)})
        totales["tension"].append({"x": fecha_str, "y": float(tension)})
        totales["consumo_total"].append({"x": fecha_str, "y": float(consumo_total)})

    cur.close()
    return render_template('index.html', data_por_nodo=data_por_nodo, totales=totales)

    cur.close()
    return render_template('index.html', data_por_nodo=data_por_nodo, totales=totales)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
