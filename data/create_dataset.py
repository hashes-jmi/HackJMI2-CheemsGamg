import os
import json
import shutil

os.makedirs('train/real')
os.makedirs('train/fake')

with open('train.json') as f:
    data = json.load(f)
    imgs = data.keys()
    for im in imgs:
        if data[im] == 1:
            shutil.move('images/'+im, 'train/real')
        else:
            shutil.move('images/'+im, 'train/fake')