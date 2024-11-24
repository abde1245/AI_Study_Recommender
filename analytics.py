# analytics.py
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd
from models import get_user_data

def plot_study_distribution(user_id):
    # Fetch the study session data for the user
    data = get_user_data(user_id)
    if data.empty:
        return None

    # Generate a bar chart to visualize study distribution by subject
    plt.figure(figsize=(10, 6))
    data['subject'].value_counts().plot(kind='bar', color='skyblue')
    plt.title('Study Distribution by Subject')
    plt.xlabel('Subject')
    plt.ylabel('Number of Sessions')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save plot as base64 encoded image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    plt.close()
    return image_base64
