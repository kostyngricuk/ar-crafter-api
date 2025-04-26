from flask import Flask, request, jsonify
import os

from services import get_encoded_model

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>AR Crafter - Model Generator!</p>"

@app.route('/model/create', methods=['POST'])
def generate():
    data = request.get_json()
    image1 = data.get('image1')
    image2 = data.get('image2')

    encodedModel = get_encoded_model(image1, image2)

    return jsonify(encodedModel)

app.run(host='0.0.0.0', port=5000)
