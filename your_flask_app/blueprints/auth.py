# your_flask_app/blueprints/auth.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from datetime import datetime, timedelta
import random
import bleach

from ..forms import LoginForm, TwoFactorForm, RegistrationForm
from ..models import User
from ..extensions import db, mail # Necesario para la DB y enviar correos

# Crea una instancia de Blueprint.
auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth') # Apunta a la subcarpeta de templates

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # Redirige al index del blueprint 'main'
    form = RegistrationForm()
    if form.validate_on_submit():
        username = bleach.clean(form.username.data)
        password = form.password.data
        user = User(username=username, role='user')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('¡Felicidades, te has registrado exitosamente!', 'success')
        # app.logger.info(f'Nuevo usuario registrado: {username}') # Acceder al logger global
        return redirect(url_for('auth.login')) # Redirige al login del blueprint 'auth'
    return render_template('register.html', title='Registro', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # Redirige al index del blueprint 'main'
    form = LoginForm()
    if form.validate_on_submit():
        username = bleach.clean(form.username.data)
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(form.password.data):
            flash('Usuario o contraseña inválidos', 'danger')
            # app.logger.warning(f'Intento de login fallido para: {username}')
            return redirect(url_for('auth.login')) # Redirige al login del blueprint 'auth'

        # Generar y enviar código 2FA
        two_factor_code = str(random.randint(100000, 999999))
        user.two_factor_code = two_factor_code
        user.two_factor_expiry = datetime.utcnow() + timedelta(minutes=5)
        db.session.commit()

        # Importar current_app para acceder a la configuración de MAIL_DEFAULT_SENDER
        from flask import current_app
        msg = Message('Código de Autenticación de Dos Factores',
                      sender=current_app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[user.username])
        msg.body = f"Tu código de autenticación de dos factores es: {two_factor_code}\n\nEste código es válido por 5 minutos."

        try:
            mail.send(msg)
            flash('Se ha enviado un código 2FA a tu correo electrónico.', 'info')
            session['awaiting_2fa_user_id'] = user.id
            return redirect(url_for('auth.two_factor_auth')) # Redirige a 2FA del blueprint 'auth'
        except Exception as e:
            flash(f'Error al enviar el código 2FA: {e}', 'danger')
            # current_app.logger.error(f'Error al enviar 2FA a {user.username}: {e}')
            return redirect(url_for('auth.login'))

    return render_template('login.html', title='Iniciar Sesión', form=form)

@auth_bp.route('/two_factor_auth', methods=['GET', 'POST'])
def two_factor_auth():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user_id = session.get('awaiting_2fa_user_id')
    if not user_id:
        flash('Acceso denegado. Por favor, inicia sesión de nuevo.', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('auth.login'))

    form = TwoFactorForm()
    if form.validate_on_submit():
        entered_code = bleach.clean(form.code.data)
        if user.two_factor_code == entered_code and datetime.utcnow() < user.two_factor_expiry:
            login_user(user, remember=False)
            user.two_factor_code = None
            user.two_factor_expiry = None
            db.session.commit()
            session.pop('awaiting_2fa_user_id', None)
            flash('Autenticación exitosa.', 'success')
            # current_app.logger.info(f'Login exitoso para: {user.username}')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Código 2FA inválido o expirado.', 'danger')
            # current_app.logger.warning(f'Código 2FA inválido/expirado para: {user.username}')
            return redirect(url_for('auth.two_factor_auth'))

    return render_template('2fa.html', title='Autenticación de Dos Factores', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    # current_app.logger.info(f'Usuario {current_user.username} ha cerrado sesión.')
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('main.index')) # Redirige al index del blueprint 'main'