from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
import mysql.connector
from flask_login import LoginManager, UserMixin


login_manager = LoginManager()


class User(UserMixin):
    
    def __init__(self, user_id, username, password):
        self.user_id = user_id
        self.username = username
        self.password = password

    def get_id(self):
        return str(self.user_id)

    @staticmethod
    def get(user):
        with myDB() as db:
            userTuple = db.search_user('user', user) #ser om username finnes i user
            if userTuple:
                user_id = userTuple[0][0]
                username = userTuple[0][1]
                password = userTuple[0][2]
                return User(user_id, username, password)
            return None


    def is_authenticated(self):
        return self.is_authenticated

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
    def get(adminUser):
        with myDB as db:
            adminUserTuple = db.search_user('admin', adminUser) #ser om username finnes i user
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
    
    def search_user(self, table, usernameForm):
            sql = f'SELECT * FROM {table} WHERE username = %s'
            userTuple = self.query(sql, usernameForm)
            return userTuple
    


class adminLoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()], render_kw={"placeholder": "Enter username", "class": "textinput"})
    fornavn = StringField('fornavn', validators=[DataRequired()], render_kw={"placeholder": "Fornavn", "class": "textinput"})
    etternavn = StringField('etternavn', validators=[DataRequired()], render_kw={"placeholder": "Etternavn", "class": "textinput"})
    password = PasswordField('password' , validators=[DataRequired()], render_kw={"placeholder": "Password", "class": "textinput"})


        
class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()], render_kw={"placeholder": "Enter username", "class": "textinput"})
    password = PasswordField('password' , validators=[DataRequired()], render_kw={"placeholder": "Password", "class": "textinput"})


        