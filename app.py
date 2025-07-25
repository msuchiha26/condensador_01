from flask import Flask, render_template, jsonify, send_file
import mysql.connector
import csv
import io
import os

app = Flask(__name__)

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

@app.route("/api/ultimo")
def api_ultimo():
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM lecturas2 ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(row)

@app.route("/descargar_csv")
def descargar_csv():
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lecturas2")
    rows = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(column_names)
    writer.writerows(rows)
    output.seek(0)

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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
