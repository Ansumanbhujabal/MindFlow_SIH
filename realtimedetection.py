import cv2
from keras.models import model_from_json
import numpy as np
import json
import time

json_file = open("facialemotionmodel.json", "r")
model_json = json_file.read()
json_file.close()
model = model_from_json(model_json)

model.load_weights("facialemotionmodel.h5")
haar_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(haar_file)


def extract_features(image):
    feature = np.array(image)
    feature = feature.reshape(1, 48, 48, 1)
    return feature/255.0


webcam = cv2.VideoCapture(0)
labels = {0: 'angry', 1: 'disgust', 2: 'fear',
          3: 'happy', 4: 'neutral', 5: 'sad', 6: 'surprise'}

# Initialize an empty list to store predictions
output_data = {"predictions": []}

# Set the interval for saving the JSON file (4 seconds)
save_interval = 60
last_save_time = time.time()

while True:
    i, im = webcam.read()
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(im, 1.3, 5)

    try:
        for (p, q, r, s) in faces:
            image = gray[q:q+s, p:p+r]
            cv2.rectangle(im, (p, q), (p+r, q+s), (255, 0, 0), 2)
            image = cv2.resize(image, (48, 48))
            img = extract_features(image)
            pred = model.predict(img)
            prediction_label = labels[pred.argmax()]

            # Append the prediction to the output_data dictionary
            output_data["predictions"].append({
                "label": prediction_label,
                "coordinates": {"x": p, "y": q, "width": r, "height": s}
            })

            cv2.putText(im, '% s' % (prediction_label), (p-10, q-10),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 255))
        cv2.imshow("Output", im)
        cv2.waitKey(1)
    except cv2.error:
        pass

    # Save the JSON file every 4 seconds
    current_time = time.time()
    if current_time - last_save_time >= save_interval:
        with open('output_predictions.json', 'w') as json_file:
            json.dump(output_data, json_file, indent=15)
        # Reset the last save time
        last_save_time = current_time
