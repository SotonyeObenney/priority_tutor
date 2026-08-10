import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI") or "sqlite:///priority_tutor.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PAYSTACK_API_TEST_PKEY = os.environ.get("PAYSTACK_API_TEST_PKEY")
    PAYSTACK_API_TEST_SKEY = os.environ.get("PAYSTACK_API_TEST_SKEY")
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'app/static/avatars')
    WTF_CSRF_ENABLED = False


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key"    