from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from analytics import plot_study_distribution
from models import connect_to_db, get_user_data

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        connection = connect_to_db()
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO Users (name, email, age) VALUES (%s, %s, %s)", 
                           (name, email, 21))
            connection.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect('/login')
        except mysql.connector.Error as err:
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            connection.close()
    return render_template('register.html')

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        connection = connect_to_db()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user:
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            return redirect('/dashboard')
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    return render_template('dashboard.html', name=session['name'])

# Add Study Session
@app.route('/add_session', methods=['GET', 'POST'])
def add_session():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        subject = request.form['subject']
        duration = request.form['duration']
        user_id = session['user_id']
        
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO StudySessions (user_id, subject, duration, session_date) VALUES (%s, %s, %s, CURDATE())", 
                       (user_id, subject, duration))
        connection.commit()
        cursor.close()
        connection.close()
        flash("Study session added!", "success")
        return redirect('/dashboard')

    return render_template('add_session.html')

@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    study_chart = plot_study_distribution(user_id)
    if not study_chart:
        flash("No study session data available.", "warning")
        return redirect('/dashboard')

    return render_template('analytics.html', study_chart=study_chart)


@app.route('/recommendations')
def recommendations():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    recommendations = generate_recommendations(user_id)
    return render_template('recommendations.html', recommendations=recommendations)

def generate_recommendations(user_id):
    connection = connect_to_db()
    study_sessions = pd.read_sql("SELECT * FROM StudySessions", connection)
    user_data = pd.read_sql(f"SELECT * FROM StudySessions WHERE user_id = {user_id}", connection)
    connection.close()

    if study_sessions.empty or user_data.empty:
        return []

    study_sessions['combined_features'] = study_sessions['subject'] + ' ' + study_sessions['duration'].astype(str)
    user_data['combined_features'] = user_data['subject'] + ' ' + user_data['duration'].astype(str)

    tfidf = TfidfVectorizer()
    study_matrix = tfidf.fit_transform(study_sessions['combined_features'])
    user_matrix = tfidf.transform(user_data['combined_features'])

    similarity_scores = cosine_similarity(user_matrix, study_matrix)
    top_indices = similarity_scores.argsort().flatten()[-3:]
    recommendations = study_sessions.iloc[top_indices]

    return recommendations[['subject', 'duration', 'session_date']].to_dict(orient='records')

# Home Route
@app.route('/')
def index():
    return render_template('index.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
