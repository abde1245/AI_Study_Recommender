import mysql.connector
from flask import flash
import pandas as pd

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            #password='password',  # Your actual MySQL password here
            database='study_recommendation_system'
        )
        print("Database connection successful")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def add_study_session(user_id, subject, duration, focus, mood, environment):
    connection = connect_to_db()
    cursor = connection.cursor()
    query = """INSERT INTO StudySessions 
               (user_id, subject, duration, focus_level, mood, environment, session_date, session_time)
               VALUES (%s, %s, %s, %s, %s, %s, CURDATE(), CURTIME())"""
    cursor.execute(query, (user_id, subject, duration, focus, mood, environment))
    connection.commit()
    cursor.close()
    connection.close()

def get_user_data(user_id):
    connection = connect_to_db()
    query = f"SELECT * FROM StudySessions WHERE user_id = {user_id}"
    df = pd.read_sql(query, connection)
    connection.close()
    return df
