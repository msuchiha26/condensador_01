from flask import Flask, render_template, jsonify, send_file
import mysql.connector
import csv
import io

app = Flask(__name__)

# 📦 Conexión a MySQL
def get_mysql_connection():
    return mysql.connector.connect(
        host='base-condensador.cjagmwui8z8e.us-east-2.rds.amazonaws.com',
        user='msuchiha',
        password='90_Naruto_26',
        database='datos-sensores'
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data")
def api_data():
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM lecturas2 ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route("/descargar_csv")
def descargar_csv():
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lecturas2")
    rows = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]

    # 📁 Generar CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(column_names)
    writer.writerows(rows)

    output.seek(0)

    # 🧹 Borrar datos después de generar CSV
    cursor.execute("DELETE FROM lecturas2")
    conn.commit()

    cursor.close()
    conn.close()

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='lecturas.csv'
    )

if __name__ == "__main__":
    app.run(debug=True)
