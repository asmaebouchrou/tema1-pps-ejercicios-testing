
from playwright.sync_api import Page, expect


def test_login_contrasena_incorrecta(page: Page, servidor):
    # Obtenemos la URL del servidor de pruebas.
    url, _ = servidor

    # Abrimos el formulario de inicio de sesión.
    page.goto(f"{url}/entrar")

    # Introducimos unas credenciales incorrectas.
    page.get_by_label("Usuario").fill("usuario_que_no_existe")
    page.get_by_label("Contraseña").fill("clave_incorrecta")

    # Enviamos el formulario.
    page.get_by_role("button", name="Iniciar sesión").click()

    # Comprobamos que aparece el mensaje de error.
    expect(page.get_by_role("alert")).to_have_text(
        "Usuario o contraseña incorrectos."
    )

    # Comprobamos que no hemos accedido a la zona protegida.
    expect(page).to_have_url(f"{url}/entrar")
    assert page.request.get(f"{url}/posts").status == 401



def test_usuario_demasiado_corto(page: Page, servidor):
    url, _ = servidor

    # Intentamos registrar un usuario con solo 2 caracteres.
    respuesta = page.request.post(
        f"{url}/registro",
        form={
            "usuario": "ab",
            "password": "clave_segura123"
        }
    )

    # El servidor debe rechazar el registro.
    assert respuesta.status == 400

    # Intentamos iniciar sesión para comprobar que no se creó la cuenta.
    acceso = page.request.post(
        f"{url}/entrar",
        form={
            "usuario": "ab",
            "password": "clave_segura123"
        }
    )

    assert acceso.status == 401


def test_contrasena_demasiado_corta(page: Page, servidor):
    url, _ = servidor

    respuesta = page.request.post(
        f"{url}/registro",
        form={
            "usuario": "alumno",
            "password": "123"
        }
    )

    assert respuesta.status == 400


def test_usuario_duplicado(page: Page, servidor):
    import sqlite3

    url, db_path = servidor

    datos = {
        "usuario": "alumno123",
        "password": "clave_segura123"
    }

    # Registramos el usuario por primera vez.
    primera = page.request.post(
        f"{url}/registro",
        form=datos,
        max_redirects=0
    )

    assert primera.status == 302

    # Intentamos registrar el mismo usuario otra vez.
    segunda = page.request.post(
        f"{url}/registro",
        form=datos
    )

    assert segunda.status == 409

    # Comprobamos que solo existe una cuenta.
    with sqlite3.connect(db_path) as conexion:
        cantidad = conexion.execute(
            "SELECT COUNT(*) FROM usuarios WHERE nombre = ?",
            ("alumno123",)
        ).fetchone()[0]

    assert cantidad == 1


def test_pagina_protegida_sin_sesion(page: Page, servidor):
    url, _ = servidor

    # Intentamos acceder sin iniciar sesión.
    respuesta = page.goto(f"{url}/posts")

    # Comprobamos que devuelve HTTP 401.
    assert respuesta.status == 401

    # Comprobamos que no aparece el formulario.
    expect(page.get_by_role("button", name="Publicar")).to_have_count(0)
    expect(page.get_by_label("Título")).to_have_count(0)



def test_publicacion_no_autorizada(page: Page, servidor):
    url, _ = servidor

    # Intentamos publicar sin iniciar sesión.
    respuesta = page.request.post(
        f"{url}/posts",
        form={
            "titulo": "No autorizado",
            "cuerpo": "Sin sesión"
        }
    )

    # Comprobamos que el servidor rechaza la petición.
    assert respuesta.status == 401

    # Abrimos la página principal.
    page.goto(url)

    # Comprobamos que la publicación no aparece.
    expect(
        page.get_by_role("heading", name="No autorizado")
    ).to_have_count(0)



def test_html_no_se_ejecuta(page: Page, servidor):
    url, _ = servidor
    texto = "<script>window.marcaPrueba=1</script>"

    # Registramos un usuario válido.
    page.request.post(
        f"{url}/registro",
        form={
            "usuario": "alumno123",
            "password": "clave_segura123"
        }
    )

    # Iniciamos sesión.
    page.goto(f"{url}/entrar")
    page.get_by_label("Usuario").fill("alumno123")
    page.get_by_label("Contraseña").fill("clave_segura123")
    page.get_by_role("button", name="Iniciar sesión").click()

    # Creamos una publicación con etiquetas HTML.
    page.goto(f"{url}/posts")
    page.get_by_label("Título").fill("Prueba XSS")
    page.get_by_label("Contenido").fill(texto)
    page.get_by_role("button", name="Publicar").click()

    # Comprobamos que el texto aparece literalmente.
    expect(page.locator(".texto-post")).to_have_text(texto)

    # Comprobamos que el JavaScript no se ha ejecutado.
    assert page.evaluate("window.marcaPrueba") is None


def test_edicion_publicacion_ajena(page: Page, servidor):
    url, _ = servidor

    # Registramos los dos usuarios.
    for usuario in ("autor123", "otro123"):
        page.request.post(
            f"{url}/registro",
            form={
                "usuario": usuario,
                "password": "clave_segura123"
            }
        )

    # Iniciamos sesión con el primer usuario.
    page.goto(f"{url}/entrar")
    page.get_by_label("Usuario").fill("autor123")
    page.get_by_label("Contraseña").fill("clave_segura123")
    page.get_by_role("button", name="Iniciar sesión").click()

    # Creamos una publicación.
    page.goto(f"{url}/posts")
    page.get_by_label("Título").fill("Original del autor")
    page.get_by_label("Contenido").fill("Contenido original")
    page.get_by_role("button", name="Publicar").click()

    # Cerramos la sesión del primer usuario.
    page.get_by_role("button", name="Salir").click()

    # Iniciamos sesión con el segundo usuario.
    page.goto(f"{url}/entrar")
    page.get_by_label("Usuario").fill("otro123")
    page.get_by_label("Contraseña").fill("clave_segura123")
    page.get_by_role("button", name="Iniciar sesión").click()

    # Intentamos editar la publicación del primer usuario.
    respuesta = page.request.post(
        f"{url}/posts/1/editar",
        form={
            "titulo": "Título modificado",
            "cuerpo": "Contenido cambiado"
        }
    )

    # Comprobamos que se rechaza la modificación.
    assert respuesta.status == 403

    # Comprobamos que el título original sigue apareciendo.
    page.goto(url)
    expect(
        page.get_by_role("heading", name="Original del autor")
    ).to_be_visible()

    expect(
        page.get_by_role("heading", name="Título modificado")
    ).to_have_count(0)



def test_cierre_de_sesion(page: Page, servidor):
    url, _ = servidor

    # Registramos un usuario válido.
    page.request.post(
        f"{url}/registro",
        form={
            "usuario": "alumno123",
            "password": "clave_segura123"
        }
    )

    # Iniciamos sesión.
    page.goto(f"{url}/entrar")
    page.get_by_label("Usuario").fill("alumno123")
    page.get_by_label("Contraseña").fill("clave_segura123")
    page.get_by_role("button", name="Iniciar sesión").click()

    # Comprobamos que podemos acceder a la zona protegida.
    respuesta = page.goto(f"{url}/posts")
    assert respuesta.status == 200

    # Cerramos sesión.
    page.get_by_role("button", name="Salir").click()

    # Intentamos acceder nuevamente a la zona protegida.
    respuesta = page.goto(f"{url}/posts")

    # Comprobamos que se deniega el acceso.
    assert respuesta.status == 401
