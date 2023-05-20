from flask import Flask, render_template, request, redirect, url_for, flash, url_for
from flask_wtf.csrf import CSRFProtect
import os
from models import User, adminUser, myDB, LoginForm, adminLoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
csrf = CSRFProtect(app)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(username):
    user = User.get(username)
    return user


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        usertype = request.form.get('usertype')
        if usertype == 'normal':
            return redirect (url_for('login'))
        elif usertype == 'admin':
            return redirect (url_for('admin_login'))
    return render_template('home.html')


#todo
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_template('user_menu.html')
    
    loginForm = LoginForm()
    print(loginForm) #delete

    if loginForm.validate_on_submit():
        usernameForm = loginForm.username.data
        passwordForm = loginForm.password.data
        print(usernameForm) #delete

        with myDB() as db:
            userTuple = db.search_user('user', usernameForm)
            print(userTuple) #delete
            if userTuple:
                user_id = userTuple[0][0]
                username_db = userTuple[0][1]
                password_db = userTuple[0][2]
                print(username_db) #delete
        
                if check_password_hash(password_db, passwordForm):
                    user = User(user_id, username_db, password_db)
                    login_user(user) #setter blant annet authenticated = True
                    print(user.username, user.authenticated)
                    print('You have been logged in! Your username is:{}'.format(username_db))
                    return redirect(url_for('user_menu'))

                else:
                    flash('Wrong password, please try again!')

            else:
                flash('Username not found, please try again.')
            
    return render_template('login.html', form=loginForm)

#todo
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    admin_login = adminUser()
    
     #verify user

    return render_template('admin_login.html', login=admin_login)


@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    register_user = LoginForm() #samme form som til login
    if register_user.validate_on_submit():
        username = register_user.username.data
        password_hash = generate_password_hash(register_user.password.data, method='scrypt')

        with myDB() as db:
            is_registred = db.insert_user(username, password_hash) #returnerer bool
            if is_registred:
                 flash('You have been registered, click here to return to the login-page!')
            else:
                flash('Something went wrong, please try again!')

    return render_template('register_user.html', register_user=register_user, csrf_token=register_user.csrf_token)


@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    register_admin = adminLoginForm()
    if register_admin.validate_on_submit():
        adminUsername = register_admin.username.data
        adminFornavn = register_admin.fornavn.data
        adminEtternavn = register_admin.etternavn.data
        adminPassword_hash = generate_password_hash(register_admin.password.data, method='scrypt')

        with myDB() as db:
            is_registred = db.insert_admin(adminUsername, adminFornavn, adminEtternavn, adminPassword_hash) #returnerer bool
            if is_registred:
                flash('You have been registered, click here to return to the admin login-page!')
            else:
                flash('Something went wrong, please try again!')

    return render_template('register_admin.html', register_admin=register_admin, csrf_token=register_admin.csrf_token)



@app.route('/user_menu', methods=['GET', 'POST'])
@login_required
def user_menu():
    return render_template('user_menu.html')







if __name__ == "__main__":
    app.run(debug=True)