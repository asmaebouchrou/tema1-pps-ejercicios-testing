# Reglas de negocio: Blog Flask E2E: usuarios, publicaciones y seguridad

- **RN-F01:** registro exige nombre valido y contrasena de al menos ocho caracteres.
- **RN-F02:** solo un usuario autenticado puede crear publicaciones.
- **RN-F03:** un usuario no puede modificar ni borrar publicaciones ajenas.
- **RN-F04:** cerrar sesion revoca el acceso a rutas protegidas.
- **RN-F05:** contenido de publicaciones se representa como texto, sin ejecutar HTML aportado por usuarios.

