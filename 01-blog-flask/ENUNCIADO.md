# Ejercicio 10. Seguridad y comportamiento de un blog (E2E)

Escribe **nueve tests** con Playwright en `tests/test_actividad.py`. Cada test debe tener un nombre descriptivo. La fixture `servidor` proporciona `(url, ruta_sqlite)` y arranca una instancia local con base de datos nueva para cada test; no necesitas arrancar Flask manualmente para estas pruebas.

1. **Contraseña incorrecta:** entra en `/entrar` con `usuario_que_no_existe` y `clave_incorrecta`. Debe aparecer «Usuario o contraseña incorrectos.»
2. **Nombre demasiado corto:** intenta registrar el usuario `ab`, contraseña `claveSegura123`, mediante `page.request.post()` (el navegador bloquea formularios demasiado cortos). Debe responder `400`.
3. **Contraseña demasiado corta:** registra `alumno` con `123` mediante petición HTTP. Debe responder `400`.
4. **Usuario duplicado:** registra `alumno123` con `claveSegura123` y repite el registro. La segunda petición debe responder `409`.
5. **Página protegida:** sin iniciar sesión, visita `/posts`. Debe responder `401` y no mostrar el formulario «Nueva publicación».
6. **Publicación sin autorización:** sin iniciar sesión, envía `POST /posts` con título `No autorizado` y contenido `Sin sesión`. Debe responder `401`; el texto no debe aparecer en la portada.
7. **HTML de usuario:** registra un usuario, inicia sesión y publica el texto literal `<script>window.marcaPrueba=1</script>`. El texto debe verse como contenido y el navegador **no** debe ejecutar el script (`window.marcaPrueba` debe seguir sin existir).
8. **Publicación ajena:** registra dos usuarios. El primero publica «Original del autor». Con la sesión del segundo, intenta `POST /posts/1/editar` para cambiar el título a «Alterado». Debe responder `403` y conservar el título original.
9. **Cerrar sesión:** tras iniciar sesión, pulsa «Salir» e intenta entrar en `/posts`. Debe responder `401`.

**Entrega:** `tests/test_actividad.py`, resultado de `python -m pytest -v` y una explicación de dos o tres líneas sobre qué protege cada prueba de seguridad. Utiliza solo `127.0.0.1` y cuentas ficticias.
