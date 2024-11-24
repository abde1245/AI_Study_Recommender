CREATE DATABASE study_recommendation_system;
USE study_recommendation_system;

-- Users Table
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100),
    age INT,
    favorite_subjects VARCHAR(255),
    preferred_study_time VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Study Sessions Table
CREATE TABLE StudySessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    subject VARCHAR(100),
    duration INT,
    focus_level INT,  -- Scale of 1-5
    mood VARCHAR(50),
    environment VARCHAR(100),
    session_date DATE,
    session_time TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);


CREATE TABLE Recommendations (
    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    suggestion TEXT,
    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ON DELETE CASCADE
);


CREATE TABLE Feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    recommendation_id INT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comments TEXT,
    feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ON DELETE CASCADE,
    FOREIGN KEY (recommendation_id) REFERENCES Recommendations(recommendation_id)
        ON DELETE CASCADE
);


-- Inserting users
INSERT INTO Users (name, email, age)
VALUES 
    ('Alice Johnson', 'alice@example.com', 22),
    ('Bob Smith', 'bob@example.com', 21),
    ('Charlie Brown', 'charlie@example.com', 23);

-- Inserting study sessions
INSERT INTO StudySessions (user_id, subject, duration, session_date)
VALUES 
    (1, 'Mathematics', 60, '2024-11-15'),
    (1, 'Physics', 45, '2024-11-16'),
    (2, 'Chemistry', 30, '2024-11-15'),
    (3, 'Biology', 50, '2024-11-14');

-- Inserting recommendations
INSERT INTO Recommendations (user_id, suggestion)
VALUES 
    (1, 'Focus on revising calculus problems for better understanding.'),
    (2, 'Spend 20 minutes daily on organic chemistry reactions.'),
    (3, 'Try spaced repetition for biology terms and definitions.');



