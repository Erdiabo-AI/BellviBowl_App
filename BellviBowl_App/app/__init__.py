'''
Para que Flask pueda interactuar con tu tabla usuarios y gestionar el acceso (Admin, Comisario, Usuario), necesitamos mapear la tabla en app/models.py
Este archivo (que suele llamarse __init__.py y residir dentro de la carpeta app/) es el punto de ignición de tu aplicación. Utiliza un patrón de diseño llamado Application Factory (Factoría de Aplicación).

En lugar de crear la aplicación de forma global, la encerramos en una función. Esto es vital para proyectos profesionales porque facilita las pruebas y evita "importaciones circulares" (cuando dos archivos se intentan importar entre sí al mismo tiempo).
'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from .routes.auth import auth_bp

'''
===============================
1. La Fase de Instanciación (Fuera de la función)
=======================
Aquí estamos creando los objetos de las extensiones, pero vacíos.
Por qué fuera: Necesitamos que otros archivos (como models.py) puedan importar db para definir las tablas, incluso antes de que la
aplicación Flask esté totalmente configurada. Es como comprar los electrodomésticos antes de tener la cocina instalada
'''
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.register_blueprint(auth_bp)
   
    '''
    ====================================================================
    2. La Configuración y Seguridad
    ===================================================
    SECRET_KEY: Es una cadena de texto aleatoria que Flask usa para firmar las cookies de sesión. Si alguien la roba, podría fingir ser 
    cualquier usuario. Por eso usamos os.environ.get, que intenta leerla de las variables de entorno de Vercel. Si no existe 
    (en tu PC local), usa 'dev_key_bellvibowl'.

    SQLALCHEMY_DATABASE_URI: Es la dirección de tu base de datos. Tiene este formato: postgresql://usuario:password@host:puerto/nombre_db.
    Nunca la escribimos directamente en el código para evitar que alguien vea nuestras contraseñas en GitHub.
    '''
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_bellvibowl')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    '''
    ====================================================================
    3. La Vinculación (El "init_app")
    ===================================================
    Aquí es donde ocurre la magia: le decimos a las extensiones: "Oye, esta es la aplicación de la liga BellviBowl que vas a gestionar".
    login_view: Esta línea es fundamental. Si un usuario intenta entrar al gestor de la liga sin estar logueado, Flask-Login lo interceptará
    y lo enviará automáticamente a la página de login que definamos (en este     caso, una ruta llamada auth.login
    '''
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Redirección si no están logueados
    
    '''
    ====================================================================
    4. El Sistema de Blueprints (Planos)  Registro de Blueprints (Tus 3 partes del proyecto)
    ===================================================
    Los Blueprints son como "carpetas lógicas" para tus rutas. En lugar de tener 50 rutas en un solo archivo, las dividimos:

    main_bp: No tiene prefijo. Sus rutas serán midominio.com/, midominio.com/contacto, etc. (Parte 1).
    gestor_bp: Tiene el prefijo /gestor. Todas sus rutas empezarán por ahí: midominio.com/gestor/crear-equipo, midominio.com/gestor/actas. Esto mantiene el proyecto ordenado.
    '''
    from .routes.main import main_bp
    from .routes.gestor import gestor_bp
    #Básicamente, le estás diciendo a Flask cómo organizar las URLs de las diferentes partes del proyecto para que no se mezclen
    app.register_blueprint(main_bp)
    app.register_blueprint(gestor_bp, url_prefix='/gestor')

    return app