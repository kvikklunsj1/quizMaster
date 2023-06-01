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
        password_hash = generate_password_hash(register_user.password.data, method='sha256')

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
        adminPassword_hash = generate_password_hash(register_admin.password.data, method='sha256')

        with myDB() as db:
            is_registred = db.insert_admin(adminUsername, adminFornavn, adminEtternavn, adminPassword_hash) #returnerer bool
            if is_registred:
                flash('You have been registered, click here to return to the admin login-page!')
            else:
                flash('Something went wrong, please try again!')

    return render_template('register_admin.html', register_admin=register_admin, csrf_token=register_admin.csrf_token)


@app.route('/admin_menu', methods=['GET', 'POST'])
@login_required
def admin_menu():
    quiz_tuple = []
    with myDB() as db:
         quiz_tuple= db.get_all_quizzez()
         
    return render_template('admin_menu.html',quiz_tuple=quiz_tuple)



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
    questionText = 0 #nødløsning scope-issue

    if request.method == 'POST':
        #håndterer nytt spm   
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
                quizID = db.getQuizIDbyName(quiz_name)
                if quizID:
                    db.insert_question(questionText, answerType, quizID)
                else:
                    flash('Something went wrong, please try again!')

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




@app.route('/create_quiz/<quiz_name>/edit_questions', methods=['GET', 'POST'])
@login_required
def edit_questions(quiz_name): 
    #henter alle spørsmål tilknyttet valgt quiz
    with myDB() as db:
        quiz_id = db.getQuizIDbyName(quiz_name) # ikke optimal løsning, men siden quiz_name er uniqe så funker det

        if quiz_id:
            questions = db.displayQuestionsFromQuiz(quiz_id)
        else:
            questions = []
            flash('Something went wrong, please try again!')

   

    if request.method == 'POST':
       len_questions = len(questions)
       quizID = None
       with myDB() as db:
           quizID = db.getQuizIDbyName(quiz_name)

       for index in range(len_questions):
    
            question_id = questions[index][0] #uendret verdi
            question_text = request.form[f'question{index+1}_text'] # kan være endret
            answer_type = questions[index][2] # undret verdi
            len_questions = len(questions)
            delete_question = request.form.get(f'delete_question{index+1}', False)
            print(delete_question)
            #håndterer checkbox returnerer on hvis den er checked           
            if delete_question == 'on':
                with myDB() as db:
                    db.delete_question(question_id)


            #håndterer innsetting av essay-type spørsmål
            elif answer_type == 'essay':
                with myDB() as db:
                    db.update_question(question_text, answer_type, question_id)
                   

            #håndterer innsetting av Multiple Choice-type spørsmål    
            elif answer_type == 'multiple_choice':
                with myDB() as db:
                    db.update_question(question_text, answer_type, quizID)

                    answer1 = request.form[f'question{index+1}_answer1']
                    answer2 = request.form[f'question{index+1}_answer2']
                    answer3 = request.form[f'question{index+1}_answer3']
                    answer4 = request.form[f'question{index+1}_answer4']
                    correct = request.form[f'question{index+1}_correct']

                    if question_id:
                        db.update_multiple_choice_answers(answer1, answer2, answer3, answer4, correct, question_id)
                        flash('Question has been updated!')
                    else:
                        flash('Something went wrong, please try again!')


   

    
    return render_template('edit_questions.html', quiz_name=quiz_name, questions=questions) 


@app.route('/user_menu', methods=['GET', 'POST'])
@login_required
def user_menu():
    quiz_tuple = []
    with myDB() as db:
         quiz_tuple= db.get_all_quizzez()
    



    return render_template('user_menu.html', quiz_tuple=quiz_tuple)


@app.route('/run_quiz/<quiz_name>', methods=['GET', 'POST'])
@login_required
def run_quiz(quiz_name):

    #henter alle spørsmål tilknyttet valgt quiz
    quiz_id = None #scope quickfix
    user_id = current_user.user_id
    print('userID i runquiz = ', user_id)

    with myDB() as db:
        quiz_id = db.getQuizIDbyName(quiz_name) # ikke optimal løsning, men siden quiz_name er uniqe så funker det

        if quiz_id:
            questions = db.displayQuestionsFromQuiz(quiz_id)
        else:
            questions = []
            flash('Something went wrong, please try again!')

    if request.method == 'POST':
        len_questions = len(questions)

        for index in range(len_questions):
            question_id = questions[index][0]
            answer_type = questions[index][2]


            if answer_type ==  'multiple_choice':
                user_answer1 = request.form.get(f'ans1{index}', False)
                user_answer1 = True if user_answer1 == 'on' else False #boolifiserer user_answer

                user_answer2 = request.form.get(f'ans2{index}', False)
                user_answer2 = True if user_answer2 == 'on' else False

                user_answer3 = request.form.get(f'ans3{index}', False)
                user_answer3 = True if user_answer3 == 'on' else False

                user_answer4 = request.form.get(f'ans4{index}', False)
                user_answer4 = True if user_answer4 == 'on' else False
                with myDB() as db:
                   db.insert_multi_choice(user_id, question_id, user_answer1, user_answer2, user_answer3, user_answer4)



            elif answer_type == 'essay':
                user_answer = request.form[f'question{index}_essay_ans']
                with myDB() as db:
                    db.insert_essay_ans(question_id, user_id, user_answer)

         #oppdaterer completed_quizzes-table
        with myDB() as db:
            db.complete_quiz(quiz_id, user_id)



    return render_template('run_quiz.html', quiz_name=quiz_name, questions=questions)


@app.route('/administrate_quiz', methods=['GET', 'POST'])
@login_required
def administrate_quiz():

    with myDB() as db:
        completed_quizzes = db.get_completed_quizes()
        print(completed_quizzes)

    

    return render_template('administrate_quizes.html', completed_quizzes=completed_quizzes)




@app.route('/administrate_quiz/<completed_quiz_id>', methods=['GET', 'POST'])
@login_required
def review_quiz(completed_quiz_id):

    print('stemmer id montro?: ', completed_quiz_id)
    with myDB() as db:
        results = db.get_completed_user_quiz(completed_quiz_id)


    if request.method == 'POST':
        comment = request.form['comment']
        status = request.form['status']
        question_id = request.form['question_id']
        with myDB() as db:
            db.update_question_status(status, comment, completed_quiz_id, question_id)


    return render_template('review_quiz.html', results=results)






@app.route('/quiz_results', methods=['GET', 'POST'])
@login_required
def view_quiz_results():
    user_id = current_user.user_id 
    print(user_id)
    
    with myDB() as db:
        completed_quizzes = db.get_completed_quizes_by_ID(user_id)
     
    
    return render_template('view_quiz_results.html', completed_quizzes=completed_quizzes)



@app.route('/quiz_results/<completed_quiz_id>', methods=['GET', 'POST'])
@login_required
def review_one_quiz_results(completed_quiz_id):
    user_id = current_user.user_id 
    
    with myDB() as db:
        completed_quizzes = db.get_completed_user_quiz_by_user_id(completed_quiz_id, user_id)
    
     
        print('testtest', completed_quizzes)
    
    return render_template('review_one_quiz_results.html', completed_quizzes=completed_quizzes)









@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()

    return redirect(url_for('home'))




if __name__ == "__main__":
    app.run(debug=True)