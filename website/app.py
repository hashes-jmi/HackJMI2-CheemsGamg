import os
from flask import Flask, render_template, url_for, request, redirect
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from PIL import Image
from base64 import b64decode
import uuid


app = Flask(__name__)
UPLOAD_FOLDER = 'upload_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    username = db.Column(db.String(200), primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return '<User %r>' % self.username

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base64 = db.Column(db.String(), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return '<Imagex %r>' % self.id


@app.route('/')
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        new_user = User(username=username)
        try:
            db.session.add(new_user)
            db.session.commit()
            return render_template('index.html')
        except:
            return '<h2>There was an error in adding you as a user. <br>That username you chose maybe already taken, use something else</h2>'

    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        print(user)
        if user == None:
            return redirect('/login')
        else:
            return render_template('index.html')

    else:
        return render_template('login.html')

@app.route('/test-image', methods=['POST'])
def checkImage():
    image = request.form['image']
    imageUrl = Image(base64=image)
    # process the base64 to image
    try:
        filename = f'image-{uuid.uuid4().hex}.png' 
        image = Image.fromstring('RGB',(image.size), b64decode(image))
        image.save(os.path.join(UPLOAD_FOLDER, filename))
        db.session.add(imageUrl)
        db.session.commit()
        # do the backend processing at this place
        return render_template('index.html')
    except:
        return '<h2>There was an error in parsing the image. <br>Please try again</h2>'

if __name__ == '__main__':
    app.run(debug=True)