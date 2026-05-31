from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Load trained model
model = tf.keras.models.load_model("mushroom_classifier.h5")

# IMPORTANT:
# Replace with your actual class order
class_names = [
    "bad_mash",
    "buds",
    "good",
    "intermediate",
    "mature",
    "medium"
]

@app.route('/predict', methods=['POST'])
def predict():

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"})

    file = request.files['file']

    # Save uploaded image temporarily
    filepath = "temp.jpg"
    file.save(filepath)

    # Load image
    img = image.load_img(filepath, target_size=(224,224))

    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    # Predict
    prediction = model.predict(img_array)

    predicted_class = class_names[np.argmax(prediction)]

    confidence = float(np.max(prediction) * 100)

    # Remove temp image
    os.remove(filepath)

    return jsonify({
        "prediction": predicted_class,
        "confidence": f"{confidence:.2f}%"
    })

if __name__ == '__main__':
    app.run(debug=True)