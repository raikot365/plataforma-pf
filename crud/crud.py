from flask import Flask, render_template
from flask_mysqldb import MySQL
import os, logging

logging.basicConfig(format='%(asctime)s - Dashboard - %(levelname)s - %(message)s', level=logging.INFO)

app = Flask(__name__)


# Configuración MySQL
app.config["MYSQL_USER"] = os.environ["MYSQL_USER"]
app.config["MYSQL_PASSWORD"] = os.environ["MYSQL_PASSWORD"]
app.config["MYSQL_DB"] = os.environ["MYSQL_DB"]
app.config["MYSQL_HOST"] = os.environ["MYSQL_HOST"]
mysql = MySQL(app)

@app.route('/')
def dashboard():
    cur = mysql.connection.cursor()

    # Consulta de mediciones por nodo
    cur.execute("SELECT nodo, consumo, fecha FROM consumos ORDER BY fecha ASC;")
    rows = cur.fetchall()
    data_por_nodo = {}
    for nodo, consumo, fecha in rows:
        data_por_nodo.setdefault(nodo, {"fechas": [], "consumos": []})
        data_por_nodo[nodo]["fechas"].append(fecha.strftime("%H:%M"))
        data_por_nodo[nodo]["consumos"].append(float(consumo))

    # Consulta de totales
    cur.execute("SELECT potencia, corriente, tension, consumo_total, fecha FROM totales ORDER BY fecha ASC;")
    rows_totales = cur.fetchall()
    totales = {
        "fechas": [r[4].strftime("%H:%M") for r in rows_totales],
        "potencia": [float(r[0]) for r in rows_totales],
        "corriente": [float(r[1]) for r in rows_totales],
        "tension": [float(r[2]) for r in rows_totales],
        "consumo_total": [float(r[3]) for r in rows_totales],
    }

    cur.close()
    return render_template('index.html', data_por_nodo=data_por_nodo, totales=totales)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
