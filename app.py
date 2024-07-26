from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(256), nullable=False)
    answer = db.Column(db.String(256), nullable=False)
    interval = db.Column(db.Integer, default=1)
    next_review = db.Column(db.Date, default=datetime.date.today)

# Initialize database
with app.app_context():
    db.create_all()

# Routes
@app.route('/add_card', methods=['POST'])
def add_card():
    data = request.json
    question = data.get('question')
    answer = data.get('answer')

    if not question or not answer:
        return jsonify({"error": "Question and answer are required"}), 400

    new_card = Card(question=question, answer=answer)
    db.session.add(new_card)
    db.session.commit()

    return jsonify({"message": "Card added successfully"}), 201

@app.route('/cards', methods=['GET'])
def get_cards():
    cards = Card.query.all()
    cards_list = [{"id": card.id, "question": card.question, "answer": card.answer, "interval": card.interval, "next_review": card.next_review.isoformat()} for card in cards]
    return jsonify(cards_list)

@app.route('/review', methods=['GET'])
def review():
    today = datetime.date.today()
    card = Card.query.filter(Card.next_review <= today).first()
    if card:
        return render_template('index.html', question=card.question, answer=card.answer, card_id=card.id)
    else:
        return "No cards due for review."

@app.route('/update_review/<int:card_id>', methods=['POST'])
def update_review(card_id):
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    data = request.json
    success = data.get('success')

    if success:
        card.interval = card.interval * 2
    else:
        card.interval = 1

    card.next_review = datetime.date.today() + datetime.timedelta(days=card.interval)
    db.session.commit()

    return jsonify({"message": "Review updated successfully"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
