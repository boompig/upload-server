from flask import Flask
from flask import request, render_template, redirect, url_for
import os
import psycopg2
import subprocess
from werkzeug import secure_filename

# app configuration
app = Flask(__name__, static_url_path="/static")
app.config['UPLOAD_FOLDER'] = "static/uploads"
ALLOWED_EXTENSIONS=['png']


# database methods
def connect_to_db():
    return psycopg2.connect(dbname="dbkats", user="dbkats", password="")


def save_to_db(exp_num, val):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO experiments (exp_num, value) VALUES (%s, %s);", (exp_num, val))
    conn.commit()
    conn.close()


def save_pic(exp_num, fname):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO pics (exp_num, fname) VALUES (%s, %s);", (exp_num, fname))
    conn.commit()
    conn.close()


def get_pics():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pics ORDER BY exp_num")
    rows = cur.fetchall()
    conn.close()
    return rows


def read_from_db():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM experiments ORDER BY exp_num")
    rows = cur.fetchall()
    conn.close()
    return rows


# routing methods
@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/upload", methods=["GET"])
def upload_view():
    return render_template("upload.html")


def allowed_filename(fname):
    return fname.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["POST"])
def do_upload():
    f = request.files['file']
    exp_num = request.form['exp_num']
    if f and exp_num and allowed_filename(f.filename):
        new_fname = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], new_fname))
        save_pic(int(exp_num), new_fname)
        return redirect(url_for("index"))
    else:
        return "something went wrong"


@app.route("/add", methods=["POST"])
def add_nums():
    """TODO legacy, do not use"""
    exp_num = int(request.form['exp_num'])
    num1 = int(request.form['num1'])
    num2 = int(request.form['num2'])

    val = subprocess.check_output("python add.py %d %d" % (num1, num2), shell=True)

    # write value in database
    print "saving"
    save_to_db(exp_num, val)

    return "value is %s. <a href='http://localhost:5000/'>back</a>" % val

@app.route("/show", methods=["GET"])
def show_nums():
    data = read_from_db()
    pics = get_pics()
    return render_template("nums.html", data=data, pics=pics)

if __name__ == "__main__":
    app.debug = True
    app.run()
