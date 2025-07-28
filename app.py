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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data")
def api_data():
    conn = get_mysql_connection()
    if conn is None:
        return jsonify([]), 500
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM lecturas2 ORDER BY timestamp DESC")
        rows = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Error al obtener datos: {e}")
        rows = []
    finally:
        cursor.close()
        conn.close()

    response = make_response(jsonify(rows))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

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
        cursor.execute("SELECT * FROM lecturas2")
        rows = cursor.fetchall()
        if not rows:
            return "No hay datos para exportar", 404
        column_names = [desc[0] for desc in cursor.description]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(column_names)
        writer.writerows(rows)
        output.seek(0)

        cursor.execute("DELETE FROM lecturas2")
        cursor.execute("ALTER TABLE lecturas2 AUTO_INCREMENT = 1")
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
