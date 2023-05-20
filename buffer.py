class User(UserMixin):
    
    def __init__(self, username, password):
    username = StringField('username', validators=[DataRequired()], render_kw={"placeholder": "Enter username", "class": "textinput"})
    password = PasswordField('password' , validators=[DataRequired()], render_kw={"placeholder": "Password", "class": "textinput"})

    def is_authenticated(self):
        return self.is_authenticated

    def is_active(self):
        return True
    
    def get_id(self)



class adminUser(FlaskForm):
    username = StringField('username', validators=[DataRequired()], render_kw={"placeholder": "Enter username", "class": "textinput"})
    fornavn = StringField('fornavn', validators=[DataRequired()], render_kw={"placeholder": "Fornavn", "class": "textinput"})
    etternavn = StringField('etternavn', validators=[DataRequired()], render_kw={"placeholder": "Etternavn", "class": "textinput"})
    password = PasswordField('password' , validators=[DataRequired()], render_kw={"placeholder": "Password", "class": "textinput"})


  def search_user(self, table, usernameForm):
        sql = f'SELECT * FROM {table} WHERE username = %s'
        userTuple = self.query(sql, usernameForm)
        return userTuple