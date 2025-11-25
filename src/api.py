import io
import sys
import os
import torch
import requests

from model import FusionModel
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from torchvision import models, transforms

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def load_resnet():
    try:
        resnet = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        resnet = torch.nn.Sequential(*list(resnet.children())[:-1])
        resnet.eval()
        print("ResNet loaded successfully")
        return resnet

    except Exception as e:
        print(f"Error loading ResNet: {e}")
        return False

def load_model():
    try:
        # Hard coded - not sensitive and is accessible via http
        url = "https://ams3.digitaloceanspaces.com/s3.retinacare/fusion_model_mvp.pth"
        response = requests.get(url)
        response.raise_for_status()
        state_dict = torch.load(io.BytesIO(response.content), map_location="cpu")
        model = FusionModel().to("cpu")
        model.load_state_dict(state_dict)
        model.eval()
        print("Model loaded successfully")
        return model

    except Exception as e:
        print(f"Error loading model: {e}")
        return False

resnet = load_resnet()
model = load_model()

@app.route('/predict', methods=['POST'])
def predict():
    try:
        image_file = validate_request_image()
        image = Image.open(image_file.stream).convert('RGB')
        image_features = preprocess_image(image)
        clinical_features = validate_request_features()

        if model is False:
            raise Exception("Model failed to load")

        with torch.no_grad():
            output = model(image_features, clinical_features)
            probabilities = torch.softmax(output, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item()

        recommendations = {
            0: "Annual screening recommended. Maintain good glycemic control.",
            1: "Follow-up in 9-12 months. Monitor blood sugar and blood pressure closely.",
            2: "Follow-up in 6-9 months. Consider referral to ophthalmologist.",
            3: "Follow-up in 3-4 months. Urgent ophthalmologist referral recommended.",
            4: "Immediate ophthalmologist referral required. High risk of vision loss."
        }

        return jsonify({
            'success': True,
            'confidence': confidence,
            'risk': map_risk(predicted_class),
            'recommendation': recommendations[predicted_class]
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

# =============================================================
# Helpers
# =============================================================

def validate_request_image():
    if 'image' not in request.files:
        raise Exception("No image file provided")

    file = request.files['image']
    if file.filename == '':
        raise Exception("No file selected")

    if not allowed_file(file.filename):
        raise Exception("File must be a JPEG or JPG image")

    if not validate_image_type(file.stream):
        raise Exception("File is not a valid JPEG image")

    file.stream.seek(0)
    return file

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image_type(file_stream):
    try:
        file_stream.seek(0)
        img = Image.open(file_stream)
        file_stream.seek(0)
        return img.format == 'JPEG'

    except Exception:
        file_stream.seek(0)
        return False

def validate_request_features():
    if 'hba1c' not in request.form:
        raise Exception("Hba1c key is missing")

    if "blood_pressure" not in request.form:
        raise Exception("Blood Pressure key is missing")

    if "duration" not in request.form:
        raise Exception("Duration key is missing")

    clinical_tensor = torch.tensor([[
        float(request.form['hba1c']),
        float(request.form['blood_pressure']),
        float(request.form['duration'])
    ]], dtype=torch.float32)

    return clinical_tensor

def preprocess_image(image):
    if resnet is False:
        raise Exception("ResNet not loaded")

    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    image_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        features = resnet(image_tensor).squeeze()

    return features.unsqueeze(0)

def map_risk(score):
    risk_level = {
        0: "No DR",
        1: "Mild Non-Proliferative Dr",
        2: "Moderate Non-Proliferative Dr",
        3: "Severe Non-Proliferative Dr",
        4: "High Risk Of Progression",
    }
    return score(risk_level)


# =============================================================
# Entry Point
# =============================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
