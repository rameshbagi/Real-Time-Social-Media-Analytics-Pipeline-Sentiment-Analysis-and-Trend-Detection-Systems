import sqlite3
import json
from datetime import datetime
import os
import logging
from utils.helpers import ensure_directory_exists

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path='src/default.db'):
        # Ensure the directory exists
        db_dir = os.path.dirname(db_path)
        ensure_directory_exists(db_dir)
        
        self.db_path = db_path
        self._create_tables()
        logger.info(f"Database initialized at {db_path}")

    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create tweets table with proper indices
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tweets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user TEXT,
                    retweet_count INTEGER DEFAULT 0,
                    favorite_count INTEGER DEFAULT 0,
                    sentiment TEXT,
                    trends TEXT
                )
            ''')

            # Create indices for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON tweets(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user ON tweets(user)')

            conn.commit()
            logger.info("Database tables and indices created successfully")
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def store(self, data):
        """Store processed tweet data in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Ensure data is properly formatted
            sentiment_json = json.dumps(data.get('sentiment', {}))
            trends_json = json.dumps(data.get('trends', {}))
            timestamp = data.get('timestamp', datetime.now().isoformat())

            cursor.execute('''
                INSERT INTO tweets (
                    text, timestamp, user, 
                    retweet_count, favorite_count,
                    sentiment, trends
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('text', ''),
                timestamp,
                data.get('user', 'unknown'),
                int(data.get('retweet_count', 0)),
                int(data.get('favorite_count', 0)),
                sentiment_json,
                trends_json
            ))

            conn.commit()
            logger.debug(f"Stored tweet from user {data.get('user', 'unknown')}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error storing data: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error storing data: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_recent_tweets(self, limit=100):
        """Retrieve recent tweets from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM tweets 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))

            columns = [description[0] for description in cursor.description]
            tweets = []

            for row in cursor.fetchall():
                tweet = dict(zip(columns, row))
                try:
                    tweet['sentiment'] = json.loads(tweet['sentiment'])
                    tweet['trends'] = json.loads(tweet['trends'])
                except json.JSONDecodeError:
                    tweet['sentiment'] = {}
                    tweet['trends'] = {}
                tweets.append(tweet)

            return tweets

        except sqlite3.Error as e:
            logger.error(f"Error retrieving tweets: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_sentiment_stats(self, hours=24):
        """Get sentiment statistics for the last n hours"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT 
                    json_extract(sentiment, '$.sentiment') as sentiment_label,
                    COUNT(*) as count
                FROM tweets 
                WHERE datetime(timestamp) > datetime('now', '-? hours')
                GROUP BY sentiment_label
            ''', (hours,))

            stats = dict(cursor.fetchall())
            return stats

        except sqlite3.Error as e:
            logger.error(f"Error retrieving sentiment stats: {e}")
            return {}
        finally:
            if conn:
                conn.close()

    def cleanup_old_data(self, days=7):
        """Remove tweets older than specified days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                DELETE FROM tweets 
                WHERE datetime(timestamp) < datetime('now', '-? days')
            ''', (days,))

            conn.commit()
            logger.info(f"Removed tweets older than {days} days")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error cleaning up old data: {e}")
            return False
        finally:
            if conn:
                conn.close() 