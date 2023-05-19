from flask import Flask, render_template, request, redirect, url_for, flash, url_for
from flask_wtf.csrf import CSRFProtect
import os
from models import User, adminUser, myDB
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
csrf = CSRFProtect(app)





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
    user_login = User()
    if user_login.validate_on_submit():
        username_Form = user_login.username.data
        
        with myDB() as db:
            userTuple = db.search_username('user', username_Form) #ser om username finnes i user
           
            if userTuple:
                username_db = userTuple[0][0]
                password_db = userTuple[0][1]

                if userTuple and check_password_hash(password_db, user_login.password.data):
                    print('You have been logged in! Your username is:', username_db)

                else:
                    flash('Wrong password, please try again!')

            else:
                flash('Username not found, please try again.')
                
        

            
    return render_template('login.html', login=user_login)


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
        password_hash = generate_password_hash(register_user.password.data, method='sha256')

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
        adminPassword_hash = generate_password_hash(register_admin.password.data, method='sha256')

        with myDB() as db:
            sql = 'INSERT INTO admin (username, fornavn, etternavn, password) VALUES (%s, %s, %s, %s)'
            args = (adminUsername, adminFornavn, adminEtternavn, adminPassword_hash)
            db.query(sql, *args)
            flash('You have been registered, click here to return to admin login-page!')

    

    
    return render_template('register_admin.html', register_admin=register_admin)










if __name__ == "__main__":
    app.run(debug=True)