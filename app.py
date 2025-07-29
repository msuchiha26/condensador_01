from flask import Flask, render_template, jsonify, send_file, make_response, request
import mysql.connector
import csv
import io
import os

app = Flask(__name__)

# Usa variables de entorno para mayor seguridad
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_TABLE_NAME = os.getenv("MYSQL_TABLE_NAME", "lecturas2")

def get_mysql_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data")
def get_data():
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    # Solo los últimos 10 registros
    cursor.execute(f"SELECT * FROM {MYSQL_TABLE_NAME} ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # Revertimos para que el más reciente quede al final
    rows.reverse()

    return jsonify(rows)

@app.route("/download_csv", methods=["GET"])
def download_csv():
    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {MYSQL_TABLE_NAME}")
    rows = cursor.fetchall()
    headers = [i[0] for i in cursor.description]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)

    # Opcional: vaciar la tabla después de exportar
    cursor.execute(f"DELETE FROM {MYSQL_TABLE_NAME}")
    conn.commit()

    cursor.close()
    conn.close()

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=datos.csv"
    response.headers["Content-type"] = "text/csv"
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


