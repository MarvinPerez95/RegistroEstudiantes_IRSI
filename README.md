Pronto Principal

Crea una aplicación web en Flask que incluya lo siguiente:
Conexión a una base de datos SQL Server utilizando SQLAlchemy. Usa el driver ODBC
Driver 17 for SQL Server.
Modelo de usuario con los campos: username (email), password_hash, role,
two_factor_code y two_factor_expiry.
Modelo adicional llamado Estudiante con campos personales como nombre, apellidos,
pais, ciudad, direccion, grado, dni, fecha_nacimiento, correo, telefono,
anio_solicitud.
Login de usuarios con validación vía formulario (Flask-WTF), uso de CSRF y control
de sesiones con LoginManager.
Autenticación con segundo factor (2FA) usando código numérico enviado por email.
Configuración para enviar correos electrónicos mediante un servidor SMTP (usa
Flask-Mail).
Uso de sanitización de entradas con bleach para prevenir XSS.
Decorador @role_required para restringir acceso a vistas según el rol del usuario.
Configura también MAX_CONTENT_LENGTH a 2MB y guarda logs en un archivo app.log.

