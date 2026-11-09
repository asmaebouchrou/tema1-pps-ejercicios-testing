"""Dominio reutilizable por tests unitarios y por la tienda Flask de integracion/E2E."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def dinero(valor):
    """Normaliza euros a dos decimales sin errores de coma flotante."""
    return Decimal(str(valor)).quantize(CENT, rounding=ROUND_HALF_UP)


def total(subtotal, cupon=None):
    """Devuelve importe total con descuento y transporte, segun RN-C02/C03."""
    base = dinero(subtotal)
    if base < 0:
        raise ValueError("Subtotal negativo")
    if cupon not in (None, "AHORRA10", "SINENVIO"):
        raise ValueError("Cupon desconocido")
    if cupon == "AHORRA10":
        base = dinero(base * Decimal("0.90"))
    # Se calcula el umbral sobre el importe que paga realmente el cliente.
    envio = Decimal("0.00") if cupon == "SINENVIO" or base > Decimal("50.00") else Decimal("4.95")
    return dinero(base + envio)


@dataclass
class Producto:
    id: int
    nombre: str
    precio: Decimal
    stock: int


def comprar(producto, cantidad):
    """Reduce stock si hay unidades suficientes; no permite stock negativo."""
    if type(cantidad) is not int or cantidad <= 0:
        raise ValueError("Cantidad invalida")
    if cantidad > producto.stock:
        raise ValueError("Stock insuficiente")
    producto.stock -= cantidad
    return dinero(producto.precio * cantidad)


def puede_ver_pedido(actor, propietario, admin=False):
    """La informacion privada no debe mostrarse a otros clientes."""
    return actor == propietario or admin
