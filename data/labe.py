import os
import json

img = os.listdir('images')
dict = {}
for im in img:
    dict[im] = 0


with open("train.json", "w") as f:
    json.dump(dict, f, indent=2)
