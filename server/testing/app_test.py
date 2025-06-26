# testing/app_test.py

import pytest
from app import app
from models import db, Message

class TestApp:

    @pytest.fixture(autouse=True)
    def setup_app_context(self):
        with app.app_context():
            # Ensure a clean database for each test run:
            db.drop_all()
            db.create_all()
            db.session.commit()

            yield # Allows the test to run

            # Clean up after each test:
            db.session.remove()

    def test_has_correct_columns(self):
        """Tests that a Message instance has the expected content and username attributes."""
        with app.app_context():
            hello_from_liza = Message(
                content="Hello 👋",
                username="Liza"
            )
            
            db.session.add(hello_from_liza)
            db.session.commit()

            assert hello_from_liza.content == "Hello 👋"
            assert hello_from_liza.username == "Liza"

    def test_returns_list_of_json_objects_for_all_messages_in_database(self):
        """Tests the GET /messages endpoint returns a list of messages as JSON."""
        with app.app_context():
            db.session.add_all([
                Message(content="Hello from Liza", username="Liza"),
                Message(content="Hi brother", username="Duane")
            ])
            db.session.commit()

            response = app.test_client().get('/messages')
            assert response.status_code == 200
            assert response.content_type == 'application/json'

            records = db.session.query(Message).all()
            response_json = response.json

            assert isinstance(response_json, list)
            assert len(response_json) == len(records)

            for message_data in response_json:
                assert 'id' in message_data
                assert 'content' in message_data
                assert 'username' in message_data

                matching_record = next((r for r in records if r.id == message_data['id']), None)
                assert matching_record is not None
                assert message_data['content'] == matching_record.content
                assert message_data['username'] == matching_record.username


    def test_creates_new_message_in_the_database(self):
        """Tests the POST /messages endpoint creates a new message in the database."""
        with app.app_context():
            initial_message_count = db.session.query(Message).count()

            app.test_client().post(
                '/messages',
                json={
                    "content":"Hello 👋",
                    "username":"Liza",
                }
            )

            assert db.session.query(Message).count() == initial_message_count + 1
            
            h = db.session.query(Message).filter_by(content="Hello 👋").first()
            assert h is not None


    def test_returns_data_for_newly_created_message_as_json(self):
        """Tests the POST /messages endpoint returns the newly created message as JSON."""
        with app.app_context():
            response = app.test_client().post(
                '/messages',
                json={
                    "content":"Hello 👋",
                    "username":"Liza",
                }
            )

            assert response.status_code == 201
            assert response.content_type == 'application/json'

            response_data = response.json
            assert response_data["content"] == "Hello 👋"
            assert response_data["username"] == "Liza"
            assert "id" in response_data


    def test_updates_content_of_message_in_database(self):
        """Tests the PATCH /messages/<id> endpoint updates the message content in the database."""
        with app.app_context():
            m = Message(content="Original Content", username="TestUser")
            db.session.add(m)
            db.session.commit()
            
            message_id = m.id

            app.test_client().patch(
                f'/messages/{message_id}',
                json={
                    "content":"Goodbye 👋",
                }
            )

            updated_message = db.session.get(Message, message_id)
            assert updated_message is not None
            assert updated_message.content == "Goodbye 👋"


    def test_returns_data_for_updated_message_as_json(self):
        """Tests the PATCH /messages/<id> endpoint returns the updated message as JSON."""
        with app.app_context():
            m = Message(content="Original Content", username="TestUser")
            db.session.add(m)
            db.session.commit()
            
            message_id = m.id

            response = app.test_client().patch(
                f'/messages/{message_id}',
                json={
                    "content":"Goodbye 👋",
                }
            )

            assert response.status_code == 200
            assert response.content_type == 'application/json'
            response_data = response.json
            assert response_data["content"] == "Goodbye 👋"
            assert response_data["username"] == "TestUser"


    def test_deletes_message_from_database(self):
        """Tests the DELETE /messages/<id> endpoint deletes the message from the database."""
        with app.app_context():
            hello_from_liza = Message(
                content="Hello 👋",
                username="Liza")
            
            db.session.add(hello_from_liza)
            db.session.commit()

            initial_count = db.session.query(Message).count()

            response = app.test_client().delete(
                f'/messages/{hello_from_liza.id}'
            )

            assert response.status_code == 204
            assert db.session.query(Message).count() == initial_count - 1
            
            deleted_message = db.session.get(Message, hello_from_liza.id)
            assert deleted_message is None