from flask import Flask, session, request, render_template, redirect, url_for, flash
import pickle
import json
import numpy as np
from application_logging.logger import Logger
from flask_cors import cross_origin
from pymongo import MongoClient
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

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
# model = pickle.load(open('Scaler_Credit_Data .pkl', 'rb'))
# model2 = pickle.load(open('Credit_Data_RF.pkl', 'rb'))


@app.route("/", methods=['GET'])
def home():
    return render_template('base.html')


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

            # Redirect based on gender
            gender = user.get('gender', '').lower()

            if gender == 'male':
                return redirect(url_for('mental_health'))
            elif gender == 'female':
                return redirect(url_for('track_periods'))
            else:
                return redirect(url_for('default_page'))

    # If it's a GET request or if the login is unsuccessful, render the login page
    return render_template('login.html')


def get_user_info():
    # Retrieve user information from the session
    user_info = session.get('user_info')
    print("User Info from Session:", user_info)
    return user_info


# ... (existing code)
# Define a function to assess suicide risk
with open('mental_health_models//Mindflow_Suicide_model.pkl', 'rb') as file:
    loaded_gb_model = pickle.load(file)

with open('mental_health_models//Mindflow_Suicide_scaler.pkl', 'rb') as file:
    loaded_scaler = pickle.load(file)

with open('mental_health_models//Mindflow_Suicide_risk_factors.pkl', 'rb') as file:
    loaded_risk_factors = pickle.load(file)

# Define a function to assess suicide risk


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


@app.route("/menstrual_info", methods=['GET', 'POST'])
def menstrual_info():
    user = get_user_info()  # Replace with your logic to get user information

    if user and user.get('gender', '').lower() == 'female':
        # Allow access to the track_periods page for female users
        return render_template('menstrual_info.html')
    else:
        # Redirect to another page or display an error message
        return redirect(url_for('access_denied'))
    if request.method == 'POST':
        # Process the form data for menstrual information
        # Add your logic here
        pass

    return render_template('menstrual_info.html')


@app.route("/track_periods")
def track_periods():
    # Assuming the user information is available in the session or database
    # Replace this with your actual way of retrieving user information
    user = get_user_info()  # Replace with your logic to get user information

    if user and user.get('gender', '').lower() == 'female':
        # Allow access to the track_periods page for female users
        return redirect('http://localhost:3000/d/3kwKHuvIc/mindflow-menstrual-dashboard?orgId=1')
    else:
        # Redirect to another page or display an error message
        return redirect(url_for('access_denied'))

# You can create a separate route for an access denied page


@app.route("/access_denied")
def access_denied():
    return render_template('access_denied.html')


#

if __name__ == '__main__':
    app.run(debug=True)
