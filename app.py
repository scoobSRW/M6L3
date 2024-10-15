from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from mysql.connector import Error
from password import my_password

# Initialize Flask app, SQLAlchemy and Marshmallow
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/Fitness_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


# Define the Members model
class Member(db.Model):
    __tablename__ = 'Members'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)


# Define the WorkoutSessions model
class WorkoutSession(db.Model):
    __tablename__ = 'WorkoutSessions'

    session_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.Time, nullable=False)
    activity = db.Column(db.String(100), nullable=False)

    # Define relationship
    member = db.relationship('Member', backref='workout_sessions', lazy=True)


# Create schemas for serialization
class MemberSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Member


class WorkoutSessionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WorkoutSession


# Initialize schemas
member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
workout_session_schema = WorkoutSessionSchema()
workout_sessions_schema = WorkoutSessionSchema(many=True)


# Welcome page route
@app.route('/', methods=['GET'])
def welcome():
    return "<h1>Welcome to Fitness Database</h1>"


# Task 1: CRUD operations for Members
@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    new_member = Member(name=data['name'], age=data['age'])

    db.session.add(new_member)
    db.session.commit()

    return member_schema.jsonify(new_member), 201


@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    member = Member.query.get(id)
    if member:
        return member_schema.jsonify(member)
    else:
        return jsonify({"error": "Member not found"}), 404


@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get(id)
    if not member:
        return jsonify({"error": "Member not found"}), 404

    data = request.get_json()
    member.name = data.get('name', member.name)
    member.age = data.get('age', member.age)

    db.session.commit()
    return member_schema.jsonify(member)


@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get(id)
    if not member:
        return jsonify({"error": "Member not found"}), 404

    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member deleted successfully!"})


# Task 3: CRUD operations for Workout Sessions
@app.route('/workout_sessions', methods=['POST'])
def add_workout_session():
    data = request.get_json()
    new_session = WorkoutSession(
        member_id=data['member_id'],
        session_date=data['session_date'],
        session_time=data['session_time'],
        activity=data['activity']
    )

    db.session.add(new_session)
    db.session.commit()
    return workout_session_schema.jsonify(new_session), 201


@app.route('/workout_sessions/member/<int:member_id>', methods=['GET'])
def get_workouts_for_member(member_id):
    sessions = WorkoutSession.query.filter_by(member_id=member_id).all()
    if sessions:
        return workout_sessions_schema.jsonify(sessions)
    else:
        return jsonify({"error": "No workout sessions found for this member"}), 404


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables
    app.run(debug=True)
