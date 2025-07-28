from flask import Flask, render_template, jsonify, send_file
import mysql.connector
import csv
import io
import os

app = Flask(__name__)

def get_mysql_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
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

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(column_names)
    writer.writerows(rows)
    output.seek(0)

    cursor.execute("DELETE FROM lecturas2")
    cursor.execute("ALTER TABLE lecturas2 AUTO_INCREMENT = 1")
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
