from app import create_app
import os
cert_path = os.path.join(os.path.dirname(__file__), "localhost+1.pem")
key_path = os.path.join(os.path.dirname(__file__), "localhost+1-key.pem")
print(cert_path)
print(key_path, "keyPath")

app = create_app()
if __name__ == '__main__':
    app.run(debug=True, ssl_context=(cert_path, key_path))
