import sys
import json

# if sys.prefix == sys.base_prefix:
#     print("NOT IN VIRTUAL ENV")
#     sys.exit()

from flask import Flask, request, make_response, jsonify
from flask_cors import CORS, cross_origin
import os
from modules.caption_model import CaptionGenerator

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes


# startup code (load the model in)
model = CaptionGenerator(
    tok_path="tokenizer.json",
    weights_path="caption_model/caption_model_weights_60k.pth",
)

UPLOAD_DIR = "images/uploaded/"

@app.route("/")
def hello_world():
    return '<p>hi there! It works!</p>'

# @app.route("/upload-img", methods=['OPTIONS'])
# def preflight_response():
#     my_response = make_response("", 200)
#     my_response.headers['Access-Control-Allow-Origin'] = '*'

#     return my_response

@app.route("/upload-img", methods=['POST'])
@cross_origin()
def upload_image():
    print("upload recieved")
    if 'image_file' not in request.files:
        return 'No file part', 400
    
    file = request.files['image_file']

    if file.filename == '':
        return 'No selected file', 400
    if file:
        full_path = os.path.join(UPLOAD_DIR, file.filename)

        file.save(full_path)
        print('success')

        my_response = make_response(jsonify({"filename": file.filename}), 200)
        # my_response.headers['Access-Control-Allow-Origin'] = '*'


        print(my_response.headers)

        return my_response
    
    return 'Something went wrong', 500


@app.route("/cap-generate") 
# TODO figure out how to pass the image into this request
def generate_cap():
    img_path = request.args.get('src')
    
    # check if img_path is a valid image that was uploaded
    if (not os.path.exists(os.path.join(UPLOAD_DIR, img_path))):
        return "image path invalid", 404

    # generate caption here
    mycaption = model.generate_caption(img_path=os.path.join(UPLOAD_DIR, img_path))

    # delete the image after a caption has been generated from it
    os.remove(os.path.join(UPLOAD_DIR, img_path))

    my_response = make_response(jsonify({"caption": mycaption}), 200)

    return my_response