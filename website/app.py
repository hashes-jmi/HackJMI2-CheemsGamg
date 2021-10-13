from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///img.db'
db = SQLAlchemy(app)

class User(db.Model):
    id: db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    date_created: db.Column(db.DateTime, default=datetime.utcnow)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base64 = db.Column(db.String(), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/')
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        new_user = User(content=username)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/testing')
        except:
            return 'There was an error in adding you as a user'

    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        print(user)
        return redirect('/testing')

    else:
        return render_template('login.html')

@app.route('/testing')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)