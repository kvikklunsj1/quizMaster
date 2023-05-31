from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
import mysql.connector
from flask_login import LoginManager, UserMixin
import traceback

login_manager = LoginManager()


class User(UserMixin):
    
    def __init__(self, user_id, username, password):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.authenticated = True 

    def get_id(self):
        return str(self.user_id)

    @staticmethod
    def get(username):
        with myDB() as db:
            userTuple = db.getUserByID('user', username) #ser om username finnes i user
            if userTuple:
                user_id = userTuple[0][0]
                username_db = userTuple[0][1]
                password = userTuple[0][2]
                return User(user_id, username_db, password)
            return None


    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
class adminUser(User):
    def __init__(self, user_id, username, password, fornavn, etternavn):
        super().__init__(user_id, username, password)
        self.fornavn = fornavn
        self.etternavn = etternavn


    @staticmethod
    def get(admin_id):
        with myDB() as db:
            adminUserTuple = db.getAdminByID('admin', admin_id) #ser om username finnes i user
            if adminUserTuple:
                admin_id = adminUserTuple[0][0]
                username = adminUserTuple[0][1]
                fornavn = adminUserTuple[0][2]
                etternavn = adminUserTuple[0][3]
                password = adminUserTuple[0][4]
                return adminUser(admin_id, username, fornavn, etternavn, password)
            return None

#Modifisert version av klassen som ble brukt i forelsening: MyDb.py
class myDB:
    def __init__(self) -> None:
        dbconfig = { 'host': '127.0.0.1',
                    'user': 'user',
                    'password': 'userpwd',
                    'database': 'myDB', }
        self.configuration = dbconfig


    def __enter__(self) -> 'cursor':
        self.conn = mysql.connector.connect(**self.configuration)
        self.cursor = self.conn.cursor()
        return self
    
    
    def __exit__(self, exc_type, exc_val, exc_trace) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def query(self, sql, *args):
        self.cursor.execute(sql, args)
        result = self.cursor.fetchall()
        return result
    
    def search_user(self, table, usernameForm): #brukes i login
        sql = f'SELECT * FROM {table} WHERE username = %s'
        userTuple = self.query(sql, usernameForm)
        return userTuple
    
    def getUserByID(self, table, user_id): #brukes av login-manager
        sql = f'SELECT * FROM {table} WHERE user_id = %s'
        userTuple = self.query(sql, user_id)
        return userTuple
    
    def getAdminByID(self, table, admin_id): #brukes av login-manager
        sql = f'SELECT * FROM {table} WHERE admin_id = %s'
        userTuple = self.query(sql, admin_id)
        return userTuple
    
    def insert_user(self, username, password_hash):
        sql = f'INSERT INTO user (username, password) VALUES (%s, %s)'
        args = (username, password_hash)
        try:
            self.query(sql, *args) #blir behandlet som en tuple, så den kan håndtere flere parametere
            return True
        except Exception:
            return False
        
    def insert_admin(self, adminUsername, adminFornavn, adminEtternavn, adminPassword_hash):
        sql = f'INSERT INTO admin (username, fornavn, etternavn, password) VALUES (%s, %s, %s, %s)'
        args = (adminUsername, adminFornavn, adminEtternavn, adminPassword_hash)
        try:
            self.query(sql, *args)
            return True
        except Exception as e:
            print(f"Error inserting admin: {e}") #delete
            traceback.print_exc() #delete
            return False


    def insert_quiz(self, quiz_name, category, admin_id):
        sql = f'INSERT INTO quiz (quiz_name, category, admin_id) VALUES (%s, %s, %s)'
        args = (quiz_name, category, admin_id)
        try:
            self.query(sql, *args) #blir behandlet som en tuple, så den kan håndtere flere parametere
            return True
        except Exception:
            return False
        
    def insert_question(self, questionText, answerType, admin_id):
        sql = f'INSERT INTO question (question_text, answer_type, quiz_id) VALUES (%s, %s, %s)'
        args = (questionText, answerType, admin_id)
        try:
            self.query(sql, *args) #blir behandlet som en tuple, så den kan håndtere flere parametere
            return True
        except Exception:
            return False
        
    
    def getQuizIDbyName(self, quiz_name):
        sql = f'SELECT quiz_id FROM quiz WHERE quiz_name=%s'
        args = (quiz_name,)
        try:
            result = self.query(sql, *args)
            return result[0][0] #returnerer int istedenfor tuple
        except Exception:
            return None
    
    def getQuestionIDbyText(self, questionText):
        sql = f'SELECT question_id FROM question WHERE question_text=%s'
        args = (questionText,)
        try:
            result = self.query(sql, *args)
            return result[0][0] #returnerer int istedenfor tuple
        except Exception as e:
            print('Error:', e)
            return None


    def insert_multiple_choice_answers(self, answer1, answer2, answer3, answer4, correct, questionID):
        sql = f'INSERT INTO answer (answer_1, answer_2, answer_3, answer_4, correct_answer, question_id) VALUES (%s, %s, %s, %s, %s, %s)'
        args = (answer1, answer2, answer3, answer4, correct, questionID)
        try:
            self.query(sql, *args) #blir behandlet som en tuple, så den kan håndtere flere parametere
            return True
        except Exception:
            return False
        

    def displayQuestionsFromQuiz(self, quizID):
        sql = f'SELECT q.question_id, q.question_text, q.answer_type, a.answer_1, a.answer_2, a.answer_3, a.answer_4, a.correct_answer FROM question q LEFT JOIN answer a ON q.question_id = a.question_id WHERE q.quiz_id=%s'
        args = (quizID,)
        try:
            results = self.query(sql, *args)
            return results
        except Exception as e:
            print("An error occurred:", str(e))
            return None
            
    def update_multiple_choice_answers(self, answer1, answer2, answer3, answer4, correct, questionID):
        sql = f'UPDATE answer SET answer_1 = %s, answer_2 = %s, answer_3 = %s, answer_4 = %s, correct_answer = %s WHERE question_id = %s'
        args = (answer1, answer2, answer3, answer4, correct, questionID)
        try:
            self.query(sql, *args) #blir behandlet som en tuple, så den kan håndtere flere parametere
            return True
        except Exception:
            return False
        

    def update_question(self, questionText, answerType, question_id):
        sql = f'UPDATE question SET question_text=%s, answer_type=%s WHERE question_id=%s'
        args = (questionText, answerType, question_id)
        try:
            self.query(sql, *args) #blir behandlet som en tuple, så den kan håndtere flere parametere
            return True
        except Exception:
            return False
        
    def delete_question(self, question_id):
        sql = f'DELETE FROM question WHERE question_id=%s'
        args = (question_id,)
        try:
            self.query(sql, *args) #blir behandlet som en tuple, så den kan håndtere flere parametere
            return True
        except Exception:
            return False
    
    def get_all_quizzez(self):
        sql = f'SELECT quiz_id, quiz_name, category FROM quiz'
        try:
            return self.query(sql)
        except Exception:
            return False



class adminLoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()], render_kw={"placeholder": "Enter username", "class": "textinput"})
    fornavn = StringField('fornavn', validators=[DataRequired()], render_kw={"placeholder": "Fornavn", "class": "textinput"})
    etternavn = StringField('etternavn', validators=[DataRequired()], render_kw={"placeholder": "Etternavn", "class": "textinput"})
    password = PasswordField('password' , validators=[DataRequired()], render_kw={"placeholder": "Password", "class": "textinput"})
        
class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()], render_kw={"placeholder": "Enter username", "class": "textinput"})
    password = PasswordField('password' , validators=[DataRequired()], render_kw={"placeholder": "Password", "class": "textinput"})

