from flask import Flask, render_template, request, jsonify, Response
import mysql.connector
import csv
import io
import os

app = Flask(__name__)

# Cargar variables de entorno para credenciales
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_TABLE_NAME = os.getenv("MYSQL_TABLE_NAME", "lecturas2")

# Contraseña para descargar CSV
CSV_PASSWORD = os.getenv("CSV_PASSWORD", "1234")  # puedes cambiarla desde Render

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
    connection = get_mysql_connection()
    cursor = connection.cursor()

    # Obtener los últimos 10 registros
    cursor.execute(f"SELECT * FROM {MYSQL_TABLE_NAME} ORDER BY id DESC LIMIT 10")
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    # Revertir para mostrar del más antiguo al más reciente
    rows.reverse()

    return jsonify([dict(zip(columns, row)) for row in rows])

@app.route("/download", methods=["POST"])
def download_data():
    password = request.form.get("password", "")
    if password != CSV_PASSWORD:
        return "Contraseña incorrecta", 403

    connection = get_mysql_connection()
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM {MYSQL_TABLE_NAME}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    writer.writerows(rows)
    output.seek(0)

    # Borrar datos y reiniciar ID
    cursor.execute(f"DELETE FROM {MYSQL_TABLE_NAME}")
    cursor.execute(f"ALTER TABLE {MYSQL_TABLE_NAME} AUTO_INCREMENT = 1")

    connection.commit()
    cursor.close()
    connection.close()

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=datos.csv"}
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
