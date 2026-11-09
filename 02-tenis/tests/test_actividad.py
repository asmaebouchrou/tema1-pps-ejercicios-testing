
import pytest
from tenis import Partido


def test_ventaja_jugador_0():
    partido = Partido()

    partido.puntos = [3, 3]

    partido.punto(0)

    assert partido.marcador_juego() == "ventaja 0"


def test_jugador_invalido():
    partido = Partido()

    with pytest.raises(ValueError):
        partido.punto(2)

