# your_flask_app/app.py

import os
from flask import Flask, render_template, redirect, url_for, flash, request, session, abort
import logging
from logging.handlers import RotatingFileHandler



from dotenv import load_dotenv
load_dotenv()

from .extensions import db, login_manager, mail # Si eliminaste Flask-Bootstrap5, quita 'bootstrap' de aquí también
from .config import Config

from .blueprints.main import main_bp
from .blueprints.auth import auth_bp
from .blueprints.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    # Si vas a usar Flask-Bootstrap5 y lograste instalar la versión estable, descomenta la siguiente línea:
    # bootstrap.init_app(app) # <--- SOLO SI TENÍAS FLASK-BOOTSTRAP5 Y YA NO ES 0.1.DEV1

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler(f'logs/{app.config["LOG_FILE"]}', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('App startup')

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    # ==============================================================================
    # CAMBIO CRUCIAL AQUÍ: ELIMINA url_prefix PARA main_bp
    # ==============================================================================
    app.register_blueprint(main_bp) # <--- ASÍ DEBE QUEDAR PARA QUE '/' FUNCIONE
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    # ==============================================================================

    from flask_login import current_user
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    # Si usaste la Opción 1 de Bootstrap (CDN), NO INCLUYAS ESTE BLOQUE
    # Si lograste instalar Flask-Bootstrap5 y quieres usarlo, descomenta este bloque:
    # @app.context_processor
    # def inject_bootstrap():
    #     return dict(bootstrap=bootstrap) # <--- SOLO SI TENÍAS FLASK-BOOTSTRAP5 Y YA NO ES 0.1.DEV1


    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        db.session.rollback()
        return render_template('500.html'), 500

    @app.errorhandler(413)
    def too_large(e):
        flash('El archivo es demasiado grande. El tamaño máximo permitido es 2MB.', 'danger')
        return redirect(request.referrer or url_for('main.index')) 
        
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        
        from .models import User
        if not User.query.filter_by(username='admin@example.com').first():
            admin_user = User(username='admin@example.com', role='admin')
            admin_user.set_password('adminpassword')
            db.session.add(admin_user)
            db.session.commit()
            app.logger.info('Usuario administrador por defecto creado.')
    app.run(debug=True)