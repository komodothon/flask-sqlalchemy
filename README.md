# flask-sqlalchemy
Flask-SQLAlchem implementation within a flask web app and managing a SQLite database

Postman VSCode extension used to test the APIs.

In this version, apart from the basics, the functionality involves association of three models in a one-to-many (Users to Posts), many-to-many (Posts to likes) relationship.

A multi-model, relational database with features to manage users, their posts, and commenting and likes system. Providing API to interect with the data, allowing create and read operations (not update/delete) on users, posts and tags.

Session management is implemented using session object from Flask.

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
  -  `relationship`: with `Post` model with `User` as author. One-To-Many relationship with post. => One user can author many different posts.

- `Post` model defined for posts table in the database with the following columns:
  - `id`: Primary key, integer.
  - `title`: String, unique, non-nullable.
  - `content`: Text, unique, non-nullable.
  -  `relationship`: with `User` model with `Post` as a post. One post can be authored only one `User`.
  -  `relationship`: with `Tag` model with `Tag` as a tag. One post can have many tags. Association is secondary as described by the Association Table.

- `Comment` model defined for a comments table in the database with the following columns:
  - `id`: Primary key, integer.
  - `content`: String, unique, non-nullable.
  -  `user_id`: id of the commenting user as foreign key.
    - `post_id`: related post for this comment, as foreign key.

- Association table `likes` added in the database with the following columns:
  -  `user_id`: id of the commenting user as foreign key.
    - `post_id`: related post for this comment, as foreign key.

- Database tables are created using `db.create_all()` within the application context.

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
  - Accepts JSON data to add a new post with `title`, `content` and utilises user detail from `session` to be author of the post.
  - Inserts the new post into the database and commits the transaction.

#### - **like a post (`/posts/<int:post_id>/like`, POST)**
  - Accepts JSON data to like a post.
  - Inserts the new like into the database association table and commits the transaction.

#### - **Add comment (`/posts/<int:post_id>/comments`, POST)**
  - Accepts JSON data to add a new comment with `content`.
  - retrieves detail of commenting user from `session`.
  - Inserts the new comment into the database and commits the transaction.

#### - **Get All Posts (`/posts`, GET)**
  - Retrieves all posts from the database.
  - Returns a JSON response containing a list of all posts.

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
