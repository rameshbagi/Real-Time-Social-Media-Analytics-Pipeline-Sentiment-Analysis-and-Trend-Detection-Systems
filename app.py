from flask import Flask, render_template_string
import os
import threading
import logging
from ingestion.stream_listener import StreamListener
from processing.analyzer import Analyzer
from storage.database import Database
from visualization.dashboard import Dashboard
from config import config
from utils.helpers import ensure_directory_exists

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global dashboard instance
dashboard = None
dashboard_thread = None

def create_app():
    """Create and configure the Flask application"""
    try:
        global dashboard, dashboard_thread
        
        # Initialize Flask app
        app = Flask(__name__)
        
        # Ensure all required directories exist
        ensure_directory_exists('src/storage/data')
        ensure_directory_exists('src/visualization/static')
        ensure_directory_exists('src/visualization/templates')
        
        # Initialize components
        database = Database()
        analyzer = Analyzer()
        dashboard = Dashboard(analyzer)
        
        # Initialize stream listener with components
        stream_listener = StreamListener(
            api=config.twitter_config,
            analyzer=analyzer,
            database=database
        )
        
        @app.route('/')
        def index():
            """Render the main page with links to the dashboard"""
            return render_template_string('''
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>Real-Time Social Media Analytics Pipeline</title>
                        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                        <style>
                            body { padding: 20px; }
                            .container { max-width: 800px; }
                            .btn { margin: 10px; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1 class="text-center mb-4">Real-Time Social Media Analytics Pipeline</h1>
                            <div class="text-center">
                                <p class="lead">
                                    Welcome to the Real-Time Social Media Analytics Dashboard.
                                    This application provides real-time analysis of social media data,
                                    including sentiment analysis and trend detection.
                                </p>
                                <a href="/dashboard" class="btn btn-primary btn-lg">Launch Dashboard</a>
                            </div>
                        </div>
                    </body>
                </html>
            ''')
        
        @app.route('/dashboard')
        def dashboard_view():
            """Start the dashboard on a separate port and provide a link"""
            global dashboard_thread
            
            if dashboard_thread is None or not dashboard_thread.is_alive():
                def run_dashboard():
                    try:
                        # Use 127.0.0.1 to allow only local connections
                        dashboard.run(debug=False, port=config.DASH_PORT, host='127.0.0.1')
                    except Exception as e:
                        logger.error(f"Error starting dashboard: {e}")
                
                # Start dashboard in a separate thread
                dashboard_thread = threading.Thread(target=run_dashboard)
                dashboard_thread.daemon = True
                dashboard_thread.start()
                logger.info(f"Starting dashboard on port {config.DASH_PORT}")
            
            return render_template_string(f'''
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>Dashboard - Real-Time Social Media Analytics</title>
                        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                        <style>
                            body {{ padding: 20px; }}
                            .container {{ max-width: 800px; }}
                        </style>
                       <meta http-equiv="refresh" content="2;url=http://localhost:8051">
                    </head>
                    <body>
                        <div class="container text-center">
                            <h2>Dashboard is starting...</h2>
                            <p>You will be redirected to the dashboard in a moment.</p>
                            <p>If you are not redirected, try this URL:</p>
                            <ul class="list-unstyled">
                           <li><a href="http://localhost:8051">http://localhost:8051</a></li>    
                            </ul>
                        </div>
                    </body>
                </html>
            ''')
        
        return app, stream_listener
        
    except Exception as e:
        logger.error(f"Error creating application: {e}")
        raise

def start_pipeline(stream_listener):
    """Start the data ingestion pipeline"""
    try:
        # Start streaming with default keywords
        stream_listener.start(track_keywords=config.DEFAULT_KEYWORDS)
        logger.info("Stream listener started successfully")
    except Exception as e:
        logger.error(f"Error starting stream listener: {e}")
        raise

if __name__ == '__main__':
    try:
        # Create the application
        app, stream_listener = create_app()
        
        # Start the pipeline in a separate thread
        pipeline_thread = threading.Thread(target=lambda: start_pipeline(stream_listener))
        pipeline_thread.daemon = True
        pipeline_thread.start()
        
        # Start the Flask application
        logger.info(f"Starting Flask application on port {config.FLASK_PORT}")
        app.run(debug=config.DEBUG, port=config.FLASK_PORT, host='127.0.0.1')
        
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        raise 