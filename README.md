# flask-sqlalchemy
Flask-SQLAlchem implementation within a flask web app and managing a SQLite database

Postman VSCode extension used to test the APIs.

In this version, apart from the basics, the functionality involves association of three elements in a one-to-many (Users to Posts), many-to-many (Posts to Tags) relationship.

A multi-model, relational database with features to manage users, their posts, and a tagging system. Providing API to interect with the data, allowing create and read operations (not update/delete) on users, posts and tags.

---

## Features and Components
---

### 1. **App Configuration**
- The app is configured to use **SQLite** as its database via the URI `sqlite:///example.db`.
- `SQLALCHEMY_TRACK_MODIFICATIONS` is disabled for performance optimization.

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

- `Tag` model defined for a tags table in the database with the following columns:
  - `id`: Primary key, integer.
  - `name`: String, unique, non-nullable.
  -  `relationship`: with `Post` model. One `Tag` can be applied to many different `Post` elements. Similarly, one `Post` can have many different `Tag`s

- Association table `post_tags` added in the database with the following columns:
  - `post_id`: Primary key, integer, is a ForeignKey from ('posts.id').
  - `tag_id`: Primary key, integer, is a ForeignKey from ('tags.id').
  - Each association of a tag to a post is a separate row in this table.

- Database tables are created using `db.create_all()` within the application context.

---

### 3. **Routes**
#### - **Home Page (`/`)**
  - A simple route that returns a plain text message for demonstration.

#### - **Add User (`/users`, POST)**
  - Accepts JSON data to add a new user with `username` and `email`.
  - Checks for duplicate usernames.
  - Inserts the new user into the database and commits the transaction.

#### - **Get All Users (`/users`, GET)**
  - Retrieves all users from the database.
  - Returns a JSON response containing a list of all users.

#### - **Add Post (`/posts`, POST)**
  - Accepts JSON data to add a new post with `title`, `content` and `author`.
  - Inserts the new post into the database and commits the transaction.

#### - **Get All Posts (`/posts`, GET)**
  - Retrieves all posts from the database.
  - Returns a JSON response containing a list of all posts.

#### - **Add Tag (`/tags`, POST)**
  - Accepts JSON data to add a new tag with `name`.
  - Inserts the new tag into the database and commits the transaction.

#### - **Get All Tags (`/tags`, GET)**
  - Retrieves all tags from the database.
  - Returns a JSON response containing a list of all tags.

#### - **Add Tag to Post(`/posts/<int:post_id>/tags`, POST)**
  - Accepts JSON data to add a existing tag to an existing post.
  - Checks for specific tag and post to exist in the database before association.
  - Inserts the tag and associated post info into the post_tags table of database and commits the transaction.

---

## Example Usage
**Testing the APIs using Postman app**

### 1. **POST Request to `/users`**
Add a user with a JSON payload:
```json
{
  "username": "john_doe",
  "email": "john.doe@example.com"
}
