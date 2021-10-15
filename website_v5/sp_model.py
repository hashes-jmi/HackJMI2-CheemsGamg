import cv2
import os
import numpy as np
from PIL import Image
#import matplotlib.pyplot as plt
from keras.models import load_model
#from keras_vggface.vggface import VGGFace
from keras.preprocessing.image import img_to_array, ImageDataGenerator
import matplotlib.pyplot as plt

def process(img):
  return cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb)

def realvfake(fname): # Cropped numpy image as input.
    img = Image.open(fname)
    img = img.resize((224, 224), Image.ANTIALIAS)
    img_arr = np.expand_dims(img_to_array(img), axis=0)

    datagen = ImageDataGenerator(rescale=1./255, preprocessing_function=process)
    for batch in datagen.flow(img_arr, batch_size=1):
        img = batch[0]
        break
    
    #plt.imsave('det_face.png', img)
    os.remove(fname)
    clf = load_model('model/clf.h5')
    pre = clf.predict(np.expand_dims(img, axis=0))
    out = np.argmax(pre)
    if out == 1:
        return False
    elif out == 0:
        return True