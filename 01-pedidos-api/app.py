"""Aplicación didáctica: Flask + SQLite con interfaz y API para pruebas de integración."""
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, redirect, render_template_string, request, url_for

PAGINA = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pedidos - práctica de integración</title>
<style>body{font-family:system-ui,sans-serif;max-width:760px;margin:3rem auto;padding:0 1rem;background:#f6f8fb;color:#182436}main{background:white;padding:2rem;border-radius:12px;box-shadow:0 2px 12px #0001}label{display:block;margin:1rem 0 .3rem}input,button{font:inherit;padding:.6rem}input{width:100%;box-sizing:border-box}button{background:#184e88;color:white;border:0;border-radius:5px;margin-top:1rem;cursor:pointer}table{border-collapse:collapse;width:100%;margin-top:1rem}td,th{border-bottom:1px solid #ddd;text-align:left;padding:.6rem}.error{color:#9a1b1b}</style>
</head><body><main><h1>Gestión de pedidos</h1><p>Crea pedidos y comprueba cómo se almacenan en SQLite.</p>
{% if error %}<p class="error" role="alert">{{ error }}</p>{% endif %}
<form action="{{ url_for('crear_desde_web') }}" method="post">
<label for="producto">Producto</label><input id="producto" name="producto" required maxlength="100">
<label for="unidades">Unidades</label><input id="unidades" name="unidades" type="number" min="1" step="1" required>
<button type="submit">Guardar pedido</button></form>
<h2>Pedidos registrados</h2>
{% if pedidos %}<table><thead><tr><th>ID</th><th>Producto</th><th>Unidades</th></tr></thead><tbody>
{% for pedido in pedidos %}<tr><td>{{ pedido[0] }}</td><td>{{ pedido[1] }}</td><td>{{ pedido[2] }}</td></tr>{% endfor %}
</tbody></table>{% else %}<p>Aún no hay pedidos.</p>{% endif %}
</main></body></html>"""

def create_app(db_path='pedidos.db'):
    app = Flask(__name__)
    app.config['DB_PATH'] = str(db_path)
    with sqlite3.connect(app.config['DB_PATH']) as db:
        db.execute('CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY, producto TEXT NOT NULL, unidades INTEGER NOT NULL)')

    def validar(producto, unidades):
        return isinstance(producto, str) and bool(producto.strip()) and type(unidades) is int and unidades > 0

    def guardar(producto, unidades):
        with sqlite3.connect(app.config['DB_PATH']) as db:
            cursor = db.execute('INSERT INTO pedidos(producto, unidades) VALUES (?, ?)', (producto.strip(), unidades))
            return cursor.lastrowid

    @app.get('/')
    def inicio():
        with sqlite3.connect(app.config['DB_PATH']) as db:
            pedidos = db.execute('SELECT id, producto, unidades FROM pedidos ORDER BY id DESC').fetchall()
        return render_template_string(PAGINA, pedidos=pedidos, error=request.args.get('error'))

    @app.post('/web/pedidos')
    def crear_desde_web():
        producto = request.form.get('producto', '')
        try:
            unidades = int(request.form.get('unidades', ''))
        except ValueError:
            unidades = None
        if not validar(producto, unidades):
            return redirect(url_for('inicio', error='Introduce un producto y un número positivo de unidades.'))
        guardar(producto, unidades)
        return redirect(url_for('inicio'))

    @app.post('/pedidos')
    def crear_pedido():
        datos = request.get_json(silent=True) or {}
        producto, unidades = datos.get('producto'), datos.get('unidades')
        if not validar(producto, unidades):
            return jsonify(error='Datos incorrectos'), 400
        pedido_id = guardar(producto, unidades)
        return jsonify(id=pedido_id, producto=producto.strip(), unidades=unidades), 201

    @app.get('/pedidos/<int:pedido_id>')
    def consultar_pedido(pedido_id):
        with sqlite3.connect(app.config['DB_PATH']) as db:
            fila = db.execute('SELECT id, producto, unidades FROM pedidos WHERE id=?', (pedido_id,)).fetchone()
        if fila is None:
            return jsonify(error='No encontrado'), 404
        return jsonify(id=fila[0], producto=fila[1], unidades=fila[2])

    return app

if __name__ == '__main__':
    create_app(Path(__file__).with_name('pedidos.db')).run(debug=True, host='127.0.0.1', port=5000)
