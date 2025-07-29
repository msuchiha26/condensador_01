from flask import Flask, render_template, jsonify, send_file, make_response, request
import mysql.connector
import csv
import io
import os

app = Flask(__name__)

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

DB_TABLE = os.getenv("MYSQL_TABLE_NAME", "lecturas2")

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
        cursor.execute(f"SHOW COLUMNS FROM {DB_TABLE}")
        columnas = [col["Field"] for col in cursor.fetchall()]

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

@app.route("/descargar_csv", methods=["GET"])
def descargar_csv():
    key = request.args.get("key")
    if key != os.getenv("CSV_SECRET_KEY"):
        return "❌ Acceso no autorizado", 403

    conn = get_mysql_connection()
    if conn is None:
        return "Error al conectar con la base de datos", 500

    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {DB_TABLE}")
        rows = cursor.fetchall()
        if not rows:
            return "No hay datos para exportar", 404
        column_names = [desc[0] for desc in cursor.description]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(column_names)
        writer.writerows(rows)
        output.seek(0)

        cursor.execute(f"DELETE FROM {DB_TABLE}")
        cursor.execute(f"ALTER TABLE {DB_TABLE} AUTO_INCREMENT = 1")
        conn.commit()
    except mysql.connector.Error as e:
        print(f"Error durante exportación o borrado: {e}")
        return "Error en la exportación de datos", 500
    finally:
        cursor.close()
        conn.close()

    response = send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='lecturas.csv'
    )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


