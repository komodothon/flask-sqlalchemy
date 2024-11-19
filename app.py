from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Config SQLA database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///complex_demo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Association table
post_tags = db.Table(
    'post_tags', 
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


# define model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    posts = db.relationship('Post', back_populates='author', cascade='all, delete')

    def __repr__(self):
        return f"<User (id:{self.id}, username:{self.username}, email:{self.email})>"
    

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    author = db.relationship('User', back_populates='posts')
    tags = db.relationship('Tag', secondary=post_tags, back_populates='posts')

    def __repr__(self):
        return f"<Post(id={self.id}, title={self.title})>"
    

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    posts = db.relationship('Post', secondary=post_tags, back_populates='tags')

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})"


# create database tables
with app.app_context():
    db.create_all()

# routes 
@app.route("/")
def home():
    return "Flask-SQLAlchemy slightly complex demo"

### User routes

@app.route("/users", methods=["POST"])
def add_user():
    """Add a new user."""

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({'error': 'Username or email is missing'}), 400

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
    print(users)
    print(f'datatype of users: {type(users)}')
    user_list = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
    return jsonify({'users': user_list})


### Posts routes

@app.route("/posts", methods=["POST"])
def add_post():
    """Creates a new post"""

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    user_id = data.get('user_id')

    if not title or not content or not user_id:
        return jsonify({'error': 'Invalid/missing credentials'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'user not found'}), 404
    
    new_post = Post(title=title, content=content, author=user)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({'message': 'Post created', 'post': {'title': title, 'content': content}})
    
@app.route("/posts", methods = ["GET"])
def get_posts():
    """Get all posts."""

    posts = Post.query.all()
    post_list = [{'id': post.id, 'title': post.title, 'author': post.author.username} for post in posts]
    return jsonify({'posts': post_list})


### Tag routes
@app.route("/tags", methods=["POST"])
def add_tag():
    """Create new tag"""
    tag_data = request.get_json()
    name = tag_data.get('name')

    if not name:
        return jsonify({'error': 'missing tag name'}), 400
    
    if Tag.query.filter_by(name=name).first():
        return jsonify({'error': 'Tag name already exists'}), 400
    
    new_tag = Tag(name=name)
    db.session.add(new_tag)
    db.session.commit()

    return jsonify({'message': 'New tag added', 'tag': {'name':name}})

@app.route("/tags", methods=["GET"])
def get_tags():
    tags = Tag.query.all()
    tag_list = [{'id': tag.id, 'name': tag.name} for tag in tags]
    return jsonify({'tags': tag_list})


### Add tags to posts
@app.route("/posts/<int:post_id>/tags", methods=["POST"])
def add_tag_to_post(post_id):
    """Add (a) tag(s) to post."""
    data = request.get_json()
    tag_name = data.get('tag')

    if not tag_name:
        return jsonify({'error': 'No tag name'}), 400
    
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    tag = Tag.query.filter_by(name=tag_name).first()
    if not tag:
        return jsonify({'error': 'Tag not found'}), 404
    
    post.tags.append(tag)
    db.session.commit()

    return jsonify({'message': 'Tag added to post',
                    'post': post.title,
                    'tag': tag.name})



if __name__ == "__main__":
    app.run(debug=True)