from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import os

app = Flask(__name__)
CORS(app)

model = tf.keras.models.load_model("mushroom_classifier.h5")

class_names = [
    "bad mash",
    "buds",
    "good",
    "intermediate",
    "mature",
    "medium",
    "no mushroom detected"
]

display_names = {
    "bad mash": "Bad Mushroom Detected",
    "buds": "Bud Mushroom Detected",
    "good": "Good Mushroom Detected",
    "intermediate": "Intermediate Mushroom Detected",
    "mature": "Mature Mushroom Detected",
    "medium": "Medium Mushroom Detected",
    "no mushroom detected": "No Mushroom Detected"
}

@app.route('/predict', methods=['POST'])
def predict():

    if 'file' not in request.files:
        return jsonify({
            "error": "No file uploaded"
        })

    file = request.files['file']

    filepath = "temp.jpg"
    file.save(filepath)

    img = image.load_img(filepath, target_size=(224, 224))

    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    prediction = model.predict(img_array)

    predicted_index = np.argmax(prediction)

    confidence = float(np.max(prediction) * 100)

    if confidence < 60:
        final_prediction = "Uncertain Detection"
    else:
        raw_prediction = class_names[predicted_index]
        final_prediction = display_names[raw_prediction]

    os.remove(filepath)

    return jsonify({
        "prediction": final_prediction,
        "confidence": f"{confidence:.2f}%"
    })

if __name__ == '__main__':
    app.run(debug=True)