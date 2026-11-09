"""Blog Flask de laboratorio para pruebas funcionales, integracion, E2E y seguridad."""
import os
import sqlite3
from functools import wraps
from flask import Flask, abort, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


def create_app(database=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "solo-laboratorio-cambiar"),
                      DATABASE=database or os.environ.get("BLOG_DB", "blog_lab.db"),
                      TESTING=False)

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_error):
        conn = g.pop("db", None)
        if conn is not None:
            conn.close()

    with app.app_context():
        conn = db()
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY, nombre TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY, autor_id INTEGER NOT NULL,
            titulo TEXT NOT NULL, cuerpo TEXT NOT NULL,
            FOREIGN KEY(autor_id) REFERENCES usuarios(id));
        """)
        conn.commit()

    def usuario_actual():
        return session.get("usuario_id")

    def requiere_sesion(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if usuario_actual() is None:
                abort(401)
            return f(*args, **kwargs)
        return wrapper

    @app.get("/")
    def inicio():
        posts = db().execute("SELECT posts.id, titulo, cuerpo, nombre AS autor FROM posts JOIN usuarios ON usuarios.id=posts.autor_id ORDER BY posts.id DESC").fetchall()
        return render_template("index.html", posts=posts, conectado=usuario_actual() is not None)

    @app.route("/registro", methods=["GET", "POST"])
    def registro():
        if request.method == "GET":
            return render_template("registro.html")
        nombre = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")
        if not (3 <= len(nombre) <= 40):
            return render_template("registro.html", error="El usuario debe tener entre 3 y 40 caracteres.", usuario=nombre), 400
        if len(password) < 8:
            return render_template("registro.html", error="La contraseña debe tener al menos 8 caracteres.", usuario=nombre), 400
        try:
            db().execute("INSERT INTO usuarios(nombre,password_hash) VALUES(?,?)", (nombre, generate_password_hash(password)))
            db().commit()
        except sqlite3.IntegrityError:
            return render_template("registro.html", error="Ese nombre de usuario ya está registrado.", usuario=nombre), 409
        return redirect(url_for("entrar", registrado="1"))

    @app.route("/entrar", methods=["GET", "POST"])
    def entrar():
        if request.method == "GET":
            return render_template("entrar.html")
        nombre = request.form.get("usuario", "")
        password = request.form.get("password", "")
        usuario = db().execute("SELECT id,password_hash FROM usuarios WHERE nombre=?", (nombre,)).fetchone()
        if usuario is None or not check_password_hash(usuario["password_hash"], password):
            return render_template("entrar.html", error="Usuario o contraseña incorrectos.", usuario=nombre), 401
        session.clear()
        session["usuario_id"] = usuario["id"]
        return redirect(url_for("inicio"))

    @app.post("/salir")
    def salir():
        session.clear()
        return redirect(url_for("inicio"))

    @app.route("/posts", methods=["GET", "POST"])
    @requiere_sesion
    def posts():
        if request.method == "GET":
            return render_template("nuevo.html")
        titulo = request.form.get("titulo", "").strip()
        cuerpo = request.form.get("cuerpo", "").strip()
        if not (1 <= len(titulo) <= 100) or not (1 <= len(cuerpo) <= 2000):
            abort(400)
        db().execute("INSERT INTO posts(autor_id,titulo,cuerpo) VALUES(?,?,?)", (usuario_actual(), titulo, cuerpo))
        db().commit()
        return redirect(url_for("inicio"))

    @app.post("/posts/<int:post_id>/editar")
    @requiere_sesion
    def editar(post_id):
        post = db().execute("SELECT autor_id FROM posts WHERE id=?", (post_id,)).fetchone()
        if post is None:
            abort(404)
        if post["autor_id"] != usuario_actual():
            abort(403)
        titulo = request.form.get("titulo", "").strip()
        cuerpo = request.form.get("cuerpo", "").strip()
        if not (1 <= len(titulo) <= 100) or not (1 <= len(cuerpo) <= 2000):
            abort(400)
        db().execute("UPDATE posts SET titulo=?, cuerpo=? WHERE id=?", (titulo, cuerpo, post_id))
        db().commit()
        return redirect(url_for("inicio"))

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
