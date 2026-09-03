from flask import Flask
from config import Config
from .extensions import db, login_manager, migrate, cors

#The way you repeatedly update the database


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class) #These two lines create the app and register it with Config settings
    print(app.config["SESSION_COOKIE_SAMESITE"]) ; print(app.config["SESSION_COOKIE_SECURE"])
    migrate.init_app(app, db) # These three lines connect the app to the db and login manager
    db.init_app(app)
    cors.init_app(app, supports_credentials=True, origins=["http://localhost:5173"])



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