import sqlite3
import json
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """Generate sample data for the dashboard"""
    # Connect to database
    conn = sqlite3.connect('src/default.db')
    cursor = conn.cursor()
    
    # Create tweets table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tweets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        user TEXT,
        timestamp DATETIME,
        sentiment JSON
    )
    ''')
    
    # Sample topics and sentiments
    topics = ['Python', 'Data Science', 'AI', 'Machine Learning', 
             'Analytics', 'Big Data', 'Deep Learning', 'NLP']
    
    sentiments = ['positive', 'negative', 'neutral']
    users = ['data_enthusiast', 'ai_lover', 'ml_expert', 'tech_guru', 'python_dev']
    
    # Generate sample tweets for the last 24 hours
    now = datetime.now()
    for i in range(100):  # Generate 100 sample tweets
        # Random timestamp within last 24 hours
        timestamp = now - timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        # Generate random tweet text
        topic1 = random.choice(topics)
        topic2 = random.choice(topics)
        text = f"Really interesting developments in {topic1} and its applications in {topic2}! #Tech #Innovation"
        
        # Generate random sentiment
        sentiment = random.choice(sentiments)
        polarity = random.uniform(-1, 1)
        sentiment_data = {
            'sentiment': sentiment,
            'polarity': polarity
        }
        
        # Insert tweet into database
        cursor.execute('''
        INSERT INTO tweets (text, user, timestamp, sentiment)
        VALUES (?, ?, ?, ?)
        ''', (text, random.choice(users), timestamp.strftime('%Y-%m-%d %H:%M:%S'), 
              json.dumps(sentiment_data)))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Sample data generated successfully!")

if __name__ == '__main__':
    generate_sample_data() 