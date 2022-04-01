from flask import Blueprint, render_template, request,flash,redirect,url_for
import re
from website import views
from website import dashboard
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

regex = re.compile(r".*[A-Z].*\d.*\w")


auth = Blueprint('auth', __name__)

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                flash('Logged in successfully!', category='success')
                login_user(user,remember=True)
                return redirect(url_for('dashboard.dash'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out Successfully',category='success')
    return redirect('login')
    
@auth.route('/sign-up' , methods = ['GET', 'POST'])
def sign_up():
    
    if request.method == 'POST':
        
        email = request.form.get("email")
        password = request.form.get("password")
        api = request.form.get("api")
        secret = request.form.get("secret")
        
        mo = re.search(regex,password)
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash("Email already exists.",category='error')
        elif mo == None:
            flash("Weak Password! Enter a password with atleast one Capital Letter and one number", category='error')
        elif len(api) < 64:
            flash("Enter a valid API key!", category='error')
        elif len(secret) < 64:
            flash("Enter valid secret key!", category='error')
        else:
            new_user = User(email=email, password=generate_password_hash(password,method = 'SHA256'),apiK=api,secK=secret)
            db.session.add(new_user)
            db.session.commit()
            login_user(user,remember=True)
            flash("User successfully registered.", category='success')
            return render_template("login.html")

    return render_template("signup.html")