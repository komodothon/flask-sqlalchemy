from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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