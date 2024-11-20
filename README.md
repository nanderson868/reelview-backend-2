# ReelView

ReelView is a web app that provides analytics on user data from Letterboxd accounts. It allows users to query any Letterboxd usernames and access analytics for their or their friends watchlist and watched movies. Users can compare their watchlists with friends to discover films to watch together.

Key Features:

    Web Scraping: Automatically fetches data from Letterboxd.
    Database: Stores scraped data to improve load times and reduce the need for repeated scraping.
    Analytics: Delivers insights on personal and friend’s watchlist and watched movies.

Security and Performance:

    Query Limiting and Timeouts: Ensures efficient use of resources and prevents abuse of syncing privileges.
    User Permissions: Manages access rights to syncing and scraping functionalities to maintain system integrity.
    Error Handling: Implements robust error handling and retry logic for network requests and database operations.

## Stack

### Backend

- Flask: Web application framework.
- SQLAlchemy: ORM and database toolkit.
- Flask-Migrate: Database migration tool for SQLAlchemy.
- PostgreSQL: Relational database system. (Heroku Postgres)
- Heroku: Cloud platform for deployment. [https://api.reelview.io]

#### Project Structure

```bash
├── Procfile
├── README.md
├── app
│   ├── __init__.py
│   ├── extensions.py
│   ├── models.py
│   ├── routes.py
│   └── services.py
├── config.py
├── docs
│   └── openAPI.yaml
├── pyvenv.cfg
├── requirements.txt
└── run.py
```

#### Overview

##### Initialization & Configuration

`__init__.py`:

- Initializes Flask app with settings from `config.py`.
- Sets up CORS and Flask-Migrate.
- Registers routes from `routes.py`.

`config.py`:

- Base Config class with SQLALCHEMY configurations.
- DevelopmentConfig and ProductionConfig for environment-specific settings.

##### Environment Variables

`.env`:

- Contains environment variables for the application such as `DATABASE_URL`.

##### Database Setup

`extensions.py`:

- Initializes SQLAlchemy and Flask Limiter

`models.py`: Defines ORM models: User, Movie, UserMovie.

- Maps models to database tables using SQLAlchemy.

##### Application Logic

`routes.py`: Defines API endpoints for operations.

- Links to `services.py` for business logic.

`services.py`:

- Contains core business logic including database interaction, data processing and web scraping.
- Robust error handling and retry logic for network requests.

##### Error Handling & Design

- Centralized configuration management via `config.py`.
- Emphasizes robust error handling, especially in network interactions and database operations.

## API Endpoints

> Full openAPI specs available in `/docs/openapi.yaml`

- `/api/get`
  - Input: List of Letterboxd usernames
  - Output: User data.
- `/api/sync`
  - Input: List of Letterboxd username
    - Syncs user data from Letterboxd to database.
  - Output: Synced user data.

### Frontend

- TypeScript
- npm (package manager)
- Next.js (web framework)
- Tailwind CSS (styling)
- Vercel (frontend deployment) [https://reelview.io]

## Project Structure

### Backend

## Installation

### Backend

1. Clone the repository

```bash
git clone
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the application

```bash
python run.py
```

### Frontend

1. Clone the repository

```bash
git clone
```

2. Install dependencies

```bash
npm install
```

3. Run the application

```bash
npm run dev
```

Test
