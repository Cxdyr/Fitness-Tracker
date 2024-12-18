from flask import Flask, render_template, redirect, url_for, request, flash
from models import db, bcrypt, User
from config import Config 
from forms import LoginForm, RegisterForm
from calendar_1 import generate_calendar, get_month_name

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)

@app.route('/')
def index():
    calendar_data = generate_calendar()
    return render_template(
        "index.html",
        year=calendar_data["year"],
        month=calendar_data["month"],
        day=calendar_data["day"],
        cal=calendar_data["calendar"],
        calendar_month_name=get_month_name()
    )
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))  
    return render_template('login.html', form=form)  

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            email=form.email.data,
            date_of_birth=form.date_of_birth.data,
            goal=form.goal.data,
            password_hash=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/tracker')
def tracker():
    return render_template('tracker.html')

@app.route('/plan')
def plan():
    return render_template('plan.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)