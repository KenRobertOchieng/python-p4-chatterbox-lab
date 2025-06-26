# app.py
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Message
import os

# Initialize the Flask app
app = Flask(__name__)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///chatterbox.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database and migrations
db.init_app(app)
migrate = Migrate(app, db)

# Define API routes
@app.route('/messages', methods=['GET'])
def get_messages():
    """Returns a list of all messages in the database as JSON."""
    messages = db.session.query(Message).all()
    messages_data = [msg.to_dict() for msg in messages]
    return jsonify(messages_data), 200

@app.route('/messages', methods=['POST'])
def create_message():
    """Creates a new message in the database from a JSON payload."""
    data = request.get_json()
    
    if not data or 'content' not in data or 'username' not in data:
        return jsonify({"error": "Missing 'content' or 'username' in request body"}), 400

    new_message = Message(
        content=data['content'],
        username=data['username']
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify(new_message.to_dict()), 201

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    """Updates the content of a message by its ID."""
    message = db.session.get(Message, id)
    
    if not message:
        return jsonify({"error": "Message not found"}), 404

    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"error": "Missing 'content' in request body"}), 400

    message.content = data['content']
    db.session.commit()
    
    return jsonify(message.to_dict()), 200

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    """Deletes a message by its ID."""
    message = db.session.get(Message, id)

    if not message:
        return jsonify({"error": "Message not found"}), 404

    db.session.delete(message)
    db.session.commit()
    
    return '', 204

if __name__ == '__main__':
    with app.app_context():
        # This is for running the app directly, not for tests.
        # Tests use the fixture in app_test.py to manage the database.
        db.create_all()
    app.run(port=5555, debug=True)