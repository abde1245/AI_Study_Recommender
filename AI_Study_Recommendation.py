import mysql.connector
import pandas as pd

# Establishing the database connection
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',       # Change this to your MySQL username
            #password='password', # Change this to your MySQL password
            database='study_recommendation_system'
        )
        print("Database connection successful!")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Fetching data from the database
def fetch_data(query):
    connection = connect_to_db()
    if connection:
        df = pd.read_sql(query, connection)
        connection.close()
        return df
    else:
        return None


def get_user_study_sessions(user_id):
    query = f"""
    SELECT subject, duration, session_date
    FROM StudySessions
    WHERE user_id = {user_id}
    """
    return fetch_data(query)

def get_all_study_sessions():
    query = """
    SELECT user_id, subject, duration, session_date
    FROM StudySessions
    """
    return fetch_data(query)



from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def generate_recommendations(user_id):
    # Fetch all study sessions data
    study_sessions = get_all_study_sessions()
    if study_sessions is None or study_sessions.empty:
        print("No study sessions found.")
        return None

    # Get study sessions of the specific user
    user_data = get_user_study_sessions(user_id)
    if user_data is None or user_data.empty:
        print("No study data for this user.")
        return None

    # Combine subject and duration as a single feature for analysis
    study_sessions['combined_features'] = study_sessions['subject'] + ' ' + study_sessions['duration'].astype(str)
    user_data['combined_features'] = user_data['subject'] + ' ' + user_data['duration'].astype(str)

    # Vectorize the combined features using TF-IDF
    tfidf = TfidfVectorizer()
    study_matrix = tfidf.fit_transform(study_sessions['combined_features'])
    user_matrix = tfidf.transform(user_data['combined_features'])

    # Calculate similarity scores between user's data and all sessions
    similarity_scores = cosine_similarity(user_matrix, study_matrix)

    # Get the most relevant study sessions
    top_indices = similarity_scores.argsort().flatten()[-3:]
    recommendations = study_sessions.iloc[top_indices]

    return recommendations[['subject', 'duration', 'session_date']]

# Example usage
if __name__ == "__main__":
    user_id = 1
    recommendations = generate_recommendations(user_id)
    if recommendations is not None:
        print("\nRecommended Study Sessions:")
        print(recommendations)
