from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Config SQLA database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# define model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<User (id:{self.id}, username:{self.username}, email:{self.email})>"
    
# create database tables
with app.app_context():
    db.create_all()
    print(app.instance_path)

# routes 
@app.route("/")
def home():
    return "Home page for Flask-SQLAlchemy demo"

@app.route("/users", methods=["POST"])
def add_user():
    """Add a new user."""

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists!'}), 400
    
    new_user = User(username=username, email=email) 
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User added successfully', 'user':{'username': username, 'email': email}})

@app.route("/users", methods=["GET"])
def get_users():
    """Retrieve all users."""
    users = User.query.all()
    user_list = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
    return jsonify({'users': user_list})

if __name__ == "__main__":
    app.run(debug=True)