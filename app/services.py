# services.py
from datetime import datetime, timezone
import time
from bs4 import BeautifulSoup
from flask import request, jsonify
import requests
from .models import User, Movie, UserMovie
from .extensions import db
import logging
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

base_url = "https://letterboxd.com"


def fetch_page(url, max_attempts=3, delay=1):
    """Fetches page content, with retry logic for robustness."""
    for attempt in range(max_attempts):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.RequestException as e:
            logging.error("Request failed. URL: [%s] Error: [%s]", url, e)
            if attempt < max_attempts - 1:
                logging.info("Retrying... Attempt %d of %d", attempt + 1, max_attempts)
                time.sleep(delay)
            else:
                logging.info("Final attempt failed. No more retries.")
    logging.error("Failed to fetch page after %d attempts.", max_attempts)
    return None


def update_user_movies(user, max_pages=10):
    """Updates movies for a user by scraping a web page."""
    page_index = 1
    current_page = get_url(user.username, list_type="watchlist")
    while current_page and page_index <= max_pages:
        logging.info("Fetching page %d", page_index)
        soup = fetch_page(current_page)
        if not soup:
            break
        process_movies(user=user, soup=soup)
        current_page = get_next_page(soup)
        page_index += 1


def process_movies(soup, user, max_movies=50):
    """Processes each movie found on a page."""
    for li in soup.find_all("li", class_="poster-container")[:max_movies]:
        process_movie(li, user)


def process_movie(li, user):
    """Processes an individual movie and adds it to the database if necessary."""
    movie_poster = li.find("div", {"class": "film-poster"})
    if not movie_poster:
        logging.error("Movie poster not found")
        return
    movie_id = movie_poster.get("data-film-id")
    movie = Movie.query.get(movie_id)
    if not movie:
        movie = Movie(
            id=movie_id,
            title=movie_poster.get("data-film-name") or "N/A",
            slug=format_title(movie_poster.get("data-film-slug")),
        )
        db.session.add(movie)
        logging.info("New movie added: [%s]", movie.title)
    db.session.add(UserMovie(user_id=user.id, movie_id=movie.id))


def get_next_page(soup):
    """Finds and returns the URL of the next page to scrape, if it exists."""
    next_page_link = soup.find("a", class_="next")
    if next_page_link:
        return f"{base_url}{next_page_link['href']}"
    return None


def get_url(username, list_type="watchlist"):
    """Generates a URL for a user's page."""
    return f"{base_url}/{username}/{list_type}/"


def check_session(session, caller="check_session"):
    transaction_active = False
    if session.is_active:
        transaction = session.get_transaction()
        transaction_active = transaction is not None and transaction.is_active
    logging.info(caller + f"\n\tTransaction active: {str(transaction_active)}")


# def handle_search_request():
#     """Handles search requests for username."""
#     try:
#         data = parse_request_data()
#         username = get_usernames(data)
#         return jsonify(process_usernames(usernames, find=True)), 200
#     except (BadRequest, SQLAlchemyError) as e:
#         logging.error(f"Error in handle_search_request: {e}", exc_info=True)
#         raise


def handle_request(suggest=False, find=False, add=False, sync=False):
    """Handles user verification or synchronization requests based on the input sync flag."""
    try:
        data = parse_request_data()
        usernames = get_usernames(data)
        results = process_usernames(
            usernames, suggest=suggest, find=find, add=add, sync=sync
        )
        return (
            jsonify(results),
            200,
        )
    except (BadRequest, SQLAlchemyError) as e:
        # Raise to let the app-level handler take care of it
        logging.error(f"Error in handle_request: {e}", exc_info=True)
        raise


def parse_request_data():
    """Attempt to parse request data as JSON or raise an error."""
    try:
        data = request.get_json(force=True)
    except BadRequest:
        logging.error("Invalid JSON provided")
        raise BadRequest("Invalid JSON data")
    if not data:
        logging.error("No data provided in request")
        raise BadRequest("No data provided")
    return data


def get_usernames(data):
    """Ensure usernames forms a list of strings."""
    usernames = data.get("usernames")
    if not usernames or not isinstance(usernames, list):
        logging.error("Invalid username list provided or list is empty")
        raise BadRequest("Usernames should be a list of strings")
    for name in usernames:
        if not isinstance(name, str):
            logging.error(f"Invalid username format: {name}")
            raise BadRequest("All usernames must be strings")
    return usernames


def process_usernames(usernames, suggest, find, add, sync):
    """Process a list of usernames and collect their processing results."""
    logging.info(f"Processing usernames: {usernames}...")
    results = {}
    for username in usernames:
        user, suggestions, searched, added, synced, error = handle_user(
            username, suggest=suggest, find=find, add=add, sync=sync
        )
        data = user_data(
            user=user,
            searched=searched,
            suggestions=suggestions,
            added=added,
            synced=synced,
        )
        results[username] = request_data(data=data, error=error)
    logging.info(f"Processed usernames: {results}")
    return results


def handle_user(username, suggest=False, find=False, add=False, sync=False):
    """Process a list of usernames and collect their processing results."""
    logging.info(f"Handling user: {username}...")
    user = None
    suggestions = None
    found = False
    searched = False
    added = False
    synced = False
    error = None
    try:
        user = get_user(username)
        if suggest:
            suggestions = autocomplete(username)
        if find:
            found = find_user(username)
            searched = True
        if not user and found and add:
            user = add_user(username)
            added = True
        if user and sync:
            user = sync_user(user)
            synced = True
    except NoResultFound as e:
        logging.error(f"User not found processing user {username}: {e}")
        error = "User not found"
    except SQLAlchemyError as e:
        logging.error(f"Database error processing user {username}: {e}")
        raise BadRequest("Database error") from e
    return user, suggestions, searched, added, synced, error


def get_user(username):
    """Returns user; adding new users if verified on the external source."""
    logging.debug(f"Getting user {username}...")
    try:
        user = User.query.filter_by(username=username).one()  # Begins a transaction
        logging.info(f"User {username} found in database")
        db.session().commit()
        return user
    except NoResultFound:
        logging
        db.session().rollback()
        return None


def find_user(username):
    """Verifies if a user exists on the external source."""
    logging.debug(f"Verifying user {username}...")
    try:
        response = fetch_page(get_url(username))
        if not response:
            logging.error(f"User {username} not found on external source")
            return False
        logging.info(f"User {username} found on external source")
        return True
    except Exception as e:
        logging.error(f"Failed to fetch user data for {username}: {e}")
        raise


def add_user(username):
    """Add a new user to the database."""
    logging.info(f"Adding user {username}...")
    try:
        with db.session.begin():
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        return user
    except SQLAlchemyError as e:
        logging.error(f"Error adding new user {username}: {e}")
        raise


def sync_user(user):
    """Sync a user's details with an external account."""
    logging.info(f"Syncing user {user.username}...")
    try:
        UserMovie.query.filter_by(user_id=user.id).delete()
        update_user_movies(user=user)
        user.synced_at = datetime.now(timezone.utc)
        db.session.commit()
        return user
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error syncing user {user.username}: {e}")
        raise


def autocomplete(username):
    """Returns a list of usernames that match the input."""
    return User.query.filter(User.username.ilike(f"{username}%")).all()


def request_data(data, error):
    """Generate a summary for a user, handling cases with errors and new users."""
    return {"error": error, "data": data}


def user_data(user, suggestions, searched, added, synced):
    return {
        "added": added,
        "synced": synced,
        "searched": searched,
        "suggestions": (
            [suggestion.username for suggestion in suggestions] if suggestions else []
        ),
        "user": (user_details(user) if user else None),
    }


def user_details(user):
    return {
        "username": user.username,
        "added_at": get_date(user.added_at),
        "synced_at": get_date(user.synced_at),
        "movie_count": len(user.movies),
    }


def get_date(date):
    """Format datetime object as a string or return None if not set."""
    return date.strftime("%Y-%m-%d %H:%M:%S") if date else None


def format_title(slug: str) -> str:
    return " ".join(word.capitalize() for word in slug.split("-"))
