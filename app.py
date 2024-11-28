from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
from models import connect_to_db, add_study_session
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from analytics import plot_study_distribution

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
            cursor.execute("INSERT INTO Users (name, email, password, age) VALUES (%s, %s, %s, %s)", 
                           (name, email, password, 21))  # Storing password as plain text, consider hashing it
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
        cursor.execute("SELECT * FROM Users WHERE email = %s AND password = %s", (email, password))
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
        focus = request.form['focus']
        mood = request.form['mood']
        environment = request.form['environment']
        user_id = session['user_id']
        
        add_study_session(user_id, subject, duration, focus, mood, environment)
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


@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    connection = connect_to_db()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        # Handle feedback submission
        recommendation_id = request.form.get('recommendation_id')
        rating = request.form.get('rating')
        comments = request.form.get('comments')

        try:
            cursor.execute("""
                INSERT INTO Feedback (user_id, recommendation_id, rating, comments)
                VALUES (%s, %s, %s, %s)
            """, (user_id, recommendation_id, rating, comments))
            connection.commit()
            flash("Feedback submitted successfully!", "success")
        except mysql.connector.Error as err:
            print(f"Error inserting feedback: {err}")
            connection.rollback()
            flash("Error submitting feedback.", "danger")

    try:
        # Fetch existing recommendations for the user, including feedback if any
        cursor.execute("""
            SELECT r.recommendation_id, r.suggestion, r.recommendation_date, f.rating, f.comments 
            FROM Recommendations r
            LEFT JOIN Feedback f ON r.recommendation_id = f.recommendation_id AND f.user_id = %s
            WHERE r.user_id = %s
        """, (user_id, user_id))
        recommendations = cursor.fetchall()
    
    except mysql.connector.Error as err:
        print(f"Error fetching recommendations: {err}")
        recommendations = [] # Handle errors gracefully

    finally:
        cursor.close()
        connection.close()
        


    return render_template('recommendations.html', recommendations=recommendations)


def generate_recommendations(user_id):
    connection = connect_to_db()
    study_sessions = pd.read_sql("SELECT * FROM StudySessions", connection)  # Get all study sessions
    user_data = pd.read_sql(f"SELECT * FROM StudySessions WHERE user_id = {user_id}", connection) # User's study sessions
    connection.close() #Close after reading

    if study_sessions.empty or user_data.empty:
        return [] # Handle cases where there's no data

    # Feature Engineering (Combine subject and duration)
    study_sessions['combined_features'] = study_sessions['subject'] + ' ' + study_sessions['duration'].astype(str)
    user_data['combined_features'] = user_data['subject'] + ' ' + user_data['duration'].astype(str)

    # TF-IDF Vectorization
    tfidf = TfidfVectorizer()
    study_matrix = tfidf.fit_transform(study_sessions['combined_features'])
    user_matrix = tfidf.transform(user_data['combined_features'])

    # Cosine Similarity Calculation
    similarity_scores = cosine_similarity(user_matrix, study_matrix)

    # Get top recommendations (e.g., top 3)
    top_indices = similarity_scores.argsort().flatten()[-3:]
    recommendations_df = study_sessions.iloc[top_indices]
    recommendations_list = recommendations_df[['subject', 'duration']].to_dict(orient='records')



    connection = connect_to_db()
    cursor = connection.cursor()
    try:
        for recommendation in recommendations_list:
            suggestion = f"Study {recommendation['subject']} for {recommendation['duration']} minutes."
            cursor.execute("""
                INSERT INTO Recommendations (user_id, suggestion) 
                VALUES (%s, %s)
            """, (user_id, suggestion))

        connection.commit()  # Important: Commit changes to the database
    except mysql.connector.Error as err:
        print(f"Error inserting recommendations: {err}")
        connection.rollback() # Rollback if any error
    finally:
        cursor.close()
        connection.close()
    return recommendations_list # Return for immediate display


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
    app.run(debug=True, port=5000)
