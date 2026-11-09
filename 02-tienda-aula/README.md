# Tienda Aula: ejercicio E2E

Consulta `ENUNCIADO.md` y `REGLAS_NEGOCIO.md` para conocer los casos que hay que probar.

```bash
python3 -m venv .venv
source .venv/bin/activate
# Con Fish: source .venv/bin/activate.fish
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m pytest -v tests/test_actividad.py
```

Los tests ejecutan un servidor Flask **solo en localhost** y crean una SQLite temporal distinta para cada caso mediante `tests/conftest.py`. No es necesario iniciar `app.py` en otra terminal, ni borrar bases manualmente.

Para ver la ejecución en Chromium, añade `--headed` al comando pytest. La carpeta `tests` incluye solo la fixture de arranque, no las soluciones.

## Tienda y navegación

La portada muestra 14 artículos, tres categorías y un buscador. Puedes consultar fichas individuales, cambiar o eliminar unidades del carrito y leer la ayuda. Todo se ejecuta en local con datos ficticios. Los ejercicios de Playwright se centran en el catálogo, los pedidos, la seguridad y la coherencia del inventario.
