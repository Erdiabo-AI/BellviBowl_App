'''
Esta sección es la definición del Modelo de Datos en Python. Es el puente que conecta tu base de datos SQL con el código de Flask. Aquí es donde transformamos una tabla de base de datos en una Clase de Python, permitiéndonos manipular usuarios como objetos.
========================
1. Las Importaciones (Las Herramientas)
=====================
'''
from . import db #Importa la instancia de SQLAlchemy que configuramos en el __init__.py. Esto le dice a esta clase: "Tú eres parte de nuestra base de datos".
#Es una herramienta de Flask-Login. Al heredar de ella, nuestra clase Usuario gana automáticamente propiedades necesarias para la sesión, como is_authenticated (saber si el usuario está logueado).
from flask_logi import UserMixin 
#Son las funciones de Werkzeug para la seguridad. Sirven para "hashear" (encriptar de forma irreversible) las contraseñas. Regla de oro: Nunca guardamos la contraseña real, solo su huella digital (hash).
from werkzeug.security import generate_password_hash, check_password_hash
'''
============================================
2. La Clase y sus Atributos (Mapeo SQL)
=======================
defines que esta clase representa a la tabla que creaste en SQL llamada usuarios:

usuario_id: Usamos db.UUID. El server_default=db.text("gen_random_uuid()") es fundamental: le dice a la base de datos que,
si Python no envía un ID, ella misma genere uno automáticamente usando la función nativa de PostgreSQL.

usuario_email: Tiene unique=True. Flask-SQLAlchemy lanzará un error si intentas registrar a dos personas con el mismo correo, protegiendo la integridad de tu liga.

usuario_rol: Con default='user'. Por defecto, todos son entrenadores. Luego tú, desde la base de datos, podrás cambiar el valor a 'admin' o 'comisario'.
'''

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    usuario_id = db.Column(db.UUID, primary_key=True, server_default=db.text("gen_random_uuid()"))
    usuario_nombre = db.Column(db.String(100), nullable=False)
    usuario_naf = db.Column(db.String(100), nullable=False)
    usuario_email = db.Column(db.String(150), unique=True, nullable=False)
    usuario_password_hash = db.Column(db.String(255), nullable=False)
    usuario_rol = db.Column(db.String(20), default='user')
    '''=========================
    3. Métodos de Flask-Login # Flask-Login espera un campo ID, mapeamos el tuyo:
    ==============================
    Flask-Login busca por defecto un campo llamado simplemente id. Como en tu base de datos lo has llamado usuario_id, 
    este método sirve de "traductor". Cuando Flask-Login pregunte "¿Quién es el usuario actual?", esta función le devolverá
    el UUID convertido a texto para que pueda gestionarlo.
    '''
    def get_id(self):
        return str(self.usuario_id)
      '''=========================
      4. La Lógica de Seguridad (Password Handling)
      ====================================================
      set_password(self, password):
        Cuando un usuario se registra, no guardamos "123456". Llamamos a esta función, que convierte "123456" en algo como pbkdf2:sha256:250000$tY8.... 
        Eso es lo que se guarda en la columna usuario_password_hash.

        check_password(self, password):
        Cuando el usuario intenta hacer login, esta función toma la contraseña que escribió en el formulario, la encripta con el mismo algoritmo
        y la compara con el hash guardado. Si coinciden, le deja pasar.
      '''
    def set_password(self, password):
        self.usuario_password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.usuario_password_hash, password)