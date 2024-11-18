# flask-sqlalchemy
Flask-SQLAlchem implementation within a flask web app and managing a SQLite database

Postman VSCode extension used to test the APIs.

---

## Features and Components
---

### 1. **App Configuration**
- The app is configured to use **SQLite** as its database via the URI `sqlite:///example.db`.
- `SQLALCHEMY_TRACK_MODIFICATIONS` is disabled for performance optimization.

---

### 2. **Database Setup**
- **SQLAlchemy** is initialized with `Flask` app instance.
- `User` model defined for a user table in the database with the following columns:
  - `id`: Primary key, integer.
  - `username`: String, unique, non-nullable.
  - `email`: String, unique, non-nullable.
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
