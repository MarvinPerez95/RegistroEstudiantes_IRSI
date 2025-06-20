# config.py
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env.
# Esto es crucial para que os.environ.get() pueda acceder a ellas.
load_dotenv()




class Config:
    # Clave Secreta de Flask: Es fundamental para la seguridad de las sesiones y la firma de datos.
    # Obtiene la clave de las variables de entorno. Si no está definida (ej. en desarrollo),
    # usa un valor por defecto. ¡CAMBIA 'una_clave_secreta_muy_dificil_de_adivinar' por un valor único y complejo en PRODUCCIÓN!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_secreta_muy_dificil_de_adivinar'

    DEBUG = True 
    # Configuración de la Base de Datos SQLAlchemy para SQL Server
    # Obtiene cada componente de la cadena de conexión de las variables de entorno.
    SQLALCHEMY_DATABASE_URI = (
        'mssql+pyodbc:///?odbc_connect='
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f"SERVER={os.environ.get('DB_SERVER') or 'DESKTOP-MIF1BOH'};"
        f"DATABASE={os.environ.get('DB_DATABASE') or 'IRSI_ADMISION'};"
        f"UID={os.environ.get('DB_UID') or 'dbAdmin'};"
        f"PWD={os.environ.get('DB_PWD') or 'dbAdmin'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Recomendado: desactiva el seguimiento de modificaciones de SQLAlchemy para ahorrar recursos.

    # Configuración de Flask-Mail
    # MAIL_SERVER: Servidor SMTP para Gmail (se puede sobrescribir con una variable de entorno si es necesario).
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    # MAIL_PORT: Puerto SMTP, 587 es estándar para TLS (se puede sobrescribir con una variable de entorno).
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    # MAIL_USE_TLS: Habilitar Transport Layer Security (TLS). Por defecto True (se puede sobrescribir con una variable de entorno).
    # Convierte el valor del entorno a booleano de forma segura.
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('true', '1')

    # MAIL_USERNAME: La cuenta de correo que Flask-Mail usará para autenticarse y enviar.
    # Se obtiene directamente de la variable de entorno EMAIL_USER.
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    # MAIL_PASSWORD: La contraseña (o Contraseña de Aplicación) para la cuenta de correo.
    # Se obtiene directamente de la variable de entorno EMAIL_PASS.
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')

    # MAIL_DEFAULT_SENDER: La dirección de correo que aparecerá como remitente por defecto.
    # Obtiene el valor de la variable de entorno MAIL_DEFAULT_SENDER, o usa MAIL_USERNAME si no está definida.
    # Es crucial que esta dirección coincida con MAIL_USERNAME para una autenticación y entrega correctas.
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME

    # Límite de tamaño de contenido (bytes) para las solicitudes HTTP, útil para subidas de archivos.
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 # 2 Megabytes

    # Configuración de Logging: Nombre del archivo donde se guardarán los logs de la aplicación.
    LOG_FILE = 'app.log'