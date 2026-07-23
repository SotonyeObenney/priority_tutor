from flask import Flask
from config import Config
from .extensions import db, login_manager, migrate

#The way you repeatedly update the database


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    migrate.init_app(app, db)
    db.init_app(app)
    login_manager.init_app(app)
    from .users import users as users_blueprint
    from .auth import auth as auth_blueprint
    from .videos import videos as videos_blueprint
    from .tutors import tutors as tutors_blueprint
    from .admin import admin as admin_blueprint
    from .main import main as main_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(videos_blueprint, url_prefix='/videos')
    app.register_blueprint(tutors_blueprint, url_prefix='/tutors')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(main_blueprint)
    app.register_blueprint(users_blueprint, url_prefix='/users')

    return app