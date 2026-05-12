from flask import Flask
from config import Config
from .extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from .auth import auth as auth_blueprint
    from .videos import videos as videos_blueprint
    from .tutors import tutors as tutors_blueprint
    from .admin import admin as admin_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(videos_blueprint, url_prefix='/videos')
    app.register_blueprint(tutors_blueprint, url_prefix='/tutors')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app