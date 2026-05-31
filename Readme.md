# Mushroom Classification using CNN & Transfer Learning

A computer vision based mushroom classification system built using TensorFlow and MobileNetV2.

The model classifies mushroom growth and quality stages from uploaded images using a transfer learning pipeline optimized for lightweight inference and edge deployment.

---

## Overview

This project uses a pretrained MobileNetV2 convolutional neural network as a feature extraction backbone combined with a custom classification head for multi-class mushroom image classification.

The system supports:

* Image based mushroom classification
* Web-based prediction interface
* Flask inference API
* Transfer learning workflow
* Edge-device deployment possibility using TensorFlow Lite

---

## Classification Classes

* Buds
* Intermediate
* Mature
* Good
* Medium
* Bad Mash

---

## Architecture

```text id="umq5rb"
Input Image
    ↓
Preprocessing & Augmentation
    ↓
MobileNetV2 Backbone
    ↓
GlobalAveragePooling2D
    ↓
Dense Layer (ReLU)
    ↓
Dropout
    ↓
Softmax Output Layer
```

---

## Tech Stack

* TensorFlow
* Keras
* MobileNetV2
* Flask
* NumPy
* HTML / CSS / JavaScript

---

## Dataset Structure

```bash id="v3h2p9"
mashrooms_dataset/
├── bad_mash/
├── buds/
├── good/
├── intermediate/
├── mature/
└── medium/
```

---

## Training

The model uses:

* Transfer learning
* Image augmentation
* Frozen pretrained backbone
* Multi-class categorical classification

Training is handled through `train.py`.

```bash id="vfjlwm"
python train.py
```

---

## Inference API

The prediction pipeline is served using Flask.

```bash id="pc4b3m"
python classify.py
```

The frontend uploads images to the Flask endpoint and returns:

* Predicted class
* Confidence score

---

## Current Performance

* Multi-class CNN classification
* Validation accuracy around 74%
* Lightweight architecture suitable for low-resource devices

---

## Deployment Possibilities

The model architecture is suitable for:

* Raspberry Pi deployment
* TensorFlow Lite conversion
* Edge AI applications
* Real-time image classification systems

---

## Future Improvements

* Larger and more balanced dataset
* Backbone fine-tuning
* TensorFlow Lite optimization
* Real-time camera inference
* Grad-CAM visualization
* Edge deployment benchmarking

---
