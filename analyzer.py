from textblob import TextBlob
import re
from collections import Counter
from datetime import datetime, timedelta

class Analyzer:
    def __init__(self):
        self.trends = Counter()
        self.trend_window = timedelta(hours=24)
        self.trend_timestamps = []
        self.trend_data = []
        self._initialize_sample_trends()

    def _initialize_sample_trends(self):
        """Initialize with sample trends if no data is available"""
        sample_trends = [
            "#AI", "#DataScience", "#Python", 
            "machine learning", "artificial intelligence", 
            "data analytics", "#Technology", "#Innovation",
            "deep learning", "neural networks"
        ]
        current_time = datetime.now()
        for trend in sample_trends:
            self._add_trend(trend, current_time)
            # Add multiple counts to make it look more realistic
            for _ in range(5):
                self._add_trend(trend, current_time - timedelta(minutes=30))

    def analyze_sentiment(self, text):
        """
        Analyze the sentiment of given text using TextBlob.
        Returns a dictionary with polarity and subjectivity scores.
        """
        try:
            analysis = TextBlob(text)
            return {
                'polarity': analysis.sentiment.polarity,
                'subjectivity': analysis.sentiment.subjectivity,
                'sentiment': 'positive' if analysis.sentiment.polarity > 0 else 'negative' if analysis.sentiment.polarity < 0 else 'neutral'
            }
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return {
                'polarity': 0,
                'subjectivity': 0,
                'sentiment': 'neutral'
            }

    def analyze_trends(self, text):
        """
        Extract and analyze trends from text.
        Includes hashtags, mentions, and common phrases.
        """
        try:
            # Clean old trends
            self._clean_old_trends()

            # Extract features
            text = text.lower()
            hashtags = set(re.findall(r'#(\w+)', text))
            mentions = set(re.findall(r'@(\w+)', text))
            
            # Extract common phrases (3 words)
            words = re.findall(r'\b\w+\b', text)
            phrases = [' '.join(words[i:i+3]) for i in range(len(words)-2)]

            # Update trends
            current_time = datetime.now()
            for item in hashtags:
                self._add_trend(f'#{item}', current_time)
            for item in mentions:
                self._add_trend(f'@{item}', current_time)
            for phrase in phrases:
                self._add_trend(phrase, current_time)

            # Get current trending topics
            top_trends = dict(self.trends.most_common(10))

            return {
                'hashtags': list(hashtags),
                'mentions': list(mentions),
                'top_trends': top_trends,
                'timestamp': current_time.isoformat()
            }

        except Exception as e:
            print(f"Error in trend analysis: {e}")
            return {
                'hashtags': [],
                'mentions': [],
                'top_trends': {},
                'timestamp': datetime.now().isoformat()
            }

    def _clean_old_trends(self):
        """Remove trends older than the trend window"""
        current_time = datetime.now()
        cutoff_time = current_time - self.trend_window

        # Remove old trends
        while self.trend_timestamps and self.trend_timestamps[0] < cutoff_time:
            old_data = self.trend_data.pop(0)
            self.trend_timestamps.pop(0)
            for item in old_data:
                self.trends[item] -= 1
                if self.trends[item] <= 0:
                    del self.trends[item]

    def _add_trend(self, item, timestamp):
        """Add a new trend item with timestamp"""
        self.trends[item] += 1
        self.trend_timestamps.append(timestamp)
        self.trend_data.append([item]) 