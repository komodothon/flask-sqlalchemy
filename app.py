from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from forms import RegisterForm, LoginForm, CreatePostForm
from db_models import db, User, Post


app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'app_secret_key'

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600


# Extensions
db.init_app(app) # initialising the db object
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


# create database tables
with app.app_context():
    db.create_all()


# routes 
@app.route("/")
def home():
    return render_template("home.html")


### User routes
@app.route("/register", methods=["GET","POST"])
def register():
    """Register a new user"""

    registerform = RegisterForm()

    if registerform.validate_on_submit():
        username = registerform.username.data
        email = registerform.email.data
        password = registerform.password.data
        password_hashed = bcrypt.generate_password_hash(password).decode('utf-8')

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash("User already exists!", "danger")
            return render_template("register.html", form=registerform)
        
        new_user = User(username=username, email=email, password=password_hashed)
        db.session.add(new_user)
        db.session.commit()
        flash("User added successfully!", "success")
        return redirect(url_for('login'))


    return render_template("register.html", form=registerform)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate an user"""
    
    loginform = LoginForm()

    if loginform.validate_on_submit():
        username = loginform.username.data
        password = loginform.password.data

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            # generate access token
            access_token = create_access_token(identity=str(user.id))

            # make response
            response = make_response(redirect(url_for('dashboard')))
            response.set_cookie('access_token_cookie', 
                                access_token, 
                                httponly=True, 
                                secure=False)

            return response

    return render_template("login.html", form=loginform)

@app.route("/dashboard")
@jwt_required(locations=["cookies"])
def dashboard():
    current_user_id = get_jwt_identity()
    return render_template("dashboard.html", user_id=current_user_id)


### Post routes
@app.route("/create_post", methods=["GET","POST"])
@jwt_required(locations=["cookies"])
def create_post():
    """Create a new post."""
    create_post_form = CreatePostForm()

    if create_post_form.validate_on_submit():
        title = create_post_form.title.data
        content = create_post_form.content.data
        
        current_user_id = get_jwt_identity()

        print(f"Title: {title}")
        print(f"Content: {content}")
        print(f"Current user id: {current_user_id}")


        new_post = Post(title=title, content=content, user_id=current_user_id)
        db.session.add(new_post)
        db.session.commit()

        flash("Post created successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template("create_post.html", form=create_post_form)


@app.route("/my_posts", methods=["GET"])
@jwt_required(locations=["cookies"])
def get_my_posts():
    """List all posts by the current user"""
    current_user_id = get_jwt_identity() # SQLA performing data type coercion when checking against the database.

    posts = Post.query.filter_by(user_id=current_user_id).all()
    post_list = [{'id': post.id, 'title': post.title, 'content': post.content}for post in posts]

    return render_template("my_posts.html", posts=post_list)

if __name__ == "__main__":
    app.run(debug=True)