from flask import render_template, redirect, url_for, flash, request, abort, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Post
from app.forms import RegisterForm, LoginForm, PostForm

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("index.html", posts=posts)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()

    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()

        if existing_user:
            flash("Пользователь с таким именем или email уже существует", "danger")
            return redirect(url_for("main.register"))

        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(
                form.password.data,
                method="pbkdf2:sha256"
            ),
        )

        db.session.add(user)
        db.session.commit()

        flash("Регистрация прошла успешно. Теперь войдите в систему.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Вы успешно вошли в систему", "success")

            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)

            return redirect(url_for("main.index"))

        flash("Неверный email или пароль", "danger")

    return render_template("login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "info")
    return redirect(url_for("main.index"))


@bp.route("/posts/create", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(
            body=form.body.data,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()

        flash("Пост успешно создан", "success")
        return redirect(url_for("main.index"))

    return render_template("create_post.html", form=form)


@bp.route("/posts/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        abort(403)

    form = PostForm()

    if form.validate_on_submit():
        post.body = form.body.data
        db.session.commit()

        flash("Пост обновлен", "success")
        return redirect(url_for("main.index"))

    if request.method == "GET":
        form.body.data = post.body

    return render_template("edit_post.html", form=form, post=post)


@bp.route("/posts/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()

    flash("Пост удален", "info")
    return redirect(url_for("main.index"))


@bp.route("/profile/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    return render_template("profile.html", user=user, posts=posts)