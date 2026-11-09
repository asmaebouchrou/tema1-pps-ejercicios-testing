import pytest
from cuenta import Cuenta


def test_retirar_30_euros():
    # Creamos una cuenta con 100 euros.
    cuenta = Cuenta(100)

    # Retiramos 30 euros.
    cuenta.retirar(30)

    # Comprobamos que el saldo sea 70 euros.
    assert cuenta.saldo == 70

def test_retirar_saldo_insuficiente():
    # Creamos una cuenta con 100 euros.
    cuenta = Cuenta(100)

    # Intentamos retirar 150 euros.
    with pytest.raises(ValueError):
        cuenta.retirar(150)

    # Comprobamos que el saldo no ha cambiado.
    assert cuenta.saldo == 100
