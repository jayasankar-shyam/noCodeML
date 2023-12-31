# app.py
from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib
matplotlib.use('agg')  # Use the 'agg' backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import ast
import mysql.connector
app = Flask(__name__)

servername = "localhost"
username = "root"
password = "password"
dbname = "NoCodeML"

# Helper function for linear regression
def perform_linear_regression(file):
    df = pd.read_csv(file)
    x = df.iloc[:, :-1].values.reshape(-1, 1)
    y = df.iloc[:, -1].values.reshape(-1, 1)

    # Perform Linear Regression
    model = LinearRegression()
    model.fit(x, y)

    # Create scatter plot and regression line
    plt.scatter(x, y)
    plt.plot(x, model.predict(x), color='red')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')

    # Save plot to BytesIO object
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)
    img_str = base64.b64encode(image_stream.read()).decode('utf-8')

    plt.close()

    return model, img_str

# Main route
@app.route('/')
def index():
    # Connect to the database
    connection = mysql.connector.connect(
        host=servername,
        user=username,
        password=password,
        database=dbname
    )

    # Create a cursor to execute queries
    cursor = connection.cursor(dictionary=True)

    # Execute the query to select all columns from the 'users' table
    cursor.execute("SELECT id, full_name, email FROM users where password='pass'")

    # Fetch all rows from the result set
    result = cursor.fetchall()
    id=result[0]['id']
    name=result[0]['full_name']
    email=result[0]['email']
    # Close the cursor and connection
    cursor.close()
    connection.close()

    return render_template('landing.html',name=name,id=id,email=email)

# Upload route
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    model, plot = perform_linear_regression(file)

    return render_template('linearreg.html', plot=plot, model=model)

# Predict route
@app.route('/predict', methods=['POST'])
def predict():
    new_value = float(request.form['new_value'])  # Get the new value as a float
    # Create a new instance of LinearRegression
    model = LinearRegression()

    # Set the parameters for the new instance
    model.intercept_ = request.form['inter']
    model.intercept_=float(model.intercept_.strip('[]'))
    model.coef_ = request.form['coef']
    outer_list = ast.literal_eval(model.coef_)
    inner_list_floats = [float(item) for item in outer_list[0]]
    model.coef_ = np.array([inner_list_floats])
    # Reshape the new value to fit the model's input requirements
    new_value_reshaped = np.array([new_value]).reshape(-1, 1)

    # Use the trained model to predict the new value
    prediction = model.predict(new_value_reshaped)


    return render_template('linearreg.html', prediction=prediction, model=model, new_value=new_value)

app.run(debug=True, use_reloader=True, port=5004)
