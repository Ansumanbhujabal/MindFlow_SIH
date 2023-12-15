import pickle
from application_logging.logger import Logger
from flask import Flask, request, render_template, redirect, url_for
from flask_cors import cross_origin
from pymongo import MongoClient


app = Flask(__name__)

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


@app.route("/mental_health", methods=['GET', 'POST'])
def mental_health():
    if request.method == 'POST':
        # Process the form data for mental health assessment
        # Add your logic here
        pass

    return render_template('mental_health.html')


@app.route("/menstrual_info", methods=['GET', 'POST'])
def menstrual_info():
    if request.method == 'POST':
        # Process the form data for menstrual information
        # Add your logic here
        pass

    return render_template('menstrual_info.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        password = request.form['password']
        gender = request.form['gender']
        phone_number = request.form['phoneNumber']

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

        # Add your logic here, for example, check email and password against database

        # After processing the data, you can redirect to another page
        # return redirect(url_for('dashboard'))

    # If it's a GET request, simply render the login page
    return render_template('login.html')

# ... (existing code)


@app.route("/track_periods")
def track_periods():
    return render_template('track_periods.html')

# @app.route("/report", methods=['GET', 'POST'])
# @cross_origin()
# def report():
#     """
#     :Method_Name: report
#     :DESC: This Will Return The  Data Report Page
#     :param: None
#     :return: report.html
#     """

#     try:
#         logger.info('INFO', 'The Home Method Call The index.html Page')
#         return render_template('German_Credit_Data.html')

#     except Exception as e:
#         logger.info('INFO', 'Something Went Wrong With The Home Method')
#         raise Exception(
#             f'(Home)- Something Went Wrong With The Method \n' + str(e))


# @app.route("/predict", methods=['POST'])
# @cross_origin()
# def predict():
#     """
#     :Method_Name: predict
#     :DESC: This Will Return The Credit Risk Is Bad or Good
#     :param: None
#     :return: The Risk Is Bad or Good
#     """

#     try:
#         logger.info('INFO', 'Checking The Method Is Post Or Not')
#         if request.method == "POST":

#             try:
#                 logger.info(
#                     'INFO', 'The Post Method Is Call & Calling The Each Feature')

#                 status = int(request.form['status'])

#                 duration = int(request.form['duration'])

#                 credit_history = int(request.form['credit_history'])

#                 purpose = int(request.form['purpose'])

#                 amount = int(request.form['amount'])

#                 savings = int(request.form['savings'])

#                 employment_duration = int(request.form['employment_duration'])

#                 personal_status_sex = int(request.form['personal_status_sex'])

#                 installment_rate = int(request.form['installment_rate'])

#                 present_residence = int(request.form['present_residence'])

#                 property = int(request.form['property'])

#                 age = int(request.form['age'])

#                 number_credits = int(request.form['number_credits'])

#                 telephone = int(request.form['telephone'])

#                 value = model.transform([[status, duration, credit_history, purpose, amount, savings,
#                                           employment_duration, personal_status_sex, installment_rate,
#                                           present_residence, property, age, number_credits, telephone]])

#                 prediction = model2.predict(value)

#                 if prediction == 0:
#                     label = 'Bad'
#                 else:
#                     label = 'Good'

#                 return render_template('result.html', prediction_text=" The Credit Risk Is {}".format(label))

#             except Exception as e:
#                 logger.info(
#                     'INFO', 'Something Went Wrong With The Post From Predict Method')
#                 raise Exception(
#                     f'(Predict)- Something Went Wrong With The Method \n' + str(e))

#         else:
#             logger.info('INFO', 'The Post Method Is Not Selected')
#             return render_template('index.html')

#     except Exception as e:
#         logger.info('INFO', 'Something Went Wrong With The Home Method')
#         raise Exception(
#             f'(Predict)- Something Went Wrong With The Method \n' + str(e))

if __name__ == '__main__':
    app.run(debug=True)
