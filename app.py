from flask import Flask, render_template, request, redirect, url_for, flash, url_for, session
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
def load_user(user_id):
    user = User.get(user_id)
    if user:
        return user
    admin_user = adminUser.get(user_id)
    if admin_user:
        return admin_user
    
    return None


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        usertype = request.form.get('usertype')
        if usertype == 'normal':
            return redirect (url_for('login'))
        elif usertype == 'admin':
            return redirect (url_for('admin_login'))
    return render_template('home.html')


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


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return render_template('admin_menu.html')
    
    adminLogin = LoginForm()
    print(admin_login)
    if adminLogin.validate_on_submit():
        usernameForm = adminLogin.username.data
        passwordForm = adminLogin.password.data
        print(usernameForm) #delete

        with myDB() as db:
            userTuple = db.search_user('admin', usernameForm)
            print(userTuple) #delete
            if userTuple:
                user_id = userTuple[0][0]
                username_db = userTuple[0][1]
                fornavn_db = userTuple[0][2]
                etternavn_db = userTuple[0][3]
                password_db = userTuple[0][4]
                print(username_db) #delete
        
                if check_password_hash(password_db, passwordForm):
                    admin_user = adminUser(user_id, username_db, fornavn_db, etternavn_db, password_db)
                    login_user(admin_user) #setter blant annet authenticated = True
                   
                    print(admin_user.username, admin_user.authenticated)
                    print('You have been logged in! Your username is:{}'.format(username_db))
                    return redirect(url_for('admin_menu'))

                else:
                    flash('Wrong password, please try again!')

            else:
                flash('Username not found, please try again.')

    return render_template('admin_login.html', form=adminLogin)


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


@app.route('/admin_menu', methods=['GET', 'POST'])
@login_required
def admin_menu():

    return render_template('admin_menu.html')



@app.route('/create_quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if request.method == 'POST':
        quiz_name = request.form['form_quiz_name']
        category = request.form['form_quiz_category']
        admin_id = current_user.user_id

        print(quiz_name, category, admin_id)
        with myDB() as db:
            db.insert_quiz(quiz_name, category, admin_id)
            return redirect(url_for('create_question', quiz_name=quiz_name))


    return render_template('create_quiz.html')



@app.route('/create_quiz/<quiz_name>', methods=['GET', 'POST'])
@login_required
def create_question(quiz_name):
    if request.method == 'POST':
        questionText = request.form['form_question']
        answerType = request.form['answer_type']

        #håndterer innsetting av essay-type spørsmål
        if answerType == 'essay':
            with myDB() as db:
                quizID = db.getQuizIDbyName(quiz_name)
                if quizID:
                    db.insert_question(questionText, answerType, quizID)
                    flash('Question has been added!')
                else:
                    flash('Something went wrong, please try again!')

        #håndterer innsetting av Multiple Choice-type spørsmål    
        elif answerType == 'multiple_choice':
            with myDB() as db:
                answer1 = request.form['choice_1']
                answer2 = request.form['choice_2']
                answer3 = request.form['choice_3']
                answer4 = request.form['choice_4']
                correct = request.form['correct_choice']
                

                questionID = db.getQuestionIDbyText(questionText)
                if questionID:
                    db.insert_multiple_choice_answers(answer1, answer2, answer3, answer4, correct, questionID)
                    flash('Question has been added!')
                else:
                    flash('Something went wrong, please try again!')
                
                    
                


            

    


    return render_template('create_question.html', quiz_name=quiz_name)















@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()

    return redirect(url_for('home'))




if __name__ == "__main__":
    app.run(debug=True)