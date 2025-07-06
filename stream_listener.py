import tweepy
import json
from datetime import datetime
import time
import random

class StreamListener(tweepy.StreamingClient):
    def __init__(self, api=None, analyzer=None, database=None):
        self.analyzer = analyzer
        self.database = database
        self.running = False
        self.use_sample_data = True  # Default to sample data
        try:
            if api and api.get('bearer_token'):
                super().__init__(bearer_token=api['bearer_token'])
                self.use_sample_data = False
            else:
                print("No valid Twitter API credentials found. Using sample data.")
        except Exception as e:
            print(f"Error initializing Twitter stream: {e}. Using sample data.")

    def _generate_sample_tweet(self):
        """Generate sample tweet data for testing"""
        sample_texts = [
            "Excited to learn about #AI and #MachineLearning today!",
            "Just finished a great #Python project on #DataScience",
            "The future of #Technology is in artificial intelligence",
            "Working on deep learning models with #TensorFlow",
            "Big data analytics is transforming business #Innovation",
            "Neural networks are amazing for #ComputerVision tasks",
            "Learning about natural language processing #NLP",
            "Cloud computing and #AI are the perfect combination",
            "Data visualization makes insights clearer #DataViz",
            "Building robust machine learning pipelines #MLOps"
        ]
        
        return {
            'text': random.choice(sample_texts),
            'timestamp': datetime.now().isoformat(),
            'user': f"sample_user_{random.randint(1, 1000)}",
            'retweet_count': random.randint(0, 100),
            'favorite_count': random.randint(0, 200)
        }

    def on_tweet(self, tweet):
        if not self.running:
            return False
            
        try:
            if hasattr(tweet, 'text'):
                # Process the tweet
                processed_data = {
                    'text': tweet.text,
                    'timestamp': datetime.now().isoformat(),
                    'user': tweet.author_id,
                    'retweet_count': getattr(tweet, 'public_metrics', {}).get('retweet_count', 0),
                    'favorite_count': getattr(tweet, 'public_metrics', {}).get('like_count', 0)
                }

                # Analyze sentiment and trends
                if self.analyzer:
                    sentiment = self.analyzer.analyze_sentiment(tweet.text)
                    trends = self.analyzer.analyze_trends(tweet.text)
                    processed_data.update({
                        'sentiment': sentiment,
                        'trends': trends
                    })

                # Store in database
                if self.database:
                    self.database.store(processed_data)

                return True

        except Exception as e:
            print(f"Error processing tweet: {e}")
        return True

    def on_error(self, status):
        print(f'Error: {status}')
        if status == 420:  # Rate limit reached
            print("Rate limit reached. Switching to sample data.")
            self.use_sample_data = True
            return False
        return True

    def start(self, track_keywords=None):
        """Start the stream with specified keywords"""
        if not track_keywords:
            track_keywords = ['python', 'data science', 'AI', 'machine learning']
        
        self.running = True
        
        if self.use_sample_data:
            print("Using sample data stream")
            self._start_sample_stream()
            return

        try:
            # Delete existing rules
            rules = self.get_rules()
            if rules and rules.data:
                rule_ids = [rule.id for rule in rules.data]
                self.delete_rules(rule_ids)

            # Add new rules
            rule = ' OR '.join(track_keywords)
            self.add_rules(tweepy.StreamRule(value=rule))
            
            # Start filtering with expanded tweet info
            self.filter(tweet_fields=['author_id', 'created_at', 'public_metrics'])
            
        except Exception as e:
            print(f"Error in Twitter stream setup: {e}. Switching to sample data.")
            self.use_sample_data = True
            self._start_sample_stream()

    def _start_sample_stream(self):
        """Start generating sample data"""
        def sample_stream():
            while self.running:
                try:
                    sample_tweet = self._generate_sample_tweet()
                    if self.analyzer:
                        sentiment = self.analyzer.analyze_sentiment(sample_tweet['text'])
                        trends = self.analyzer.analyze_trends(sample_tweet['text'])
                        sample_tweet.update({
                            'sentiment': sentiment,
                            'trends': trends
                        })
                    if self.database:
                        self.database.store(sample_tweet)
                    time.sleep(2)  # Generate a new tweet every 2 seconds
                except Exception as e:
                    print(f"Error in sample stream: {e}")
                    time.sleep(5)  # Wait longer on error

        import threading
        self.sample_thread = threading.Thread(target=sample_stream)
        self.sample_thread.daemon = True
        self.sample_thread.start()

    def stop(self):
        """Stop the stream"""
        self.running = False
        if not self.use_sample_data:
            self.disconnect() 