from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "main.login"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User, Post
    from app.routes import bp
    app.register_blueprint(bp)

    from werkzeug.security import generate_password_hash
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(email="test@test.com").first():
            user = User(
                username="test",
                email="test@test.com",
                password_hash=generate_password_hash("123456")
            )
            db.session.add(user)
            db.session.commit()

    return app