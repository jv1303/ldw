from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "uma_chave_secreta_muito_segura" 

DATABASE = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

@app.route("/")
def index():
    with get_db_connection() as conn:
        users = conn.execute("SELECT * FROM users").fetchall()
    return render_template("index.html", users=users)

@app.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip()

        if not nome or not email:
            flash("Nome e e-mail são obrigatórios!", "erro")
        else:
            with get_db_connection() as conn:
                conn.execute("INSERT INTO users (nome, email) VALUES (?, ?)", (nome, email))
                conn.commit()
            flash("Usuário criado com sucesso!", "sucesso")
            return redirect(url_for("index"))

    return render_template("create.html")

@app.route("/edit/<int:id>", methods=("GET", "POST"))
def edit(id):
    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (id,)).fetchone()

    if user is None:
        flash("Usuário não encontrado.", "erro")
        return redirect(url_for("index"))

    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip()

        if not nome or not email:
            flash("Nome e e-mail são obrigatórios!", "erro")
        else:
            with get_db_connection() as conn:
                conn.execute("UPDATE users SET nome=?, email=? WHERE id=?", (nome, email, id))
                conn.commit()
            flash("Usuário atualizado com sucesso!", "sucesso")
            return redirect(url_for("index"))

    return render_template("edit.html", user=user)

@app.route("/delete/<int:id>", methods=("POST",))
def delete(id):
    with get_db_connection() as conn:
        conn.execute("DELETE FROM users WHERE id=?", (id,))
        conn.commit()
    flash("Usuário deletado com sucesso!", "sucesso")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
    