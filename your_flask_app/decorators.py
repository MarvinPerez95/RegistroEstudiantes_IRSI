# decorators.py

from functools import wraps
from flask import flash, redirect, url_for, abort # Importar abort para 403
from flask_login import current_user

# Decorador @role_required para restricción de roles
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                # Flask-Login ya maneja la redirección a login_view ('auth.login') si no está autenticado
                # Esta línea es para asegurar que no se proceda si por alguna razón Flask-Login no redirige
                flash('Necesitas iniciar sesión para acceder a esta página.', 'warning')
                return redirect(url_for('auth.login')) # Redirigir al endpoint de login en el blueprint auth
            
            # Asegurarse de que allowed_roles sea una lista
            if isinstance(allowed_roles, str):
                roles_list = [allowed_roles]
            else:
                roles_list = allowed_roles

            if current_user.role not in roles_list:
                flash('No tienes permiso para acceder a esta página.', 'danger')
                return abort(403) # Usar abort(403) para Forbidden en lugar de redirigir a index
                                  # Esto es mejor práctica para errores de permiso.
            return f(*args, **kwargs)
        return decorated_function
    return decorator