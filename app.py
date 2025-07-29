from flask import Flask, render_template, jsonify, send_file, make_response, request
import mysql.connector
import csv
import io
import os

app = Flask(__name__)
DB_TABLE = 'lecturas2'

def get_mysql_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE')
        )
    except mysql.connector.Error as err:
        print(f"❌ Error de conexión a MySQL: {err}")
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data")
def api_data():
    conn = get_mysql_connection()
    if conn is None:
        return jsonify({"columns": [], "data": []}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        # Obtener columnas en orden
        cursor.execute(f"SHOW COLUMNS FROM {DB_TABLE}")
        columnas = [col[0] for col in cursor.fetchall()]

        # Obtener datos ordenados
        cursor.execute(f"SELECT * FROM {DB_TABLE} ORDER BY timestamp DESC")
        filas = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Error al obtener datos: {e}")
        columnas = []
        filas = []
    finally:
        cursor.close()
        conn.close()

    return jsonify({"columns": columnas, "data": filas})

# Resto de rutas como /descargar_csv se mantienen igual

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

