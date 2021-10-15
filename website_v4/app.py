from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from base64 import b64decode
import uuid
import io
from PIL import Image
from pipeline import register, log

app = Flask(__name__)

UPLOAD_FOLDER = 'upload_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    username = db.Column(db.String(200), primary_key=True)
    def __repr__(self):
        return '<User %r>' % self.username

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        
        user = User.query.filter_by(username=username).first()
        if user == None:
            return render_template('index.html', user=username)
        else:
            return render_template('messages.html', message='The user is already registered in the database')

    else:
        return render_template('signup.html')

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user == None:
            return render_template('messages.html', message='User was not found in the database')
        else:
            return render_template('index.html', user=username)

    else:
        return render_template('login.html')

@app.route('/test-image', methods=['POST'])
def checkImage():
    filename = f'{uuid.uuid4().hex}.jpeg'
    message = request.get_json(force=True)
    encoded = message['image']
    decoded = b64decode(encoded)
    image = Image.open(io.BytesIO(decoded)) 

    user = message['username']
    foundUser = User.query.filter_by(username=user).first()
    # if user is not fount, add to the database directory
    print('user: ', foundUser)
    print('filename outer: ', filename)
    if foundUser == None:
        # user came via signup
        reg_res = register(image, user)
        
        new_user = User(username=user)
        try:
            print('got user: ', user)
            db.session.add(new_user)
            db.session.commit()
            #add_data(filename,user)
            print('filename inner: ', filename)
            #os.remove(filename)
            response = { 'prediction': { 'result': reg_res } }
        except:
            response = { 'prediction': { 'result': 'There is already a user with the same name, try something different' } }
            
        return jsonify(response)
    else:
        # user came via login
        log_res = log(image, user)
        if (type(log_res) == str):
            response = { 'prediction': { 'result': log_res } }
        else:
            response = { 'prediction': { 'result': log_res[0] } }
        return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)