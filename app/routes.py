import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, createLetter, createObjective, UpdateAccountForm
from app.models import User, Objective, Letter
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        print(form.email.data)
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/letter")
@login_required

def letter():
    print(current_user)
    letters = Letter.query.filter_by(user_id=current_user.id)
    return render_template('letter.html', title='letter', letters = letters)


@app.route("/create_letter", methods=['GET', 'POST'])
def create_letter():
    form = createLetter()
    if form.validate_on_submit():
        letter = Letter(subject=form.subject.data, content=form.content.data, author=current_user)
        db.session.add(letter)
        db.session.commit()
        flash('Your letter has been created!', 'success')
        return redirect(url_for('letter'))
    return render_template('create_letter.html', title='New Letter',
                           form=form, legend='New Letter')


@app.route("/objective")
@login_required
def objective():
    objectives = Objective.query.filter_by(user_id=current_user.id)
    return render_template('objective.html', title='objective', objectives = objectives)


@app.route("/create_objective", methods=['GET', 'POST'])
def create_objective():
    form = createObjective()
    if form.validate_on_submit():
        objective = Objective(title=form.title.data,
                              content=form.content.data, author=current_user)
        db.session.add(objective)
        db.session.commit()
        flash('Your objective has been created!', 'success')
        return redirect(url_for('objective'))
    return render_template('create_objective.html', title='New objective',
                           form=form, legend='New Objective')


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn