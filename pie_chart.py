# Import necessary libraries
from flask import Flask, render_template, request
from pymongo import MongoClient
import pandas as pd
import plotly.express as px

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('pie_chart.html', chart=None)

@app.route('/show_results', methods=['GET', 'POST'])
def show_results():
    if request.method == 'POST':
        user_email = request.form['user_email']
        # Connect to your MongoDB and retrieve the user's survey data based on their email
        client = MongoClient('mongodb://localhost:27017')
        db = client.recommendation_system
        survey_data = db.users_survey_data.find_one({'user_email': user_email})

        if survey_data:
            # Create a dictionary with the custom titles for the interests
            custom_titles = {
                'aiInterest': 'Artificial Intelligence',
                'dbInterest': 'Databases and Search',
                'seInterest': 'Software Engineering',
                'algoInterest': 'Algorithms and Computers',
            }

            # Create a dictionary to store the interest counts
            interest_counts = {}

            # Extract and count the interests
            for field, title in custom_titles.items():
                interests = survey_data.get(field, '').split(' and ')
                count = len(interests)
                interest_counts[title] = count

            # Create a DataFrame from the interest counts
            df = pd.DataFrame({'Interest': list(interest_counts.keys()), 'Count': list(interest_counts.values())})

            # Create a pie chart using Plotly
            fig = px.pie(df, names='Interest', values='Count', title=f'Interests of {user_email}')

            # Convert the Plotly chart to HTML
            chart_html = fig.to_html(full_html=False)

            return render_template('pie_chart.html', chart=chart_html)
        else:
            return "Enter correct email."

    return render_template('pie_chart.html', chart=None)

if __name__ == '__main__':
    app.run(debug=True, port=9999)
