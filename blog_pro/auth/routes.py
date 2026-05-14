from flask import Blueprint, render_template, flash, redirect , url_for, request
from flask_login import login_user, current_user , logout_user, login_required
from blog_pro import bcrypt, db
from blog_pro.models import User
from .forms import RegistrationForm ,LoginForm

auth_bp = Blueprint("auth",__name__,url_prefix="/auth",template_folder='Templates')



@auth_bp.route("/login", methods=["GET","POST"])
def login() :
    if current_user.is_authenticated :
        flash("You already login in",category="success")
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit() :
        user = User.query.filter_by(email=form.email.data).first()
        if not user or not bcrypt.check_password_hash(user.password,form.password.data) :
            flash("Login unsuccessful, Please cheack username and password")
            return render_template("login.html" ,title="Login" ,form=form)

        login_user(user, remember=form.remember.data)
        flash(f'Login successfuly, Hi {user.username}',category="success")
        next_page = request.args.get("next")
        return redirect(next_page) if next_page else redirect(url_for("main.index"))

    return render_template("login.html" ,title="Login" ,form=form)

@auth_bp.route("/register", methods=["GET","POST"])
def register() :
    if current_user.is_authenticated :
        flash("You already login in",category="success")
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit() :
        hased_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        db.session.add(User(username = form.username.data, email=form.email.data, password=hased_password))
        db.session.commit()
        flash(f'Account created for {form.username.data} !','success')
        
        return redirect(url_for("auth.login"))

    for errors in form.errors.values() :
        for error in errors :
            flash(error,category="Error")

    return render_template("register.html", title="register" ,form=form)

@auth_bp.route("/logout",methods=["GET"])
def logout() :   
    if not current_user.is_authenticated :
        flash("You already logout",category="success")
        return redirect(url_for("main.index"))
    logout_user()

    flash("Logout successfuly",category="")
    return redirect(url_for("main.index"))
