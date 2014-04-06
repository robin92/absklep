
from flask import Flask, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, current_user


__version__ = "0.1.0"

app = Flask(__name__)
app.db = SQLAlchemy(app)

lorem = 'dummy'
with open('lorem.txt') as file: lorem = file.read()

import absklep.controllers
import absklep.models
import absklep.views
import absklep.forms

absklep.controllers.load_config(app, package=__name__)
absklep.controllers.load_database(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

#some communicates for now
success = "Zostałeś zarejestrowany!"
fail = "Podany email już istnieje."


@app.route("/auth/signup", methods=['GET', 'POST'])
def register():
    from absklep.models import Customer

    form = absklep.forms.Register(request.form)
    if form.validate_on_submit():

        if app.db.session.query(Customer).filter(Customer.email == form.email.data).scalar() is None:
            customer = Customer(str(form.email.data), str(form.pas.data))
            app.db.session.add(customer)
            app.db.session.commit()

            return success

        return render_template('auth/signup.html', form=form, message=fail)
    return render_template('auth/signup.html', form=form, message='')


@app.route("/auth/signin", methods=['GET', 'POST'])
def login():
    from absklep.models import Customer

    form = absklep.forms.Login(request.form)
    if form.validate_on_submit():
        user = app.db.session.query(Customer).filter(Customer.email == form.email.data).first()
        if user is not None:
            if not user.verify_password(form.pas.data):
                return render_template('index.html', form=form, message='haslo nieprawidlowe')
            if login_user(user, remember=form.remember.data):
                return 'Witaj, ' + str(current_user.email)
    return render_template('index.html', form=form, message='')


@login_manager.user_loader
def load_user(uid):
    from absklep.models import Customer

    return Customer.query.get(uid)
