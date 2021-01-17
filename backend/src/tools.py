import os
import urllib
import urllib.request
import random
import string
import base64
import shutil
import re
from mimetypes import guess_extension, guess_type
import tempfile

class Helper:
    @staticmethod
    def get_base64_image_by_urls(image_urls):
        images_result = {}
        for image_url in image_urls:
            images_result[image_url] = Helper.get_base64_image_by_url(image_url)
        return images_result

    @staticmethod
    def get_base64_image_by_url(image_url):
        #NamedTemporaryFile  has not been used because of a problem with access rights.
        temp_file = os.path.join(os.getcwd(), Helper.generate_name() + "/" + Helper.generate_name())
        os.makedirs(os.path.dirname(temp_file), exist_ok=True)
        urllib.request.urlretrieve(image_url, temp_file)
        with open(temp_file, 'rb') as read_file:
                image_string = base64.b64encode(read_file.read())
        shutil.rmtree(os.path.dirname(temp_file))
        return image_string.decode("utf-8")

    @staticmethod
    def get_fixed_base64_images_by_dict(base64_images):
        images_to_predict = {}
        for img_key, img_data in base64_images.items():
            images_to_predict[img_key] = Helper.get_fixed_base64_image(image_string)
        return images_to_predict

    @staticmethod
    def decode_base64(data, altchars=b'+/'):
        """Decode base64, padding being optional.

        :param data: Base64 data as an ASCII byte string
        :returns: The decoded byte string.

        """
        data = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', data)  # normalize
        missing_padding = len(data) % 4
        if missing_padding:
            data += b'='* (4 - missing_padding)
        return base64.b64decode(data, altchars)

    @staticmethod
    def get_fixed_base64_image(img_data):
        ext = guess_extension(guess_type(img_data)[0])
        with tempfile.TemporaryDirectory() as dir:
            local_full_path_file = os.path.join(dir, "{0}{1}".format(Helper.generate_name(), ext))
            print("local_full_path_file : ", local_full_path_file)
            exts = ["jpeg", "jpg", "png", "gif", "tiff"]
            
            with open(local_full_path_file, 'wb') as f:
                content = img_data.split(',')[1]
                encoded_content= content.encode()
                decoded = Helper.decode_base64(encoded_content)
                f.write(decoded)
            
            with open(local_full_path_file, 'rb') as read_file:
                image_string = base64.b64encode(read_file.read())
        image_string = image_string.decode("utf-8")
        return image_string

    @staticmethod
    def generate(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
    
    @staticmethod
    def generate_name(size=6, chars=string.ascii_uppercase):
        return ''.join(random.choice(chars) for _ in range(size))
    
