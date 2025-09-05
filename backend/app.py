import sys
import json

# if sys.prefix == sys.base_prefix:
#     print("NOT IN VIRTUAL ENV")
#     sys.exit()

from flask import Flask, request, make_response, jsonify, Response
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
# os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/")
def hello_world():
    return '<p>hi there! It works!</p>'

@app.route("/return-img", methods=['POST'])
@cross_origin()
def return_img():
    if 'image_file' not in request.files:
        print("no image_file attribute in request body")
        return "No file part in the request", 400

    file = request.files['image_file']

    if file.filename == '':
        return "No selected file", 400

    if file:
        # Read the image data from the in-memory file
        image_data = file.read()
        
        # Get the MIME type (e.g., 'image/jpeg', 'image/png')
        mimetype = file.mimetype
        
        # Return the raw image data with the correct MIME type
        return Response(image_data, mimetype=mimetype)
    # if 'image_file' not in request.files:
    #     print("no image_file attribute in request body")
    #     return 'No file part', 400
    
    # file = request.files['image_file']

    # if file.filename == '':
    #     return 'No selected file', 400
    # if file:
    #     print('recieved file successfully')
    #     file.seek(0)

    #     try:
    #         # Send the file. You can specify mimetype and attachment_filename if needed.
    #         print("sending now!")
    #         return send_file(file, mimetype='image/jpeg')
    #     except FileNotFoundError:
    #         abort(404, description="Image not found")
        
    # return 'Something went wrong', 500

@app.route("/generate-meme", methods=['POST'])
@cross_origin()
def generate_meme():
    print("enter method")
    if 'image_file' not in request.files:
        print("no image_file attribute in request body")
        return 'No file part', 400
    
    file = request.files['image_file']

    if file.filename == '':
        return 'No selected file', 400
    if file:
        print('recieved file successfully')

        # generate caption here
        mycaption = model.generate_caption(file=file)

        my_response = make_response(jsonify({"caption": mycaption}), 200)

        return my_response
    
    return 'Something went wrong', 500