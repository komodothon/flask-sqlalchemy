from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'app_secret_key'


# Extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# Flask-Login setup
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'info'

# Many-To-Many: Users like Postss (Association table)
likes = db.Table(
    'likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True)
)


# define models
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    posts = db.relationship('Post', back_populates='author', cascade='all, delete-orphan')
    # comments = db.relationship('Comment', back_populates='author', cascade='all,delete-orphan')
    # liked_posts = db.relationship('Post', secondary=likes, back_populates='likers')

    def __repr__(self):
        return f"<User (id:{self.id}, username:{self.username}, email:{self.email})>"
    

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    author = db.relationship('User', back_populates='posts')
    # comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')
    # likers = db.relationship('User', secondary=likes, back_populates='liked_posts')

    def __repr__(self):
        return f"<Post(id={self.id}, title={self.title}, author={self.user_id})>"
    

# class Comment(db.Model):
#     __tablename__ = 'comments'

#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.Text, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

#     author = db.relationship('User', back_populates='comments')
#     post = db.relationship('Post', back_populates='comments')

#     def __repr__(self):
#         return f"<Comment(id={self.id}, post_id={self.post_id}, user_id={self.user_id})>"


# create database tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


# routes 
@app.route("/")
def home():
    return "Flask-SQLAlchemy demo. Flask-Login implementation."

### User routes

@app.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    password_hashed = bcrypt.generate_password_hash(password).decode('UTF-8')

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
        login_user(user)
        return jsonify({'message': f'Login successful for {user.username}'}), 200

    return jsonify({'message': 'Invalid credentials'}), 401


@app.route("/logout", methods=["POST"])
def logout():
    """Logout the user by clearing session."""
    logout_user()
    return jsonify({'message': 'Logged out'}), 200


### Post routes
@app.route("/create_post", methods=["POST"])
@login_required
def create_post():
    """Create a new post."""

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    user_id = current_user.id

    new_post = Post(title=title, content=content, user_id=user_id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({'message': 'Post created successfully', 'post': {'title': title, 'content': content}}), 201

@app.route("/my_posts", methods=["GET"])
@login_required
def get_my_posts():
    """List all posts by the current user"""

    posts = Post.query.filter_by(user_id=current_user.id).all()
    post_list = [{'id': post.id, 'title': post.title, 'content': post.content}for post in posts]

    return jsonify({'posts': post_list})

if __name__ == "__main__":
    app.run(debug=True)