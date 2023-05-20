from flask import Flask, render_template, request, redirect, url_for, flash, url_for
from flask_wtf.csrf import CSRFProtect
import os
from models import User, adminUser, myDB, LoginForm, adminLoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, current_user, logout_user




app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
csrf = CSRFProtect(app)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    user = User.get(user_id)
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

    print(loginForm)

    if loginForm.validate_on_submit():
        usernameForm = loginForm.username.data
        passwordForm = loginForm.password.data
        print(usernameForm)

        with myDB() as db:
            sql = 'SELECT * FROM user WHERE username = %s'
            args = (usernameForm)
            userTuple = db.query(sql, *args)
            print(userTuple)
            if userTuple:
                user_id = userTuple[0][0]
                username_db = userTuple[0][1]
                password_db = userTuple[0][2]
                print(username_db)
        
                if check_password_hash(password_db, passwordForm):
                    login_user(User(user_id, username_db, password_db))
                    print('You have been logged in! Your username is:{}'.format(username_db))

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


#delvis ferdig
@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    #TODO implementer sjekk av username, skal være unikt. Implementer både username some unique i database, og sjekk i koden.


    register_user = User()
    if register_user.validate_on_submit():
        username = register_user.username.data
        password_hash = generate_password_hash(register_user.password.data, method='scrypt')

        with myDB() as db:
            sql = 'INSERT INTO user (username, password) VALUES (%s, %s)'
            args = (username, password_hash)
            db.query(sql, *args) #blir behandlet som en tuple, så den kan håndtere flere parametere
            flash('You have been registered, click here to return to the login-page!')
    

    return render_template('register_user.html', register_user=register_user, csrf_token=register_user.csrf_token)


#delvis ferdig
@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    #TODO implementer sjekk av username, skal være unikt. Implementer både username some unique i database, og sjekk i koden.

    register_admin = adminUser()
    if register_admin.validate_on_submit():
        adminUsername = register_admin.username.data
        adminFornavn = register_admin.fornavn.data
        adminEtternavn = register_admin.etternavn.data
        adminPassword_hash = generate_password_hash(register_admin.password.data, method='scrypt')

        with myDB() as db:
            sql = 'INSERT INTO admin (username, fornavn, etternavn, password) VALUES (%s, %s, %s, %s)'
            args = (adminUsername, adminFornavn, adminEtternavn, adminPassword_hash)
            db.query(sql, *args)
            flash('You have been registered, click here to return to admin login-page!')

    

    
    return render_template('register_admin.html', register_admin=register_admin)










if __name__ == "__main__":
    app.run(debug=True)