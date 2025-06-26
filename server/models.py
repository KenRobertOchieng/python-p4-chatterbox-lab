# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Message(db.Model):
    """A model representing a message in the database."""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Converts the Message object to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'content': self.content,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        """Provides a string representation of the Message object for debugging/testing."""
        # This format matches the expectation in your models_test.py
        return f"<Message {self.id}: {self.username} - {self.content}>"