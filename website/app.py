import os
from flask import Flask, render_template, url_for, request, redirect, jsonify
# from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
from base64 import b64decode
import uuid
import io
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from torchvision import datasets
from torch.utils.data import DataLoader
 
import numpy as np
import cv2
# import matplotlib.pyplot as plt
import os


app = Flask(__name__)

UPLOAD_FOLDER = 'upload_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# detector code (Haider Zama) start
face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def check_no_of_faces(f_path):
    img = cv2.imread(f_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    faces = face_detector.detectMultiScale(img, 1.1, 6)
    return len(faces)


def add_to_database(f_path, u_name):
    print(f_path)
    fname = os.path.basename(f_path) 
    print(fname)
    if check_no_of_faces(f_path) == 0:
        print("No faces found!")
        return
    if check_no_of_faces(f_path) > 1:
        print("More than 1 faces found!")
        return
    directory = os.path.join('database',u_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    new_path = os.path.join(directory,fname)
    print(new_path)
    os.replace(f_path, new_path)



mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) #initializing mtcnn for face detection
resnet = InceptionResnetV1(pretrained='vggface2').eval() #initializing resnet for face img to embeding conversion


def face_match(img_path, data_path): # img_path= location of photo, data_path= location of data.pt 
    # getting embedding matrix of the given img
    img = Image.open(img_path)
    face, prob = mtcnn(img, return_prob=True) # returns cropped face and probability
    emb = resnet(face.unsqueeze(0)).detach() # detech is to make required gradient false
    
    saved_data = torch.load('data.pt') # loading data.pt file
    embedding_list = saved_data[0] # getting embedding data
    name_list = saved_data[1] # getting list of names
    dist_list = [] # list of matched distances, minimum distance is used to identify the person
    
    for idx, emb_db in enumerate(embedding_list):
        dist = torch.dist(emb, emb_db).item()
        dist_list.append(dist)
        
    idx_min = dist_list.index(min(dist_list))
    return (name_list[idx_min], min(dist_list))


# detector code (Haider Zama) end


class User(db.Model):
    username = db.Column(db.String(200), primary_key=True)
    def __repr__(self):
        return '<User %r>' % self.username

@app.route('/')
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        
        user = User.query.filter_by(username=username).first()
        if user == None:
            return render_template('index.html', user=username)
        else:
            return '<h1>The user is already registered in the database</h1>'

    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user == None:
            return '<h1>The user not found in the database</h1>'
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
    # image.show()

    user = message['username']
    foundUser = User.query.filter_by(username=user).first()
    # if user is not fount, add to the database directory
    print('user: ', foundUser)
    print('filename outer: ', filename)
    if foundUser == None:
        # user came via signup
        image.save(filename)
        new_user = User(username=user)
        try:
            print('got user: ', user)
            db.session.add(new_user)
            db.session.commit()
            add_to_database(filename, user)
            print('filename inner: ', filename)
        except:
            return '<h2>There was an error in adding you as a user. <br>That username you chose maybe already taken, use something else</h2>'

        # add_to_database(filename, user)
    # else save to the images_for_auth directory 
    else:
        # user came via login
        dataset=datasets.ImageFolder('database') # photos folder path 
        idx_to_class = {i:c for c,i in dataset.class_to_idx.items()} # accessing names of peoples from folder names

        def collate_fn(x):
            return x[0]

        loader = DataLoader(dataset, collate_fn=collate_fn)

        face_list = [] # list of cropped faces from photos folder
        name_list = [] # list of names corrospoing to cropped photos
        embedding_list = [] # list of embeding matrix after conversion from cropped faces to embedding matrix using resnet

        for img, idx in loader:
            face, prob = mtcnn(img, return_prob=True) 
            if face is not None and prob>0.90: # if face detected and porbability >         90%
                emb = resnet(face.unsqueeze(0)) # passing cropped face into resnet      model to get embedding matrix
                embedding_list.append(emb.detach()) # resulten embedding matrix is stored in a list
                name_list.append(idx_to_class[idx]) # names are stored in a list


        image.save('./images_for_auth/img.jpeg')
        data = [embedding_list, name_list]
        torch.save(data, 'data.pt') # saving data.pt file
        result = face_match('./images_for_auth/img.jpeg', 'data.pt')
        print(result)
        response = {
            'prediction': {
                'result': result[0] if result[1]<0.86 else 'No Match',
            }
        }
        return jsonify(response)




if __name__ == '__main__':
    app.run(debug=True)