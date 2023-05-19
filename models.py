from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
import mysql.connector





class User(FlaskForm):
    
    username = StringField('username', validators=[DataRequired()], render_kw={"placeholder": "Enter username", "class": "textinput"})
    password = PasswordField('password' , validators=[DataRequired()], render_kw={"placeholder": "Password", "class": "textinput"})


class adminUser(FlaskForm):
    username = StringField('username', validators=[DataRequired()], render_kw={"placeholder": "Enter username", "class": "textinput"})
    fornavn = StringField('fornavn', validators=[DataRequired()], render_kw={"placeholder": "Fornavn", "class": "textinput"})
    etternavn = StringField('etternavn', validators=[DataRequired()], render_kw={"placeholder": "Etternavn", "class": "textinput"})
    password = PasswordField('password' , validators=[DataRequired()], render_kw={"placeholder": "Password", "class": "textinput"})



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
    
    def search_username(self, table, username):
        sql = f'SELECT username, password FROM {table} WHERE username = %s'
        result = self.query(sql, username)
        return result






    

        
