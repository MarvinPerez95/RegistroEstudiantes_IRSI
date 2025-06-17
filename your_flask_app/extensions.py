from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail


db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()



# Configuración opcional para Flask-Login
login_manager.login_view = 'auth.login' # <-- IMPORTANTE: Nombre del endpoint de login en el Blueprint 'auth'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'

# Función para cargar el usuario (requerida por Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    from .models import User # Importa el modelo User aquí para evitar importaciones circulares
    return User.query.get(int(user_id))