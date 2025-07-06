import sqlite3
import time
from datetime import datetime
import os

def get_recent_tweets(db_path='src/default.db'):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT text, user, timestamp, sentiment
            FROM tweets
            ORDER BY timestamp DESC
            LIMIT 5
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_sentiment_stats(db_path='src/default.db'):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                json_extract(sentiment, '$.sentiment') as sentiment,
                COUNT(*) as count
            FROM tweets
            GROUP BY sentiment
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def print_divider():
    print("-" * 80)

def show_dashboard():
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("\n=== Real-Time Social Media Analytics ===\n")
    
    # Show recent tweets
    print("Recent Tweets:")
    print_divider()
    print(f"{'Timestamp':<20} {'User':<15} {'Sentiment':<10} Tweet")
    print_divider()
    
    tweets = get_recent_tweets()
    for tweet in tweets:
        text, user, timestamp, sentiment = tweet
        # Truncate long tweets
        truncated_text = text[:50] + "..." if len(text) > 50 else text
        print(f"{timestamp[:19]:<20} {user[:15]:<15} {str(sentiment)[:10]:<10} {truncated_text}")
    
    print_divider()
    
    # Show sentiment statistics
    print("\nSentiment Analysis:")
    print_divider()
    print(f"{'Sentiment':<15} Count")
    print_divider()
    
    sentiments = get_sentiment_stats()
    for sentiment in sentiments:
        label, count = sentiment
        print(f"{str(label):<15} {count}")
    
    print_divider()
    print("\nPress Ctrl+C to exit")

def main():
    try:
        while True:
            show_dashboard()
            time.sleep(5)  # Update every 5 seconds
    except KeyboardInterrupt:
        print("\nExiting terminal visualization...")

if __name__ == "__main__":
    main() 