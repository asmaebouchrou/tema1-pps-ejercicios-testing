
from app import create_app


def test_pedido_inexistente(tmp_path):
    # Creamos la aplicación con una base de datos temporal.
    app = create_app(tmp_path / "pedidos.db")

    # Creamos un cliente de pruebas de Flask.
    cliente = app.test_client()

    # Consultamos un pedido que no existe.
    respuesta = cliente.get("/pedidos/9999")

    # Comprobamos que devuelve HTTP 404.
    assert respuesta.status_code == 404
