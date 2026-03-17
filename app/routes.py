from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import RegisterForm, LoginForm
from werkzeug.security import generate_password_hash
from app import create_app
from app.models import Post
from app.forms import PostForm

app = create_app()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegisterForm()

    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()

        if existing_user:
            flash("Пользователь с таким именем или email уже существует", "danger")
            return redirect(url_for("register"))

        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data, method="pbkdf2:sha256"),
        )

        db.session.add(user)
        db.session.commit()

        flash("Регистрация прошла успешно. Теперь войдите в систему.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Вы успешно вошли в систему", "success")

            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)

            return redirect(url_for("index"))

        flash("Неверный email или пароль", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "info")
    return redirect(url_for("index"))