from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt



app = Flask(__name__)


# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'app_secret_key'


# Extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Many-To-Many: Users like Postss (Association table)
likes = db.Table(
    'likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True)
)


# define models
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    posts = db.relationship('Post', back_populates='author', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='author', cascade='all,delete-orphan')
    liked_posts = db.relationship('Post', secondary=likes, back_populates='likers')

    def __repr__(self):
        return f"<User (id:{self.id}, username:{self.username}, email:{self.email})>"
    

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    author = db.relationship('User', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')
    likers = db.relationship('User', secondary=likes, back_populates='liked_posts')

    def __repr__(self):
        return f"<Post(id={self.id}, title={self.title}, author={self.user_id})>"
    

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

    author = db.relationship('User', back_populates='comments')
    post = db.relationship('Post', back_populates='comments')

    def __repr__(self):
        return f"<Comment(id={self.id}, post_id={self.post_id}, user_id={self.user_id})>"


# create database tables
with app.app_context():
    db.create_all()

# routes 
@app.route("/")
def home():
    return "Flask-SQLAlchemy demo. Blog with users, posts and comments"

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
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({'message': f'Login successful for {session['username']}'}), 200

    return jsonify({'message': 'Invalid credentials'}), 401


### Post routes
@app.route("/posts", methods=["POST"])
def create_post():
    """Create a new post."""
    if 'user_id' not in session:
        return jsonify({'message': 'Login required'}), 401

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    user_id = session['user_id']

    new_post = Post(title=title, content=content, user_id=user_id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({'message': 'Post created successfully', 'post': {'title': title, 'content': content}}), 201

@app.route("/posts/<int:post_id>/like", methods=["POST"])
def like_post(post_id):
    """Like or unlike a post."""

    if 'user_id' not in session:
        return jsonify({'message': 'Login required'}), 401

    user_id = session['user_id']

    user = User.query.get(user_id)
    post = Post.query.get(post_id)

    if not post:
        return jsonify({'message': "Post not found"}), 404
    
    if post in user.liked_posts:
        user.liked_posts.remove(post)
        action = 'unliked'
    else:
        user.liked_posts.append(post)
        action = 'liked'

    db.session.commit()
    return jsonify({'message': f'Post {action} successfully'})


@app.route("/posts/<int:post_id>/comments", methods=["POST"])
def add_comment(post_id):
    """Add a comment to a post."""

    if 'user_id' not in session:
        return jsonify({'message': 'Login required'}), 401
    
    data = request.get_json()
    content = data.get('content')
    
    user_id = session['user_id']

    post = Post.query.get(post_id)

    if not post:
        return jsonify({'message': 'Post not found'}), 404
    
    new_comment = Comment(content=content, user_id=user_id, post_id=post_id)
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({'message': 'Comment added successfully'}), 201


@app.route("/posts", methods=["GET"])
def get_posts():
    """List of all posts with comments and likes."""
    posts = Post.query.all()
    post_list = []

    for post in posts:
        post_info = {
            'id': post.id,
            'title' : post.title,
            'content' : post.content,
            'author' : post.author.username,
            'likes' : len(post.likers),
            'comments' : [{'content': comment.content, 'author': comment.author.username} for comment in post.comments]
        }
        post_list.append(post_info)
    
    return jsonify({'posts': post_list})

@app.route("/logout", methods=["POST"])
def logout():
    """Logout the user by clearing session."""
    session.clear()
    return jsonify({'message': 'Logged out'}), 200

if __name__ == "__main__":
    app.run(debug=True)