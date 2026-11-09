# Ejercicio 11. Compra, sesiones y seguridad en Tienda Aula (E2E)

Escribe **diez tests** con Playwright en `tests/test_actividad.py`. La fixture `servidor` arranca la tienda en `127.0.0.1` con una base SQLite temporal e independiente para cada test. Datos de acceso: `alumna` / `clave12345`. Cada prueba debe comenzar con sus propios datos iniciales.

1. **Inicio de sesión rechazado:** usuario `alumna` y contraseña `incorrecta` deben mostrar «Credenciales incorrectas».
2. **Compra sin sesión:** enviar `POST /comprar` sin iniciar sesión debe redirigir a `/entrar` (`302`).
3. **Historial protegido:** visitar `/pedidos` sin sesión debe redirigir a `/entrar`.
4. **Cantidad cero:** intentar añadir 0 teclados mediante `page.request.post()` no debe añadir productos al carrito.
5. **Cantidad superior al stock:** intentar añadir 9 teclados (solo hay 8) debe mostrar «No hay suficiente stock» y dejar vacío el carrito.
6. **Carrito vacío:** con sesión iniciada, intentar confirmar un carrito vacío debe mostrar «Carrito vacío» y no crear pedidos.
7. **Stock después de comprar:** compra 2 teclados, comprueba que la línea del pedido indica 2 unidades y que el catálogo baja de 8 a **6**.
8. **Compra de dos artículos:** compra 2 ratones y 1 alfombrilla. El total debe ser **40 €**; el stock final debe ser 3 ratones y 11 alfombrillas.
9. **Cierre de sesión:** al pulsar «Salir», intentar consultar `/pedidos` debe redirigir al inicio de sesión.
10. **Pedido de otro cliente:** el usuario `alumna` compra un ratón. Prepara una segunda cuenta ficticia en la SQLite temporal (puedes hacerlo desde la fixture o con `sqlite3`). Al entrar con esa segunda cuenta e intentar visitar `/pedidos/1`, debe responder `404`.

**Detección y reparación:** los tests **7 y 8** deben comprobar la cantidad real de existencias, no solo el mensaje de confirmación. Ejecuta primero las pruebas contra el código entregado, observa cuáles fallan, localiza la causa en `app.py`, corrígela y repite las pruebas. Los tests de protección deben pasar también después de la corrección.

**Entrega:** `tests/test_actividad.py`, `app.py` corregido, salida de pytest antes y después, y una frase sobre el riesgo de permitir el acceso a pedidos de otros usuarios. Trabaja exclusivamente en `127.0.0.1`.
