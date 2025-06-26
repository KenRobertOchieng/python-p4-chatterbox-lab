# testing/models_test.py
# Assuming this file exists and contains the TestMessage class

import pytest
from app import app # Needed for app_context
from models import db, Message

class TestMessage:
    @pytest.fixture(autouse=True)
    def setup_app_context(self):
        with app.app_context():
            # Ensure a clean database for each test run in this file too
            db.drop_all()
            db.create_all()
            db.session.commit()
            yield
            db.session.remove()

    def test_has_correct_columns(self):
        """Tests that a Message instance has the expected content and username attributes
           and that its __repr__ method returns the expected string format."""
        with app.app_context():
            # FIX: Change 'body' to 'content' here when creating the Message object
            hello_from_liza = Message(
                content="Hello 👋", # This was 'body' before
                username="Liza"
            )
            db.session.add(hello_from_liza)
            db.session.commit()
            
            retrieved_message = db.session.get(Message, hello_from_liza.id)
            
            assert retrieved_message.content == "Hello 👋"
            assert retrieved_message.username == "Liza"
            
            assert repr(retrieved_message) == f'<Message {retrieved_message.id}: {retrieved_message.username} - {retrieved_message.content}>'

    # Add any other tests related to the Message model herex