from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'app_secret_key'
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600


# Extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


# define models
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    posts = db.relationship('Post', back_populates='author', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User (id:{self.id}, username:{self.username}, email:{self.email})>"
    

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    author = db.relationship('User', back_populates='posts')

    def __repr__(self):
        return f"<Post(id={self.id}, title={self.title}, author={self.user_id})>"
    

# create database tables
with app.app_context():
    db.create_all()


# routes 
@app.route("/")
def home():
    return "Flask-SQLAlchemy demo with JWT authentication."


### User routes
@app.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    password_hashed = bcrypt.generate_password_hash(password).decode('utf-8')

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists!'}), 400
    
    new_user = User(username=username, email=email, password=password_hashed)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@app.route("/login", methods=["POST"])
def login():
    """Authenticate an user"""

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username and password:
        user = User.query.filter_by(username=username).first()
    
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=str(user.id)) # passing 'int' type in jwt results in a 'sub must be string' message. 
        return jsonify({'message': 'Login successful', 'access_token': access_token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401


### Post routes
@app.route("/create_post", methods=["POST"])
@jwt_required()
def create_post():
    """Create a new post."""

    current_user_id = get_jwt_identity() # SQLA performing data type coercion when checking against the database.

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    new_post = Post(title=title, content=content, user_id=current_user_id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({'message': 'Post created successfully', 'post': {'title': title, 'content': content}}), 201

@app.route("/my_posts", methods=["GET"])
@jwt_required()
def get_my_posts():
    """List all posts by the current user"""
    current_user_id = get_jwt_identity() # SQLA performing data type coercion when checking against the database.

    posts = Post.query.filter_by(user_id=current_user_id).all()
    post_list = [{'id': post.id, 'title': post.title, 'content': post.content}for post in posts]

    return jsonify({'posts': post_list}), 200

if __name__ == "__main__":
    app.run(debug=True)