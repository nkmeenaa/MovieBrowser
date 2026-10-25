# 🎬 Movie Browser

A full-stack Django web application that ingests movie data from an external API, stores it in a local SQLite database, and provides users with browsing, search, and watchlist management capabilities.

---

## ✨ Features

- **Data Ingestion & Storage:** Fetches movies and cast details from an external API and stores them locally using Django's ORM (`get_or_create`) to prevent duplicates.
- **Django-Based User Authentication:** Secure registration, login, and logout flows built entirely on Django's built-in `django.contrib.auth` system (session-based authentication, hashed passwords, and CSRF-protected forms).
- **Personalized Watchlist:** Authenticated users can add or remove movies from their personal watchlist, with views protected by `@login_required` so only signed-in users can manage their own list.
- **Search & Pagination:** Browse the movie catalog with server-side pagination and a case-insensitive search bar (`icontains`).
- **Relational Database Design:** Utilizes `ManyToManyField` for linking Movies to Cast members and Movies to Users (Watchlists).
- **Robust Error Handling:** Uses `get_object_or_404` for safe database queries and gracefully handles missing API data.

---

## 🔐 Authentication (Django Auth)

This project uses Django's native authentication framework rather than a third-party auth library, keeping the auth flow simple, secure, and easy to extend.

- **Registration:** New users sign up through a Django `UserCreationForm`-based view, which validates input and creates a new `User` record with a securely hashed password.
- **Login / Logout:** Handled via Django's built-in `LoginView` and `LogoutView` (or equivalent custom views using `authenticate()` and `login()`/`logout()`), which manage session cookies automatically.
- **Session Management:** Django's default session middleware keeps users logged in across requests; sessions are invalidated on logout.
- **Access Control:** Watchlist views are wrapped with the `@login_required` decorator (or `LoginRequiredMixin` for class-based views) to ensure only authenticated users can add or remove movies.
- **Per-User Data:** Each user's watchlist is tied to their `User` instance via a `ManyToManyField`, so watchlists remain private and personalized.
- **CSRF Protection:** All authentication forms (login, registration) include Django's `{% csrf_token %}` to protect against cross-site request forgery.

---

## 🛠 Tech Stack

- **Backend:** Python, Django
- **Database:** SQLite (Development)
- **Frontend:** Django Templates (HTML), CSS
- **Authentication:** Django Session Auth (`django.contrib.auth`)
- **Deployment:** Render

---

## ✅ Prerequisites

- Python 3.8+
- `pip` (Python package installer)
- `git`

---

## 🚀 Local Setup & Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/nkmeenaa/MovieBrowser/
   cd MovieBrowser/TASK3
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv

   # On macOS/Linux
   source venv/bin/activate

   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file (or set environment variables directly) for any external API keys required for movie data ingestion, e.g.:

   ```bash
   API_URL=https://jsonfakery.com/movies/paginated?page=
   ```

5. **Apply database migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional, for Django admin access)**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**

   ```bash
   python manage.py runserver
   ```

8. **Open the app**

   Visit `http://127.0.0.1:8000/` in your browser. Register a new account or log in to start browsing movies and building your watchlist.

---

## 📖 Usage

- **Browse:** View the paginated movie catalog on the home page.
- **Search:** Use the search bar to find movies by title (case-insensitive).
- **Register / Login:** Create an account or sign in to unlock watchlist features.
- **Watchlist:** Add or remove movies from your personal watchlist while logged in.
- **Admin Panel:** Visit `/admin` (with superuser credentials) to manage movies, cast, and users directly.

---

## 🗂 Project Structure (high level)

```
TASK3/
├── manage.py
├── requirements.txt
├── <TASK3>/        # Django project settings & URLs
├── <movie>/            # Core app: models, views, templates, auth
│   ├── models.py          # Movie, Cast, Watchlist models
│   ├── views.py           # Browsing, search, auth, watchlist views
│   ├── urls.py
│   └── templates/
└── db.sqlite3             # Local development database
```
