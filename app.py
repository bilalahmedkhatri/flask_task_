import hashlib
from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, PasswordField, SubmitField

app = Flask(__name__)

# For MySQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/test'

# For SQlite
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'acedasd9123klsjdlasas'
db = SQLAlchemy(app)
pass_bcrypt = Bcrypt(app)


# DateBase table creation with SQLAlchemy
class Staff(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(70), nullable=True)
    dob = db.Column(db.Date)
    password_hint = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(1000), nullable=False)

    def __repr__(self) -> str:
        return self.full_name


# if table create or recreate then this commands will create Tables in DB.
db.create_all()
db.session.commit()


# this is login From with Flask-wtf
class loginForm(FlaskForm):
    fname = StringField('full_name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Login')


# First look of this app or index Page or SignUp Page
@app.route('/', methods=['POST', 'GET'])
def SignUp():
    if request.method == 'POST':
        # getting data from HTML form
        fname = request.form['fname']
        date = request.form['date']
        password = request.form['password']

        # Verifying that if full name is already register in database.
        verify_fname = Staff.query.filter_by(full_name=fname).first()

        # Converting Password to hash code
        pw_hash = pass_bcrypt.generate_password_hash(password)

        # Checking if these requirements are not completed then show these messages.
        if verify_fname:
            flash('Full name is already register Please try something else.')
            return redirect(url_for('SignUp'))
        elif len(password) <= 5:
            flash('Maximum 5 charactor required in Password Field!')
            return redirect(url_for('SignUp'))

        # Assgining values to database fields for saving data.
        staff = Staff(full_name=fname, dob=date,
                      password=pw_hash, password_hint=password[0:3])
        db.session.add(staff)
        db.session.commit()

        # If data is successfully saved in Database than show SUCCESS message to user
        return redirect(url_for('success', name=fname))

    # result = Staff.query.all()
    return render_template('index.html')


# Login Page
@ app.route('/login', methods=['POST', 'GET'])
def Login():

    # getting data from HTML form for Login
    form = loginForm()
    if form.validate_on_submit():

        # when user submit there detail then first check Full Name from DB
        verify_fname = Staff.query.filter_by(full_name=form.fname.data)
        flash('ID or Password may not correct!')

        # if fullname is correct then next check password from fullname table.
        for password in verify_fname:
            # password is hashed so here checking password from DB
            if pass_bcrypt.check_password_hash(password.password, form.password.data):
                return redirect(url_for('Profile'))

            else:
                # if password did not matched then through this error
                flash('Password is not correct!')
                return redirect(url_for('Login'))

    return render_template('login.html', form=form)


# if user successfully created their profile then user will redirect to this page.
@ app.route('/success/<name>')
def success(name):
    name = name.upper()
    return render_template('success_message.html', name=name)


# If user Successfully login then user will redirect on this page
@ app.route('/profile')
def Profile():
    result = Staff.query.all()
    return render_template('profile.html', result=result)


# Its a main function to run this on localhost
if __name__ == '__main__':
    app.run(debug=True, port=8005)
