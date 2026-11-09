# Reglas de negocio: pedidos

- El producto no puede estar vacío.
- Las unidades deben ser un entero positivo.
- Un pedido válido se almacena en SQLite y puede consultarse por su ID.
- Una solicitud inválida devuelve HTTP 400 y no modifica la base de datos.
- Un ID inexistente devuelve HTTP 404.
