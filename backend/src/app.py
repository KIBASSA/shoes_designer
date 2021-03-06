

import os
import sys
sys.path.append(os.path.join(os.getcwd(), "pix2pixs/"))
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
from mimetypes import guess_extension, guess_type
from edge_detector import EdgeTransformer
import tempfile
from torch import nn
#initialization for flask app
app = Flask(__name__)
api = Api(app)  # type: Api

device = 'cpu'
input_dim = 1 # for edge image (1, 256, 256 )
real_dim = 3
image_shape = (512,512)

print("current : ", os.getcwd())
#load model
gen = UNet(input_dim, real_dim).to(device)
loaded_state = torch.load(os.path.join(os.getcwd(), "models/gan_shoes_model/pix2pix_black_briant_high_resolution.pth"))
gen.load_state_dict(loaded_state["gen"])

transforms = transforms.Compose([transforms.ToTensor(),transforms.Resize(image_shape)])
edge_transformer = EdgeTransformer(os.path.join(os.getcwd(), "models/hed_model"))


@app.route("/")
def hello():
    return "Hello, I Shoes Designer API"

@app.route("/test_too_large", methods=['GET'])
def test_too_large():
    #return jsonify(image)
    with open("image1.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('ascii')
    print("encoded_string : ", encoded_string)
    return jsonify("data:image/png;base64," + encoded_string)

@app.route('/generate_images', methods=['GET'])
def generate_images():
    base64Img = request.args.get('image')
    print("GET base64Img :", type(base64Img))
    print("GET base64Img :", base64Img)
    base64Img = base64Img.replace(" ", "+")
    ext = guess_extension(guess_type(base64Img)[0])
    with tempfile.TemporaryDirectory() as folder:
        local_full_path_file = os.path.join(folder, "{0}{1}".format(Helper.generate_name(), ext))
        exts = ["jpeg", "jpg", "png", "gif", "tiff"]
        with open(local_full_path_file, 'wb') as f:
            content = base64Img.split(',')[1]
            encoded_content= content.encode()
            decoded = Helper.decode_base64(encoded_content)
            f.write(decoded)
        _, hed = edge_transformer.transform(local_full_path_file)
        
        filename_hed = os.path.join(folder, "{0}_hed_{1}".format(Helper.generate_name(), ext))
        cv2.imwrite(filename_hed, hed)
        with open(filename_hed, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('ascii')

        hed_to_return = np.invert(hed) #inverse color
        filename_hed_to_return = os.path.join(folder, "{0}_hed_to_return_{1}".format(Helper.generate_name(), ext))
        cv2.imwrite(filename_hed_to_return, hed_to_return)
        with open(filename_hed_to_return, "rb") as image_file:
            hed_to_return_encoded_string = base64.b64encode(image_file.read()).decode('ascii')
            
        hed_image_base64 = "data:image/png;base64," + hed_to_return_encoded_string

        mask = Image.open(filename_hed)
        mask = transforms(mask)
        mask = mask.unsqueeze(0)
        mask = nn.functional.interpolate(mask, size=image_shape)
        mask = mask.to(device)
        with torch.no_grad():
            generated_image = gen(mask)
        generated_image_file = os.path.join(folder, Helper.generate_name() + ".png")
        save_image(generated_image[0], generated_image_file)
        with open(generated_image_file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('ascii')
        generated_image_base64 = "data:image/png;base64," + encoded_string

    return jsonify({"hed":hed_image_base64, "generated":generated_image_base64})

@app.route('/generate_images_post', methods=['POST'])
def generate_images_post():
    if "image" not in request.form:
        return "image must be provided", status.HTTP_400_BAD_REQUEST

    base64Img = request.form['image']
    print("POST base64Img :", type(base64Img))
    print("POST base64Img :", base64Img)
    base64Img = base64Img.replace(" ", "+")
    ext = guess_extension(guess_type(base64Img)[0])
    with tempfile.TemporaryDirectory() as folder:
        local_full_path_file = os.path.join(folder, "{0}{1}".format(Helper.generate_name(), ext))
        exts = ["jpeg", "jpg", "png", "gif", "tiff"]
        with open(local_full_path_file, 'wb') as f:
            content = base64Img.split(',')[1]
            encoded_content= content.encode()
            decoded = Helper.decode_base64(encoded_content)
            f.write(decoded)
        _, hed = edge_transformer.transform(local_full_path_file)
        
        filename_hed = os.path.join(folder, "{0}_hed_{1}".format(Helper.generate_name(), ext))
        cv2.imwrite(filename_hed, hed)
        with open(filename_hed, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('ascii')

        hed_to_return = np.invert(hed) #inverse color
        filename_hed_to_return = os.path.join(folder, "{0}_hed_to_return_{1}".format(Helper.generate_name(), ext))
        cv2.imwrite(filename_hed_to_return, hed_to_return)
        with open(filename_hed_to_return, "rb") as image_file:
            hed_to_return_encoded_string = base64.b64encode(image_file.read()).decode('ascii')
            
        hed_image_base64 = "data:image/png;base64," + hed_to_return_encoded_string

        mask = Image.open(filename_hed)
        mask = transforms(mask)
        mask = mask.unsqueeze(0)
        mask = nn.functional.interpolate(mask, size=image_shape)
        mask = mask.to(device)
        with torch.no_grad():
            generated_image = gen(mask)
        generated_image_file = os.path.join(folder, Helper.generate_name() + ".png")
        save_image(generated_image[0], generated_image_file)
        with open(generated_image_file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('ascii')
        generated_image_base64 = "data:image/png;base64," + encoded_string

    return jsonify({"hed":hed_image_base64, "generated":generated_image_base64})

@app.route('/generate_shoe_by_hed', methods=['GET'])
def generate_shoe_by_hed():
    base64Img = request.args.get('image')
    base64Img = base64Img.replace(" ", "+")
    """"""
    base64Img = Helper.get_fixed_base64_image(base64Img)
    decoded_img = base64.b64decode(base64Img)
    img_buffer = BytesIO(decoded_img)
    imageData = Image.open(img_buffer).convert('LA')
    
    img = ImageOps.fit(imageData, image_shape)
    img_tensor = transforms(img)
    img_tensor = img_tensor.unsqueeze(0)
    print("img_tensor.shape : ", img_tensor.shape)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    cv2.imshow(img)
    cv2.waitKey(0)
    with torch.no_grad():
        generated_image = gen(img_tensor[:,0:1,:,:])
        print("generated_image.shape : ", generated_image.shape)
    save_image(generated_image[0], "image1.png")
    with open("image1.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('ascii')

    return jsonify("data:image/png;base64," + encoded_string)
    
    #return jsonify(base64Img)
    
@app.route('/generate_shoe', methods=['GET'])
def generate_shoe():
    base64Img = request.args.get('image')
    base64Img = base64Img.replace(" ", "+")
    
    base64Img = Helper.get_fixed_base64_image(base64Img)
    decoded_img = base64.b64decode(base64Img)
    img_buffer = BytesIO(decoded_img)
    imageData = Image.open(img_buffer).convert('LA')
    #num_channel = len(imageData.split())
    #print("num_channel:", num_channel)
    img = ImageOps.fit(imageData, image_shape)
    img_tensor = transforms(img)
    img_tensor = img_tensor.unsqueeze(0)
    with torch.no_grad():
        generated_image = gen(img_tensor[:,1:2,:,:])
        print("generated_image.shape : ", generated_image.shape)
    save_image(generated_image[0], "image1.png")
    with open("image1.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('ascii')
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
    