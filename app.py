from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os

# Setting Up the flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'session_123' # Since we are using session, we must use a secret key. Session will help us in making the secret page inaccessible without signing in
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'my_db_data.db') # Configuring Db
db = SQLAlchemy(app)

# I will be using flash to show messages such as success messages and error messages

# Setting up the user Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


# Welcome Page so that there is no error when we try to access the default address
@app.route('/', methods=['GET', 'POST'])
def welcome():
    return render_template('welcome.html')


# Sign up page.
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if session.get('user_id'):
        flash('Already Signed In. Please Log out First.', 'error')
        return render_template('secretPage.html')

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('signup'))

        # Bonus Part: Prevent Creation of account if the email already exists in db
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already in use. Please use a different email.', 'error')
            return redirect(url_for('signup'))

        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('thankyou'))

    return render_template('signup.html')


# Sign in page
@app.route('/signin', methods=['GET', 'POST'])
def signin():

    if session.get('user_id'):
        flash('Already Signed In. Please Log out First.', 'error')
        return render_template('secretPage.html')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # confirm weather the user is using the correct credentials to sign in or not via db. If the credentials are invalid, we return the error as a flash message
        user = User.query.filter_by(email=email, password=password).first()

        if user:
            session['user_id'] = user.id
            return redirect(url_for('secret_page'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
            return redirect(url_for('signin'))

    return render_template('signin.html')


# Secret Page for when the user successfully logs in
@app.route('/secret_page')
def secret_page():
    if session.get('user_id'):
        return render_template('secretPage.html')
    else:
        flash("Secret Page is only accessible by logged in users", 'error')
        return redirect(url_for('signin'))


# Logout route. this will be used by the html file for the purpose of logging out the user
@app.route('/logout')
def logout():
    session.pop('user_id', '')
    flash("You Have Successfully Logged out!", 'success')
    return render_template('signin.html')


# Thank you page for when the user successfully sign up to our app
@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
