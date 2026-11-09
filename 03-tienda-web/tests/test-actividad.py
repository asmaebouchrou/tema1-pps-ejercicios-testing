import pytest
from decimal import Decimal
from tienda import total, Producto, comprar

def test_total_con_cupon_ahorra10():
    resultado = total(20, "AHORRA10")

    assert resultado == Decimal("22.95")

def test_compra_stock_insuficiente():
    # Creamos un producto con 2 unidades disponibles.
    producto = Producto(
        id=1,
        nombre="Teclado",
        precio=Decimal("20.00"),
        stock=2
    )

    # Intentamos comprar 3 unidades.
    with pytest.raises(ValueError):
        comprar(producto, 3)

    # Comprobamos que el stock no ha cambiado.
    assert producto.stock == 2
