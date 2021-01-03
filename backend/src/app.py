import os
import sys
sys.path.append("pix2pixs/")
from classes import UNet, show_tensor_images
from tools import Helper
import torch
from torchvision import transforms
from torchvision.utils import save_image
import base64
import matplotlib.pyplot as plt
import json
from PIL import Image, ImageOps
from io import StringIO
#import Image
from io import BytesIO
from flask import Flask, request, jsonify
from flask_restful import Api
import cv2
import numpy as np
#initialization for flask app
app = Flask(__name__)
api = Api(app)  # type: Api

device = 'cpu'
input_dim = 1 # for edge image (1, 256, 256 )
real_dim = 3

#load model
gen = UNet(input_dim, real_dim).to(device)
loaded_state = torch.load("../notebooks/best_weight/pix2pix_black_briant400.pth")
gen.load_state_dict(loaded_state["gen"])

transforms = transforms.Compose([transforms.ToTensor(),transforms.Resize((256,256))])

"""
@app.route('/generate_shoe', methods=['POST'])
def generate_shoe():
    data = request.data
    print("request.get_json() :", request.get_json())
    print("request : ", request.form)
    encoded_data = data.split(',')[1]
    nparr = np.fromstring(encoded_data.decode('base64'), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imshow(img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

"""

@app.route("/test_too_large", methods=['GET'])
def test_too_large():
    
    #return jsonify(image)
    with open("image1.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('ascii')
    print("encoded_string : ", encoded_string)
    return jsonify("data:image/png;base64," + encoded_string)

@app.route('/generate_shoe', methods=['GET'])
def generate_shoe():
    base64Img = request.args.get('image')
    base64Img = base64Img.replace(" ", "+")
    
    base64Img = Helper.get_fixed_base64_image(base64Img)
    #print("base64Img 2 :", base64Img)
    #base64Img = json.dumps(base64Img)
    decoded_img = base64.b64decode(base64Img)
    img_buffer = BytesIO(decoded_img)
    #imageData = Image.open(img_buffer).convert("RGB")
    imageData = Image.open(img_buffer).convert('LA')
    #imageData.show()
    num_channel = len(imageData.split())
    print("num_channel:", num_channel)
    img = ImageOps.fit(imageData, (256,256))
    img_tensor = transforms(img)
    print("img_tensor.shape : ", img_tensor.shape)
    img_tensor = img_tensor.unsqueeze(0)
    #show_tensor_images(img_tensor[0], size=(1, 256, 256))
    #img_tensor = img_tensor[:,0:1,:,:]
    print("img_tensor[0,0:1,:,:].shape : ", img_tensor[0,0:1,:,:].shape)
    #show_tensor_images(img_tensor[0,0,:,:], size=(1, 256, 256))
    #show_tensor_images(img_tensor[0,1:2,:,:], size=(1, 256, 256))
    #show_tensor_images(img_tensor[0,2,:,:], size=(1, 256, 256))
    print("img_tensor[0,1:2,:,:].shape : ", img_tensor[0,1:2,:,:].shape)
    #img_conv = np.array(img)
    with torch.no_grad():
        generated_image = gen(img_tensor[:,1:2,:,:])
        print("generated_image.shape : ", generated_image.shape)
    #show_tensor_images(generated_image[0], size=(3, 256, 256))
    save_image(generated_image[0], "image1.png")
    with open("image1.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('ascii')
    #print("encoded_string : ", encoded_string)
    return jsonify("data:image/png;base64," + encoded_string)


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    header['Access-Control-Allow-Methods'] = 'OPTIONS, HEAD, GET, POST, DELETE, PUT'
    return response

if __name__ == "__main__":
    app.run()
    