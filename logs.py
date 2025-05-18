import os
from datetime import datetime
from flask import request

class ActivityLogger:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # Ensure the logs directory exists
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Create logs file if it doesn't exist
        self.log_file = 'logs/logs.txt'
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write('Timestamp,Activity Type,Status,Username,User ID,IP Address,User Agent,Details\n')

    def _write_log(self, log_entry):
        try:
            with open(self.log_file, 'a') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            if self.app:
                self.app.logger.error(f"Failed to write to log file: {str(e)}")

    def log_activity(self, activity_type, details, status='success', user_id=None, username=None, request=None, additional_info=None):
        """Log general user activities"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ip_address = request.remote_addr if request else 'N/A'
        user_agent = request.headers.get('User-Agent') if request else 'N/A'
        
        log_entry = (
            f"{timestamp},{activity_type},{status},"
            f"{username or 'N/A'},{user_id or 'N/A'},"
            f"{ip_address},{user_agent.replace(',', ';') if user_agent else 'N/A'},"
            f"{details.replace(',', ';') if details else 'N/A'}"
        )
        
        if additional_info:
            log_entry += f",{str(additional_info).replace(',', ';')}"
        
        self._write_log(log_entry)

    def log_login_attempt(self, username, status, request, details=None):
        """Log user login attempts"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ip_address = request.remote_addr if request else 'N/A'
        user_agent = request.headers.get('User-Agent') if request else 'N/A'
        
        log_entry = (
            f"{timestamp},login_attempt,{status},"
            f"{username or 'N/A'},N/A,"
            f"{ip_address},{user_agent.replace(',', ';') if user_agent else 'N/A'},"
            f"{details.replace(',', ';') if details else 'N/A'}"
        )
        
        self._write_log(log_entry)

    def get_activity_logs(self, limit=100):
        """Retrieve recent activity logs"""
        try:
            with open(self.log_file, 'r') as f:
                # Skip header line
                lines = f.readlines()[1:]
                return lines[-limit:] if limit else lines
        except Exception as e:
            if self.app:
                self.app.logger.error(f"Failed to read log file: {str(e)}")
            return []

# Initialize the logger
activity_logger = ActivityLogger()