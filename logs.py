import os
import sqlite3
from datetime import datetime
from flask import g

class ActivityLogger:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # Ensure the logs directory exists
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Create logs database if it doesn't exist
        with app.app_context():
            self._init_db()

    def _get_db(self):
        if 'logs_db' not in g:
            g.logs_db = sqlite3.connect('logs/activity_logs.db')
            g.logs_db.row_factory = sqlite3.Row
        return g.logs_db

    def _close_db(self, e=None):
        db = g.pop('logs_db', None)
        if db is not None:
            db.close()

    def _init_db(self):
        db = self._get_db()
        cursor = db.cursor()
        
        # Create activity logs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            user_id INTEGER,
            username TEXT,
            ip_address TEXT,
            user_agent TEXT,
            activity_type TEXT NOT NULL,
            details TEXT,
            status TEXT,
            additional_info TEXT
        )
        ''')
        
        # Create login attempts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            username TEXT,
            ip_address TEXT,
            user_agent TEXT,
            status TEXT NOT NULL,
            details TEXT
        )
        ''')
        
        db.commit()

    def log_activity(self, activity_type, details, status='success', user_id=None, username=None, request=None, additional_info=None):
        """Log general user activities"""
        try:
            db = self._get_db()
            cursor = db.cursor()
            
            ip_address = request.remote_addr if request else None
            user_agent = request.headers.get('User-Agent') if request else None
            
            cursor.execute('''
            INSERT INTO activity_logs (
                timestamp, user_id, username, ip_address, user_agent, 
                activity_type, details, status, additional_info
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.utcnow(),
                user_id,
                username,
                ip_address,
                user_agent,
                activity_type,
                details,
                status,
                str(additional_info) if additional_info else None
            ))
            
            db.commit()
        except Exception as e:
            if self.app:
                self.app.logger.error(f"Failed to log activity: {str(e)}")

    def log_login_attempt(self, username, status, request, details=None):
        """Log user login attempts"""
        try:
            db = self._get_db()
            cursor = db.cursor()
            
            ip_address = request.remote_addr if request else None
            user_agent = request.headers.get('User-Agent') if request else None
            
            cursor.execute('''
            INSERT INTO login_attempts (
                timestamp, username, ip_address, user_agent, status, details
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.utcnow(),
                username,
                ip_address,
                user_agent,
                status,
                details
            ))
            
            db.commit()
        except Exception as e:
            if self.app:
                self.app.logger.error(f"Failed to log login attempt: {str(e)}")

    def get_activity_logs(self, limit=100):
        """Retrieve recent activity logs"""
        try:
            db = self._get_db()
            cursor = db.cursor()
            cursor.execute('''
            SELECT * FROM activity_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
        except Exception as e:
            if self.app:
                self.app.logger.error(f"Failed to get activity logs: {str(e)}")
            return []

    def get_login_attempts(self, limit=100):
        """Retrieve recent login attempts"""
        try:
            db = self._get_db()
            cursor = db.cursor()
            cursor.execute('''
            SELECT * FROM login_attempts 
            ORDER BY timestamp DESC 
            LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
        except Exception as e:
            if self.app:
                self.app.logger.error(f"Failed to get login attempts: {str(e)}")
            return []

# Initialize the logger
activity_logger = ActivityLogger()