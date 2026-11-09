import os
import sqlite3
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


def create_app(database=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY=os.environ.get("TIENDA_SECRET", "laboratorio-no-produccion"),
                      DATABASE=str(database or os.environ.get("TIENDA_DB", "tienda_e2e.db")))

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close(_error):
        conn = g.pop("db", None)
        if conn is not None:
            conn.close()

    with app.app_context():
        conn = db()
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, nombre TEXT UNIQUE, hash TEXT);
        CREATE TABLE IF NOT EXISTS productos (id INTEGER PRIMARY KEY, nombre TEXT, precio INTEGER, stock INTEGER);
        CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY, usuario_id INTEGER, total INTEGER);
        CREATE TABLE IF NOT EXISTS lineas (pedido_id INTEGER, producto_id INTEGER, cantidad INTEGER, precio INTEGER);
        INSERT OR IGNORE INTO productos VALUES (1, 'Teclado', 25, 8);
        INSERT OR IGNORE INTO productos VALUES (2, 'Ratón', 15, 5);
        INSERT OR IGNORE INTO productos VALUES (3, 'Alfombrilla', 10, 12);
        INSERT OR IGNORE INTO productos VALUES (4, 'Monitor 24 pulgadas', 159, 7);
        INSERT OR IGNORE INTO productos VALUES (5, 'Auriculares USB', 39, 11);
        INSERT OR IGNORE INTO productos VALUES (6, 'Webcam HD', 45, 9);
        INSERT OR IGNORE INTO productos VALUES (7, 'Hub USB-C', 29, 15);
        INSERT OR IGNORE INTO productos VALUES (8, 'Memoria USB 64 GB', 12, 22);
        INSERT OR IGNORE INTO productos VALUES (9, 'Disco SSD 1 TB', 89, 6);
        INSERT OR IGNORE INTO productos VALUES (10, 'Soporte portátil', 24, 13);
        INSERT OR IGNORE INTO productos VALUES (11, 'Lámpara LED', 32, 10);
        INSERT OR IGNORE INTO productos VALUES (12, 'Mochila tecnológica', 49, 8);
        INSERT OR IGNORE INTO productos VALUES (13, 'Altavoces compactos', 35, 14);
        INSERT OR IGNORE INTO productos VALUES (14, 'Cable HDMI 2 m', 9, 25);
        """)
        if not conn.execute("SELECT id FROM usuarios WHERE nombre='alumna'").fetchone():
            conn.execute("INSERT INTO usuarios(nombre,hash) VALUES(?,?)", ('alumna',generate_password_hash('clave12345')))
        conn.commit()

    @app.context_processor
    def shared():
        return {'usuario': session.get('nombre'), 'carrito_total': sum(session.get('carrito', {}).values())}

    # Categorías de escaparate. El catálogo y las pruebas conservan los productos originales.
    categorias = {
        'perifericos': {'nombre': 'Periféricos', 'icono': '⌨', 'descripcion': 'Teclados, ratones y accesorios', 'ids': (1, 2, 3, 5, 13)},
        'informatica': {'nombre': 'Informática', 'icono': '▣', 'descripcion': 'Pantallas, almacenamiento y conexiones', 'ids': (4, 7, 8, 9, 14)},
        'estudio': {'nombre': 'Estudio y oficina', 'icono': '✦', 'descripcion': 'Para organizar tu espacio', 'ids': (6, 10, 11, 12)},
    }

    @app.get('/')
    def catalogo():
        productos = db().execute('SELECT * FROM productos ORDER BY id').fetchall()
        categoria = request.args.get('categoria', '').strip()
        busqueda = request.args.get('q', '').strip()
        if categoria in categorias:
            permitidos = categorias[categoria]['ids']
            productos = [p for p in productos if p['id'] in permitidos]
        if busqueda:
            productos = [p for p in productos if busqueda.casefold() in p['nombre'].casefold()]
        return render_template('catalogo.html', productos=productos, categorias=categorias,
                               categoria_actual=categoria, busqueda=busqueda)

    @app.get('/producto/<int:producto_id>')
    def ficha_producto(producto_id):
        producto = db().execute('SELECT * FROM productos WHERE id=?', (producto_id,)).fetchone()
        if producto is None:
            return 'Producto no disponible', 404
        categoria = next((c['nombre'] for c in categorias.values() if producto_id in c['ids']), 'Tienda Aula')
        return render_template('producto.html', producto=producto, categoria=categoria)

    @app.get('/ayuda')
    def ayuda():
        return render_template('ayuda.html')

    @app.route('/entrar',methods=['GET','POST'])
    def entrar():
        if request.method == 'POST':
            nombre = request.form.get('usuario','')
            clave = request.form.get('password','')
            persona = db().execute('SELECT * FROM usuarios WHERE nombre=?',(nombre,)).fetchone()
            if persona and check_password_hash(persona['hash'],clave):
                session.clear(); session['user_id']=persona['id']; session['nombre']=nombre
                flash('Sesión iniciada')
                return redirect(url_for('catalogo'))
            flash('Credenciales incorrectas')
        return render_template('entrar.html')

    @app.post('/salir')
    def salir():
        session.clear()
        return redirect(url_for('catalogo'))

    @app.post('/carrito/anadir/<int:producto_id>')
    def anadir(producto_id):
        try: cantidad = int(request.form.get('cantidad', '1'))
        except ValueError: cantidad = 0
        prod = db().execute('SELECT * FROM productos WHERE id=?',(producto_id,)).fetchone()
        if not prod or cantidad <= 0:
            flash('Cantidad incorrecta'); return redirect(url_for('catalogo'))
        carrito = dict(session.get('carrito', {}))
        nueva = carrito.get(str(producto_id), 0)+cantidad
        if nueva > prod['stock']:
            flash('No hay suficiente stock'); return redirect(url_for('catalogo'))
        carrito[str(producto_id)] = nueva; session['carrito']=carrito
        return redirect(url_for('ver_carrito'))

    @app.get('/carrito')
    def ver_carrito():
        items=[]
        for pid,cantidad in session.get('carrito',{}).items():
            producto=db().execute('SELECT * FROM productos WHERE id=?',(int(pid),)).fetchone()
            if producto: items.append({'producto':producto, 'cantidad':cantidad,'subtotal':producto['precio']*cantidad})
        return render_template('carrito.html',items=items,total=sum(i['subtotal'] for i in items))

    @app.post('/carrito/actualizar/<int:producto_id>')
    def actualizar_carrito(producto_id):
        carrito = dict(session.get('carrito', {}))
        clave = str(producto_id)
        if clave not in carrito:
            flash('El producto no está en el carrito')
            return redirect(url_for('ver_carrito'))
        try:
            cantidad = int(request.form.get('cantidad', '0'))
        except ValueError:
            flash('Cantidad incorrecta')
            return redirect(url_for('ver_carrito'))
        producto = db().execute('SELECT stock FROM productos WHERE id=?', (producto_id,)).fetchone()
        if cantidad < 0 or not producto or cantidad > producto['stock']:
            flash('Cantidad incorrecta o stock insuficiente')
            return redirect(url_for('ver_carrito'))
        if cantidad == 0:
            carrito.pop(clave, None)
            flash('Producto eliminado del carrito')
        else:
            carrito[clave] = cantidad
            flash('Carrito actualizado')
        session['carrito'] = carrito
        return redirect(url_for('ver_carrito'))

    @app.post('/carrito/vaciar')
    def vaciar():
        session['carrito']={}; return redirect(url_for('ver_carrito'))

    @app.post('/comprar')
    def comprar():
        if 'user_id' not in session:
            flash('Inicia sesión para comprar'); return redirect(url_for('entrar'))
        carrito=session.get('carrito',{})
        if not carrito: flash('Carrito vacío'); return redirect(url_for('ver_carrito'))
        conn=db()
        try:
            conn.execute('BEGIN IMMEDIATE')
            items=[]
            for pid,cantidad in carrito.items():
                prod=conn.execute('SELECT * FROM productos WHERE id=?',(int(pid),)).fetchone()
                if not prod or cantidad <= 0 or prod['stock'] < cantidad:
                    conn.rollback(); flash('Stock insuficiente'); return redirect(url_for('ver_carrito'))
                items.append((prod,cantidad))
            total=sum(p['precio']*cantidad for p,cantidad in items)
            cur=conn.execute('INSERT INTO pedidos(usuario_id,total) VALUES(?,?)',(session['user_id'],total))
            for prod,cantidad in items:
                conn.execute('INSERT INTO lineas VALUES(?,?,?,?)',(cur.lastrowid,prod['id'],cantidad,prod['precio']))
                conn.execute('UPDATE productos SET stock=stock-? WHERE id=?',(cantidad,prod['id']))
            conn.commit()
        except Exception:
            conn.rollback(); raise
        session['carrito']={}
        return redirect(url_for('pedido',pedido_id=cur.lastrowid))

    @app.get('/pedidos')
    def pedidos():
        if 'user_id' not in session: return redirect(url_for('entrar'))
        lista=db().execute('SELECT * FROM pedidos WHERE usuario_id=? ORDER BY id DESC',(session['user_id'],)).fetchall()
        return render_template('pedidos.html',pedidos=lista)

    @app.get('/pedidos/<int:pedido_id>')
    def pedido(pedido_id):
        if 'user_id' not in session: return redirect(url_for('entrar'))
        pedido=db().execute('SELECT * FROM pedidos WHERE id=? AND usuario_id=?',(pedido_id,session['user_id'])).fetchone()
        if pedido is None: return 'Pedido no disponible',404
        lineas=db().execute('SELECT productos.nombre,lineas.cantidad,lineas.precio FROM lineas JOIN productos ON productos.id=lineas.producto_id WHERE pedido_id=?',(pedido_id,)).fetchall()
        return render_template('pedido.html',pedido=pedido,lineas=lineas)

    return app


if __name__ == '__main__':
    create_app().run(port=5002,debug=False)
