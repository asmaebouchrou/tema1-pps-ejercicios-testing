
from playwright.sync_api import Page, expect


def test_credenciales_incorrectas(page: Page, servidor):
    url, _ = servidor

    # Abrimos el formulario de acceso.
    page.goto(f"{url}/entrar")

    # Introducimos una contraseña incorrecta.
    page.get_by_label("Usuario").fill("alumna")
    page.get_by_label("Contraseña").fill("incorrecta")
    page.get_by_role("button", name="Iniciar sesión").click()

    # Comprobamos que aparece el mensaje de error.
    expect(page.get_by_role("status")).to_have_text(
        "Credenciales incorrectas"
    )

    # Intentamos acceder al historial de pedidos.
    page.goto(f"{url}/pedidos")

    # Comprobamos que nos redirige al inicio de sesión.
    expect(page).to_have_url(f"{url}/entrar")
    expect(page.get_by_role("heading", name="Mis pedidos")).to_have_count(0)


def test_compra_sin_iniciar_sesion(page: Page, servidor):
    url, _ = servidor

    # Intentamos confirmar una compra sin iniciar sesión.
    respuesta = page.request.post(
        f"{url}/comprar",
        max_redirects=0
    )

    # Comprobamos que devuelve HTTP 302.
    assert respuesta.status == 302

    # Comprobamos que redirige al formulario de acceso.
    assert respuesta.headers["location"] == "/entrar"


def test_historial_protegido(page: Page, servidor):
    url, _ = servidor

    # Intentamos acceder al historial sin iniciar sesión.
    respuesta = page.goto(f"{url}/pedidos")

    # Comprobamos que nos redirige a /entrar.
    expect(page).to_have_url(f"{url}/entrar")

    # Comprobamos que no aparecen datos de pedidos.
    expect(
        page.get_by_role("heading", name="Mis pedidos")
    ).to_have_count(0)

    expect(page.locator(".history-card")).to_have_count(0)


def test_cantidad_cero(page: Page, servidor):
    url, _ = servidor

    # Intentamos añadir cero teclados al carrito.
    respuesta = page.request.post(
        f"{url}/carrito/anadir/1",
        form={"cantidad": "0"}
    )

    # Comprobamos que la tienda rechaza la cantidad.
    assert respuesta.status == 200
    assert "Cantidad incorrecta" in respuesta.text()

    # Abrimos el carrito.
    page.goto(f"{url}/carrito")

    # Comprobamos que sigue vacío.
    expect(
        page.get_by_role("heading", name="El carrito está vacío.")
    ).to_be_visible()

    expect(page.locator("table tbody tr")).to_have_count(0)


def test_cantidad_superior_stock(page: Page, servidor):
    url, _ = servidor

    # Intentamos añadir 9 teclados cuando solo hay 8.
    respuesta = page.request.post(
        f"{url}/carrito/anadir/1",
        form={"cantidad": "9"}
    )

    # Comprobamos que aparece el mensaje de error.
    assert "No hay suficiente stock" in respuesta.text()

    # Abrimos el carrito.
    page.goto(f"{url}/carrito")

    # Comprobamos que sigue vacío.
    expect(
        page.get_by_role("heading", name="El carrito está vacío.")
    ).to_be_visible()

    expect(page.locator("table tbody tr")).to_have_count(0)



def test_compra_carrito_vacio(page: Page, servidor):
    url, _ = servidor

    # Iniciamos sesión.
    page.goto(f"{url}/entrar")
    page.get_by_label("Usuario").fill("alumna")
    page.get_by_label("Contraseña").fill("clave12345")
    page.get_by_role("button", name="Iniciar sesión").click()

    # Intentamos comprar con el carrito vacío.
    respuesta = page.request.post(f"{url}/comprar")

    # Comprobamos que aparece el mensaje de error.
    assert "Carrito vacío" in respuesta.text()

    # Abrimos el historial de pedidos.
    page.goto(f"{url}/pedidos")

    # Comprobamos que no se ha creado ningún pedido.
    expect(
        page.get_by_role("heading", name="Aún no tienes pedidos.")
    ).to_be_visible()

    expect(page.locator(".history-card")).to_have_count(0)


def test_compra_actualiza_inventario(page: Page, servidor):
    url, _ = servidor

    # Iniciamos sesión.
    page.goto(f"{url}/entrar")
    page.get_by_label("Usuario").fill("alumna")
    page.get_by_label("Contraseña").fill("clave12345")
    page.get_by_role("button", name="Iniciar sesión").click()

    # Añadimos dos teclados al carrito.
    page.request.post(
        f"{url}/carrito/anadir/1",
        form={"cantidad": "2"}
    )

    # Confirmamos la compra.
    page.request.post(f"{url}/comprar")

    # Comprobamos el pedido generado.
    page.goto(f"{url}/pedidos/1")

    fila = page.get_by_role("row").filter(has_text="Teclado")
    expect(fila).to_contain_text("2")

    # Volvemos al catálogo para comprobar el stock.
    page.goto(url)

    producto = page.locator("article.producto").filter(
        has=page.get_by_role("heading", name="Teclado", exact=True)
    )

    expect(producto.locator(".stock-count")).to_have_text(
        "Disponibles: 6"
    )


def test_compra_productos_diferentes(page: Page, servidor):
    url, _ = servidor

    # Iniciamos sesión.
    page.goto(f"{url}/entrar")
    page.get_by_label("Usuario").fill("alumna")
    page.get_by_label("Contraseña").fill("clave12345")
    page.get_by_role("button", name="Iniciar sesión").click()

    # Añadimos dos ratones y una alfombrilla.
    page.request.post(
        f"{url}/carrito/anadir/2",
        form={"cantidad": "2"}
    )

    page.request.post(
        f"{url}/carrito/anadir/3",
        form={"cantidad": "1"}
    )

    # Confirmamos la compra.
    page.request.post(f"{url}/comprar")

    # Comprobamos las cantidades y el total del pedido.
    page.goto(f"{url}/pedidos/1")

    fila_raton = page.get_by_role("row").filter(has_text="Ratón")
    fila_alfombrilla = page.get_by_role("row").filter(
        has_text="Alfombrilla"
    )

    expect(fila_raton.locator("td").nth(1)).to_have_text("2")
    expect(fila_alfombrilla.locator("td").nth(1)).to_have_text("1")

    expect(page.locator(".total")).to_have_text("Total: 40 €")

    # Comprobamos el inventario después de comprar.
    page.goto(url)

    raton = page.locator("article.producto").filter(
        has=page.get_by_role("heading", name="Ratón", exact=True)
    )

    alfombrilla = page.locator("article.producto").filter(
        has=page.get_by_role("heading", name="Alfombrilla", exact=True)
    )

    expect(raton.locator(".stock-count")).to_have_text(
        "Disponibles: 3"
    )

    expect(alfombrilla.locator(".stock-count")).to_have_text(
        "Disponibles: 11"
    )

def test_sesion_cerrada(page: Page, servidor):
    url, _ = servidor

    # Iniciamos sesión.
    page.goto(f"{url}/entrar")
    page.get_by_label("Usuario").fill("alumna")
    page.get_by_label("Contraseña").fill("clave12345")
    page.get_by_role("button", name="Iniciar sesión").click()

    # Accedemos al historial con la sesión iniciada.
    page.goto(f"{url}/pedidos")
    expect(
        page.get_by_role("heading", name="Mis pedidos")
    ).to_be_visible()

    # Cerramos la sesión.
    page.get_by_role("button", name="Salir").click()

    # Intentamos volver al historial.
    page.goto(f"{url}/pedidos")

    # Comprobamos que nos redirige al formulario de acceso.
    expect(page).to_have_url(f"{url}/entrar")

    # Comprobamos que no aparece el historial.
    expect(
        page.get_by_role("heading", name="Mis pedidos")
    ).to_have_count(0)


def test_pedido_de_otro_cliente(page: Page, servidor):
    import sqlite3
    from werkzeug.security import generate_password_hash

    url, db_path = servidor

    # Iniciamos sesión con alumna.
    page.goto(f"{url}/entrar")
    page.get_by_label("Usuario").fill("alumna")
    page.get_by_label("Contraseña").fill("clave12345")
    page.get_by_role("button", name="Iniciar sesión").click()

    # Añadimos un teclado y confirmamos la compra.
    page.request.post(
        f"{url}/carrito/anadir/1",
        form={"cantidad": "1"}
    )
    page.request.post(f"{url}/comprar")

    # Comprobamos que alumna puede acceder a su pedido.
    respuesta = page.goto(f"{url}/pedidos/1")
    assert respuesta.status == 200

    # Cerramos sesión.
    page.get_by_role("button", name="Salir").click()

    # Creamos otro cliente en la base de datos temporal.
    with sqlite3.connect(db_path) as conexion:
        conexion.execute(
            "INSERT INTO usuarios(nombre, hash) VALUES(?, ?)",
            ("cliente2", generate_password_hash("clave12345"))
        )
        conexion.commit()

    # Iniciamos sesión con el segundo cliente.
    page.goto(f"{url}/entrar")
    page.get_by_label("Usuario").fill("cliente2")
    page.get_by_label("Contraseña").fill("clave12345")
    page.get_by_role("button", name="Iniciar sesión").click()

    # Intentamos consultar el pedido de alumna.
    respuesta = page.goto(f"{url}/pedidos/1")

    # Comprobamos que el servidor devuelve HTTP 404.
    assert respuesta.status == 404
    expect(page.get_by_text("Pedido no disponible")).to_be_visible()
