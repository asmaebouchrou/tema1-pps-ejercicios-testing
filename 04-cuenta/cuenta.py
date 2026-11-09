class Cuenta:
    def __init__(self, saldo=100):
        self.saldo = saldo

    def ingresar(self, cantidad):
        if cantidad <= 0:
            raise ValueError("Cantidad invalida")
        self.saldo += cantidad

    def retirar(self, cantidad):
        if cantidad <= 0:
            raise ValueError("Cantidad invalida")
        if cantidad > self.saldo:
            raise ValueError("Saldo insuficiente")
        self.saldo -= cantidad
        return self.saldo
