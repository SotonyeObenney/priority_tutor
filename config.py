import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"
    SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URI") or "sqlite:///priority_tutor.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False