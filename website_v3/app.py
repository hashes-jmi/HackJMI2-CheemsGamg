import os
from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
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
import os

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


face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
def check_no_of_faces(f_path):
    img = cv2.imread(f_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faces = face_detector.detectMultiScale(img, 1.1, 6)
    return len(faces), faces

def read_image(path):
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def save_crop(img, faces, directory, idx=0, sf=20):
    i=idx
    print(f"index : {i}")
    for (x, y, w, h) in faces:
        img2 = img
        crop = img2[y:y+h, x:x+w]
        crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        cv2.imwrite(os.path.join(directory,'crop'+str(i)+'.jpeg'), crop)
        i+=1
        print(x,y)

def add_data(path,username):
    img = read_image(path)
    directory = os.path.join('database',username)
    if not os.path.exists(directory):
        os.makedirs(directory)
        faces = face_detector.detectMultiScale(img, 1.1, 6)
        print(len(faces))
        if (len(faces) > 1):
            print("More than 1 face found!")
        elif (len(faces) == 0):
            print('No faces found')

        print(faces)
        save_crop(img, faces, directory)

    else:
        faces = face_detector.detectMultiScale(img, 1.1, 6)
        print(len(faces))
        if (len(faces) > 1):
            print("More than 1 face found!")
        elif (len(faces) == 0):
            print('No faces found')
        
        n = len(os.listdir(directory))
        save_crop(img, faces, directory, n)

def add_auth(path, faces):
    img = read_image(path)
    directory = os.path.join("images_for_auth")
    if (len(faces) > 1):
        print("More than 1 face found!")
    elif (len(faces) == 0):
        print('No faces found')

    print(len(faces))
    save_crop(img, faces, directory)


mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) 
resnet = InceptionResnetV1(pretrained='vggface2').eval() 

def face_match(img_path, data_path): 
    img = Image.open(img_path)
    face, prob = mtcnn(img, return_prob=True) 
    emb = resnet(face.unsqueeze(0)).detach() 
    
    saved_data = torch.load('data.pt') 
    embedding_list = saved_data[0] 
    name_list = saved_data[1] 
    dist_list = [] 
    
    for idx, emb_db in enumerate(embedding_list):
        dist = torch.dist(emb, emb_db).item()
        dist_list.append(dist)
        
    idx_min = dist_list.index(min(dist_list))
    return (name_list[idx_min], min(dist_list))


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
        image.save(filename)
        new_user = User(username=user)
        try:
            print('got user: ', user)
            db.session.add(new_user)
            db.session.commit()
            add_data(filename,user)
            print('filename inner: ', filename)
            os.remove(filename)
            response = { 'prediction': { 'result': 'User was successfully registered' } }
        except:
            response = { 'prediction': { 'result': 'There is already a user with the same name, try something different' } }
            
        return jsonify(response)
    else:
        # user came via login
        dataset=datasets.ImageFolder('database')
        idx_to_class = {i:c for c,i in dataset.class_to_idx.items()} 

        def collate_fn(x):
            return x[0]

        loader = DataLoader(dataset, collate_fn=collate_fn)

        face_list = [] 
        name_list = [] 
        embedding_list = [] 

        for img, idx in loader:
            face, prob = mtcnn(img, return_prob=True) 
            if face is not None and prob>0.90: 
                emb = resnet(face.unsqueeze(0)) 
                embedding_list.append(emb.detach()) 
                name_list.append(idx_to_class[idx]) 

        image.save('./images_for_auth/img.jpeg')
        data = [embedding_list, name_list]
        torch.save(data, 'data.pt') 
        n, faces = check_no_of_faces('./images_for_auth/img.jpeg')
        add_auth('./images_for_auth/img.jpeg', faces)
        os.remove('./images_for_auth/img.jpeg')
        if n==0:
            response = { 'prediction': { 'result': 'No Faces found' } }
        elif n>1:
            response = { 'prediction': { 'result': 'More than one faces found' } }
        else:
            result = face_match('./images_for_auth/crop0.jpeg', 'data.pt')
            print(result)
            response = { 'prediction': { 'result': result[0] if result[1]<0.84 else 'No Match found' } }
        return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)