from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from ..models import Usuario
from .. import db, login_manager

auth_bp = Blueprint('auth', __name__)

# Necesario para que Flask-Login encuentre al usuario en la DB
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(user_id)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        nombre = request.form.get('nombre')
        password = request.form.get('password')
        naf = request.form.get('naf')

        # Comprobar si el usuario ya existe
        user = Usuario.query.filter_by(usuario_email=email).first()
        if user:
            flash('El correo electrónico ya está registrado.')
            return redirect(url_for('auth.register'))

        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            usuario_email=email, 
            usuario_nombre=nombre, 
            usuario_naf=naf
        )
        nuevo_usuario.set_password(password) # Encriptamos la clave

        db.session.add(nuevo_usuario)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = Usuario.query.filter_by(usuario_email=email).first()

        if not user or not user.check_password(password):
            flash('Por favor, comprueba tus credenciales.')
            return redirect(url_for('auth.login'))

        login_user(user)
        return redirect(url_for('gestor.dashboard')) # Al entrar, va al Gestor

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))