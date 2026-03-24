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

# --- TELA: MENU PRINCIPAL (DASHBOARD) ---
@app.route("/")
def menu():
    with get_db_connection() as conn:
        resultado = conn.execute("SELECT COUNT(*) FROM users").fetchone()
        total_users = resultado[0] if resultado else 0
        
    return render_template("menu.html", total_users=total_users)

# --- TELA: CONSULTAR ---
@app.route("/consultar")
def consultar():
    with get_db_connection() as conn:
        users = conn.execute("SELECT * FROM users").fetchall()
    return render_template("consultar.html", users=users)

# --- TELA: INSERIR ---
@app.route("/inserir", methods=("GET", "POST"))
def inserir():
    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip()

        if not nome or not email:
            flash("Nome e e-mail são obrigatórios!", "erro")
        else:
            with get_db_connection() as conn:
                conn.execute("INSERT INTO users (nome, email) VALUES (?, ?)", (nome, email))
                conn.commit()
            flash("Usuário inserido com sucesso!", "sucesso")
            return redirect(url_for("inserir"))

    return render_template("inserir.html")

# --- TELAS: ATUALIZAR ---
@app.route("/atualizar")
def atualizar_lista():
    with get_db_connection() as conn:
        users = conn.execute("SELECT * FROM users").fetchall()
    return render_template("atualizar_lista.html", users=users)

@app.route("/atualizar/<int:id>", methods=("GET", "POST"))
def atualizar_form(id):
    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (id,)).fetchone()

    if user is None:
        flash("Usuário não encontrado.", "erro")
        return redirect(url_for("atualizar_lista"))

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
            return redirect(url_for("atualizar_lista"))

    return render_template("atualizar_form.html", user=user)

# --- TELAS: EXCLUIR ---
@app.route("/excluir")
def excluir_lista():
    with get_db_connection() as conn:
        users = conn.execute("SELECT * FROM users").fetchall()
    return render_template("excluir.html", users=users)

@app.route("/excluir/<int:id>", methods=("POST",))
def excluir_acao(id):
    with get_db_connection() as conn:
        conn.execute("DELETE FROM users WHERE id=?", (id,))
        conn.commit()
    flash("Usuário deletado com sucesso!", "sucesso")
    return redirect(url_for("excluir_lista"))

if __name__ == "__main__":
    app.run(debug=True)
    