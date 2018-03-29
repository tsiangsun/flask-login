from flask import Flask, redirect, render_template, url_for, request, flash
import requests
import numpy as np
import pandas as pd
import datetime
import logging
import sys
import os
from flask_login import LoginManager, UserMixin, login_required, logout_user, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap 
from markupsafe import escape

from scripts import config
from scripts import forms
    
app = Flask(__name__)
app.config.from_object(config.Config)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
app.vars={}

db = SQLAlchemy()
db.init_app(app)
bootstrap = Bootstrap()
bootstrap.init_app(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = u"Please login to access this page."



#========================================================================================
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    password_hash = db.Column(db.String(64))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def register(username, password):
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
    @staticmethod
    def update(username, password):
        u = User.query.filter_by(username=username).first()
        u.set_password(password)
        db.session.commit()

    def __repr__(self):
        return '<User {0}>'.format(self.username)


@lm.user_loader
def load_user(id):
    return User.query.get(id) #User.query.get(int(id)) User.query.get(id)

    
#========================================================================================
@app.route('/')
def main():
      return redirect('/index')      
      
#========================================================================================
@app.route('/index', methods=['GET'])
@login_required
def index():
    return render_template('index.html')
    
#========================================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        #flash('Hello, {}. You have successfully logged in.'
        #      .format(escape(form.username.data)))
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            return redirect(url_for('login', **request.args))
        login_user(user, form.remember_me.data)
        print('User {} successfully logged in.'.format(user.username))
        flash('Hi {}, you have successfully logged in.'.format(user.username))
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html', form=form)


#========================================================================================    
@app.route('/public')
def public():
    return render_template('public.html')
    
    
#========================================================================================
@app.route('/protected')
@login_required
def protected():
    return render_template('protected.html', curr_user = current_user)
     
    
#========================================================================================    
@app.route('/logout')
@login_required
def logout():
    print('User {} has logged out.'.format(current_user.username))
    logout_user()
    return render_template('logout.html') 

    
#========================================================================================
@app.route('/error', methods=['GET'])
def error():
    return render_template('error.html')


# ========================================================================================
@app.route('/case', methods=['GET', 'POST'])
@login_required
def case():
    if request.method == 'POST':
        if request.form['caseid'] == '' or not request.form['caseid'].isnumeric():
            return redirect('/error')
        #print(type(request.form['caseid'])) # <class 'str'>
        app.vars['caseid'] = int(request.form['caseid'])

        caseid = app.vars['caseid']
        print('Received request for case ID {0}'.format(caseid))
        return render_template('case.html', caseid=caseid)
    else:
        return redirect('/error')



#========================================================================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if User.query.filter_by(username='john').first() is None:
            User.register('john', 'cat')
        if User.query.filter_by(username='mark').first() is None:
            User.register('mark', 'def')
        else:
            User.update('mark', 'dudu')

    app.debug = True
    app.run(host='0.0.0.0', port=5000)

