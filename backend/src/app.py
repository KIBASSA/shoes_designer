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
from mimetypes import guess_extension, guess_type
from edge_detector import EdgeTransformer
import tempfile
#initialization for flask app
app = Flask(__name__)
api = Api(app)  # type: Api

device = 'cpu'
input_dim = 1 # for edge image (1, 256, 256 )
real_dim = 3
image_shape = (512,512)

#load model
gen = UNet(input_dim, real_dim).to(device)
loaded_state = torch.load("../notebooks/best_weight/pix2pix_black_briant400.pth")
gen.load_state_dict(loaded_state["gen"])

transforms = transforms.Compose([transforms.ToTensor(),transforms.Resize(image_shape)])
edge_transformer = EdgeTransformer("../models/hed_model")

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

@app.route('/generate_edge', methods=['GET'])
def generate_edge():
    base64Img = request.args.get('image')
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
        cv2.imwrite(os.path.join(folder, filename_hed), hed)
        with open(filename_hed, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('ascii')
    return jsonify("data:image/png;base64," + encoded_string)

    
@app.route('/generate_shoe', methods=['GET'])
def generate_shoe():
    base64Img = request.args.get('image')
    base64Img = base64Img.replace(" ", "+")
    
    base64Img = Helper.get_fixed_base64_image(base64Img)
    decoded_img = base64.b64decode(base64Img)
    img_buffer = BytesIO(decoded_img)
    imageData = Image.open(img_buffer).convert('LA')
    num_channel = len(imageData.split())
    print("num_channel:", num_channel)
    img = ImageOps.fit(imageData, image_shape)
    img_tensor = transforms(img)
    print("img_tensor.shape : ", img_tensor.shape)
    img_tensor = img_tensor.unsqueeze(0)
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
    