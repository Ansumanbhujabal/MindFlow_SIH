from flask import Flask, session, request, render_template, redirect, url_for, flash
import pickle
import json
from datetime import datetime
import time
import numpy as np
from application_logging.logger import Logger
from flask_cors import cross_origin
from pymongo import MongoClient
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from flask import Response
from keras.models import model_from_json
import cv2

app = Flask(__name__)
app.secret_key = 'Mysecretkey'  # Replace with your actual secret key
# Use 'filesystem' or another session type
app.config['SESSION_TYPE'] = 'filesystem'

logger = Logger('logfiles/application.log')

# Configure MongoDB connection
client = MongoClient(
    "mongodb+srv://insaneengineer6:e2PX8ym6bAOCBxsJ@cluster0.stpj7kz.mongodb.net/")
# Replace 'your_database_name' with your actual database name
db = client['MindFlow']
users_collection = db['New']

# ... (existing code)

# Define a function to assess suicide risk
with open('mental_health_models//Mindflow_Suicide_model.pkl', 'rb') as file:
    loaded_gb_model = pickle.load(file)

with open('mental_health_models//Mindflow_Suicide_scaler.pkl', 'rb') as file:
    loaded_scaler = pickle.load(file)

with open('mental_health_models//Mindflow_Suicide_risk_factors.pkl', 'rb') as file:
    loaded_risk_factors = pickle.load(file)

def assess_suicide_risk(prediction, risk_factors):
    if prediction == 1:
        if risk_factors['question6'] > 60 or \
           risk_factors['question7'] > 60 or \
           risk_factors['question8'] > 60:
            return 'High Risk'
        elif risk_factors['question7'] > 50:
            return 'Intermediate Risk'
    return 'Normal Risk'

# Define a function to load models and make predictions
def load_and_predict(user_input):
    try:
        # Convert the user input to a numpy array
        user_input_array = np.array(
            [[user_input[f'question{i}'] for i in range(1, 11)]])

        # Make predictions with the loaded model
        prediction = loaded_gb_model.predict(user_input_array)[0]

        # Assess suicide risk for the user input
        risk_factors_input = {f'question{i}': int(
            user_input[f'question{i}']) for i in range(6, 9)}
        suicide_risk = assess_suicide_risk(prediction, risk_factors_input)

        return prediction, suicide_risk
    except Exception as e:
        return None, str(e)


@app.route("/mental_health", methods=['GET', 'POST'])
def mental_health():
    user = get_user_info()
    if request.method == 'POST':
        # Retrieve user inputs from the form
        user_inputs = {f'question{i}': float(
            request.form.get(f'question{i}')) for i in range(1, 11)}

        # Print the user inputs to the console
        for key, value in user_inputs.items():
            print(f"{key}: {value}")

        # Load models and make predictions using a pipeline
        user_input_array = np.array(
            [[user_inputs[f'question{i}'] for i in range(1, 11)]])
        prediction = loaded_gb_model.predict(user_input_array)[0]

        # Assess suicide risk for the user input
        risk_factors_input = {f'question{i}': int(
            user_inputs[f'question{i}']) for i in range(6, 9)}
        suicide_risk = assess_suicide_risk(prediction, risk_factors_input)

        # Print the prediction to the console
        # if prediction is not None:
        #     print(f"\nPrediction: {prediction}")
        #     print(f"Suicide Risk: {suicide_risk}")
        result_dict = {
            "Name": get_user_info.__name__,
            "MentalStatePrediction": "Neutral" if prediction == 0 else ("Sad" if prediction == 1 else "Happy"),
            "SuicideRiskAssessment": "Not Applicable" if prediction != 1 else suicide_risk
        }
        print("\nResults:")
        for key, value in result_dict.items():
            print(f"{key}: {value}")

        # Save the results as a JSON file
        with open('result.json', 'w') as json_file:
            json.dump(result_dict, json_file)

    return render_template('mental_health.html')

@app.route("/badges", methods=['GET'])
def badges():
    return render_template('badges.html')


json_file = open("facialemotionmodel.json", "r")
model_json = json_file.read()
json_file.close()
model = model_from_json(model_json)
model.load_weights("facialemotionmodel.h5")
haar_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(haar_file)

# Initialize an empty list to store predictions
output_data = {"predictions": []}

# Set the interval for saving the JSON file (4 seconds)
save_interval = 20
last_save_time = time.time()


@app.route("/", methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        password = request.form['password']
        gender = request.form['gender']
        phone_number = request.form['phoneNumber']

        # Check if the email is already in use
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            flash('Email is already in use. Please choose a different email.', 'error')
            return render_template('signup.html')

        # Create a user document
        user_data = {
            'name': name,
            'age': age,
            'email': email,
            'password': password,
            'gender': gender,
            'phone_number': phone_number
        }

        # Insert the user document into the MongoDB collection
        users_collection.insert_one(user_data)

        # Redirect to a success page or any other desired page
        # Correct the template name if needed
        return redirect(url_for('login'))

    # If it's a GET request or if the form is not submitted, simply render the signup page
    return render_template('signup.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Process the form data for login
        email = request.form.get('email')
        password = request.form.get('password')

        # Add your logic here to check email and password against the database
        user = users_collection.find_one(
            {'email': email, 'password': password})

        if user:
            # User authentication successful
            # Store user information in the session
            session['user_info'] = {
                'email': user['email'],
                'name': user['name'],
                'gender': user['gender']
                # Add other user information as needed
            }
            flash('Got your first badge!', 'success')
            return redirect(url_for('mental_health'))

    # If it's a GET request or if the login is unsuccessful, render the login page
    return render_template('login.html')


def get_user_info():
    # Retrieve user information from the session
    user_info = session.get('user_info')
    print("User Info from Session:", user_info)
    return user_info


@app.route("/facial_emotion_detection")
def facial_emotion_detection():
    return render_template('facial_emotion_detection.html')


def extract_features(image):
    feature = np.array(image)
    feature = feature.reshape(1, 48, 48, 1)
    return feature/255.0


last_save_time = time.time()


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


last_save_time = None


def generate_frames():
    global last_save_time
    if last_save_time is None:
        last_save_time = time.time()
    webcam = cv2.VideoCapture(0)
    labels = {0: 'angry', 1: 'disgust', 2: 'fear',
              3: 'happy', 4: 'neutral', 5: 'sad', 6: 'surprise'}
    output_data = {"predictions": []}
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
            cv2.waitKey(20)
        except cv2.error:
            pass

        # Save the JSON file every 4 seconds
        current_time = time.time()
        if current_time - last_save_time >= save_interval:
            with open('output_predictions.json', 'w') as json_file:
                json.dump(output_data, json_file, indent=15)
            # # Reset the last save time
            last_save_time = current_time

        # Encode the frame in JPEG format
        _, jpeg = cv2.imencode('.jpg', im)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route("/user", methods=['GET'])
def user():
    return render_template('user.html')
  
@app.route("/access_denied")
def access_denied():
    return render_template('access_denied.html')

if __name__ == '__main__':
    app.run(debug=True)