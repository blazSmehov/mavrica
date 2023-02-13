import sqlite3
from flask import Flask, request, render_template, jsonify
from datetime import datetime
#from flask_cors import CORS
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib.dates
import numpy as np
from flask import redirect, url_for

app = Flask(__name__, static_url_path="/static", static_folder="static")
#CORS(app)

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/graph')
def graph():
    con = sqlite3.connect('mydatabase.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM dezemer")
    rows = cur.fetchall()

    x = [datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') for row in rows]
    y = [row[0] for row in rows]

    dates = matplotlib.dates.date2num(x)

 
    plt.plot_date(x, y)
    plt.xlabel('String Value')
    plt.ylabel('Double Value')
    plt.title('Dezemer')

    # Create a BytesIO object
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue()).decode('ascii')
    return render_template('graph.html', figdata_png=figdata_png)

@app.route('/')
def index():
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    c.execute("SELECT * FROM dezemer")
    data = c.fetchall()
    conn.close()
    return render_template('index.html', data=data)

@app.route('/display')
def display():
    con = sqlite3.connect('mydatabase.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM dezemer")
    rows = cur.fetchall()
    return render_template('display.html', rows=rows)

@app.route('/data/<data>', methods=['POST', 'GET'])
def handle_post_request(data):

    # save current time
    current_time = datetime.now()
    time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")

    # post request
    #data = request.form['double_value']

    # connect sqlite3 database
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS dezemer (meritev REAL, cas VARCHAR(255))")
    c.execute("INSERT INTO dezemer (meritev, cas) VALUES (?, ?)", (data, time_string))
    conn.commit()
    conn.close()
    return time_string

@app.route('/double_values_data')
def double_values_data():
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    c.execute("SELECT * FROM dezemer")
    results = c.fetchall()
    labels = [i[0] for i in results]
    values = [i[1] for i in results]
    return jsonify({'labels': labels, 'values': values})

@app.route('/eksperimenti', methods=['GET', 'POST'])
def eksperimenti():
    if request.method == 'POST':
        ime = request.form['ime']
        print(f'Dodaj eksperiment: {ime}')
        
        conn = sqlite3.connect('mydatabase.db')
        c = conn.cursor()
        #c.execute("DROP TABLE IF EXISTS eksperimenti")
        c.execute("CREATE TABLE IF NOT EXISTS eksperimenti (id INTEGER PRIMARY KEY AUTOINCREMENT, ime VARCHAR(255), start DATETIME DEFAULT '0000-00-00 00:00:00', stop DATETIME DEFAULT '0000-00-00 00:00:00', timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        c.execute("INSERT INTO eksperimenti (ime) VALUES (?)", (ime,))
        conn.commit()
        conn.close()

        return redirect(url_for('eksperimenti'))

    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    c.execute("SELECT id, ime, timestamp FROM eksperimenti ORDER BY timestamp DESC")
    data = c.fetchall()
    conn.close()
    
    return render_template('eksperimenti.html', data=data)

@app.route('/eksperiment/<id_>', methods=['GET', 'POST'])
def eksperiment(id_):
    if request.method == 'POST':
        action = request.form['action']
        print(f'Eksperiment: {action}')

        current_time = datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect('mydatabase.db')
        c = conn.cursor()
        
        if action == 'start':
            c.execute("UPDATE eksperimenti SET start=? WHERE id==?", (time_string, id_))
            conn.commit()
        elif action == 'stop':
            c.execute("UPDATE eksperimenti SET stop=? WHERE id==?", (time_string, id_))
            conn.commit()
        elif action == 'save':
            #c.execute("DROP TABLE IF EXISTS konfiguracija")
            c.execute("CREATE TABLE IF NOT EXISTS konfiguracija (id INTEGER PRIMARY KEY AUTOINCREMENT, eid INTEGER, izvajalec VARCHAR(255) DEFAULT '', timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
            # v tabelo dodati še višino stojala, lokacijo dežemera pa pretok (eid , visinaStojala, pretok, lokacijaTip, lokacijaVrednost, pritisk) (?,?,?..)
            c.execute("INSERT INTO konfiguracija (eid) VALUES (?)", (id_,))
            conn.commit()

        conn.close()


        
        '''
        conn = sqlite3.connect('mydatabase.db')
        c = conn.cursor()
        #c.execute("DROP TABLE IF EXISTS eksperimenti")
        c.execute("CREATE TABLE IF NOT EXISTS eksperimenti (id INTEGER PRIMARY KEY AUTOINCREMENT, ime VARCHAR(255), start DATETIME DEFAULT '0000-00-00 00:00:00', stop DATETIME DEFAULT '0000-00-00 00:00:00', timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        c.execute("INSERT INTO eksperimenti (ime) VALUES (?)", (ime,))
        conn.commit()
        conn.close()
        '''
        return redirect(url_for('eksperiment', id_=id_))

    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    c.execute("SELECT id, ime, timestamp, start, stop FROM eksperimenti WHERE id==? LIMIT 1", (id_,))
    data = c.fetchall()[0]

    c.execute("SELECT * FROM konfiguracija WHERE eid==?", (id_,))
    conf = c.fetchall()

    conn.close()
    
    #start_disabled = 'disabled' if data[3] != '0000-00-00 00:00:00' else ''
    start_disabled = 'disabled' if data[3] is not None else ''
    stop_disabled = 'disabled' if data[4] is not None else ''
    print("DATA 3 IN 4",data[3],data[4])
    print(data[4] is not None)
    return render_template('eksperiment.html', data=data, start_disabled=start_disabled, stop_disabled=stop_disabled, conf=conf)

if __name__ == '__main__':
    app.run(debug=True, host = '127.0.0.1')
    #app.run()
