"""Marcador de tenis sin interfaz; los requisitos estan en REGLAS_NEGOCIO.md."""
class Partido:
    """Partido al mejor de tres sets. Jugadores identificados por 0 y 1."""
    def __init__(self):
        self.puntos = [0, 0]  # Puntos del juego (numeros de tantos, no 15/30/40).
        self.juegos = [0, 0]
        self.sets = [0, 0]
        self.tie_break = False
        self.terminado = False

    def marcador_juego(self):
        """Representacion legible de puntos; los valores internos son tantos."""
        a, b = self.puntos
        if self.tie_break:
            return f"{a}-{b} (tie-break)"
        if a >= 3 and b >= 3:
            if a == b:
                return "iguales"
            return "ventaja 0" if a > b else "ventaja 1"
        nombres = ("0", "15", "30", "40")
        return f"{nombres[min(a,3)]}-{nombres[min(b,3)]}"

    def punto(self, jugador):
        """Anota un tanto y actualiza juego/set/partido cuando corresponda."""
        if jugador not in (0, 1) or type(jugador) is not int:
            raise ValueError("Jugador invalido")
        if self.terminado:
            raise ValueError("Partido finalizado")
        self.puntos[jugador] += 1
        otro = 1 - jugador
        if self.tie_break:
            if self.puntos[jugador] >= 7:
                self._cerrar_set(jugador)
        else:
            # Se requieren cuatro tantos y diferencia de dos.
            if self.puntos[jugador] >= 4 and self.puntos[jugador] - self.puntos[otro] >= 2:
                self._cerrar_juego(jugador)

    def _cerrar_juego(self, jugador):
        self.juegos[jugador] += 1
        self.puntos = [0, 0]
        otro = 1 - jugador
        if self.juegos[jugador] >= 6 and self.juegos[jugador] - self.juegos[otro] >= 1:
            self._cerrar_set(jugador)
        elif self.juegos == [6, 6]:
            self.tie_break = True

    def _cerrar_set(self, jugador):
        self.sets[jugador] += 1
        self.juegos = [0, 0]
        self.puntos = [0, 0]
        self.tie_break = False
        if self.sets[jugador] == 2:
            self.terminado = True
