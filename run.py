from app import create_app

app = create_app()
if __name__ == '__main__':
    app.run(debug=True)

with app.app_context():
    from app.extensions import db
    from app import models
    db.create_all()