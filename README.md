# flask-sqlalchemy
Flask-SQLAlchemy implementation within a flask web app and managing a SQLite database

Postman application used to test the APIs routes and endpoints.

In this version, apart from the basics, the functionality involves association of two models (User and Post).

A multi-model, relational database with features to manage users and their posts. Providing API to interect with the data, allowing create and read operations (not update/delete) on users, posts and tags.

~~Session management is implemented using session object from Flask.~~

~~Flask-Login library and it's elements are implemented for user management, user authentication and user session management.~~

JWT tokens used for user authorisation (Flask-JWT-Extended library). 

---

## Features and Components
---

### 1. **App Configuration**
- The app is configured to use **SQLite** as its database via the URI `sqlite:///blog.db`.
---

### 2. **Database Setup**
- **SQLAlchemy** is initialized with `Flask` app instance.
- `User` model defined for a users table in the database with the following columns:
  - `id`: Primary key, integer.
  - `username`: String, unique, non-nullable.
  - `email`: String, unique, non-nullable.
  -  `relationship`: with `Post` model with `User` as author. One-To-Many relationship with post. One user can author many different posts.

- `Post` model defined for posts table in the database with the following columns:
  - `id`: Primary key, integer.
  - `title`: String, unique, non-nullable.
  - `content`: Text, unique, non-nullable.
  -  `relationship`: with `User` model with `Post` as a post. One post can be authored only one `User`.
  - ~~`relationship`: with `Tag` model with `Tag` as a tag. One post can have many tags. Association is secondary as described by the Association Table.~~

- ~~`Comment` model defined for a comments table in the database with the following columns:~~
  - ~~`id`: Primary key, integer.~~
  - ~~`content`: String, unique, non-nullable.~~
  -  ~~`user_id`: id of the commenting user as foreign key.~~
  - ~~`post_id`: related post for this comment, as foreign key.~~

- ~~Association table `likes` added in the database with the following columns:~~
~~  -  `user_id`: id of the commenting user as foreign key.~~
~~    - `post_id`: related post for this comment, as foreign key.~~
~~- Database tables are created using `db.create_all()` within the application context.~~
---

### 3. **Routes**
#### - **Home Page (`/`)**
  - A simple route that returns a plain text message for demonstration.

#### - **Register (`/register`, POST)**
  - Accepts JSON data to register a new user with `username`,  `email` and `password`.
  - Checks for duplicate usernames.
  - secures the password by hashing using bcrypt hash.
  - Inserts the new user into the database and commits the transaction.

#### - **Login (`/login`, POST)**
  - Logs a user in.
  - initiates a session for that user.

#### - **Create Post (`/posts`, POST)**
  - `@jwt_required()` decorator ensures that a valid token is required to access post-related routes. `get_jwt_identity()` function retrieves current user's identity from the JWT token.
  - Accepts JSON data to add a new post with `title`, `content` and utilises user detail from `session` to be author of the post.
  - Inserts the new post into the database and commits the transaction.

#### - **Get All Posts (`/posts`, GET)**
  - `@jwt_required()` decorator ensures that a valid token is required to access post-related routes. `get_jwt_identity()` function retrieves current user's dentity from the JWT token.
  - Retrieves all posts from the database by current user.
  - Returns a JSON response containing a list of all posts.

---
### Learnings
  - `access_token = create_access_token(identity=(user.id))`. Integer object was introduced as 'sub' or subject in jwt token which was not accepted and resulted in response below. Hence, string conversion was effected as `access_token = create_access_token(identity=str(user.id))`
  
  ```json 
    {"msg": "Subject must be a string"}
  ``` 

  - Expected that when assigning `current_user_id = get_jwt_identity()`, may need to convert back to Integer. But not needed to. 
  - Reason: assuming that SQLAlchemy does the data type coercion of the String object into Integer automatically. To be reviewed.

---
## Example Usage
**Testing the APIs using Postman app**


### 1. **POST Request to `/register`**
Add a user with a JSON payload:
```json
{
  "username": "john_doe",
  "email": "john.doe@example.com",
  "password": "Hellojohn"
}
```

### 2. **GET Request to `/my_posts`**
Requires a valid JWT token in the Authorization header.:
`Authorization: Bearer <your_jwt_token>`
