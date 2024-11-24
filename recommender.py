import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import mysql.connector

def connect_to_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='study_recommendation_system'
    )

def get_user_data(user_id):
    connection = connect_to_db()
    query = f"SELECT * FROM StudySessions WHERE user_id = {user_id}"
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def content_based_recommendations(user_id):
    data = get_user_data(user_id)
    if data.empty:
        return []

    data['combined_features'] = data['subject'] + ' ' + data['duration'].astype(str)
    tfidf = TfidfVectorizer()
    study_matrix = tfidf.fit_transform(data['combined_features'])

    similarity_scores = cosine_similarity(study_matrix)
    recommended_indices = similarity_scores.argsort(axis=1)[:, -3:]
    recommendations = data.iloc[recommended_indices.flatten()]
    
    return recommendations[['subject', 'duration', 'session_date']].to_dict(orient='records')
