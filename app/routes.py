# routes.py
from http.client import HTTPException
import logging
from flask import Blueprint, jsonify
from .services import (
    handle_request,
)
from http import HTTPStatus
from .extensions import limiter
from werkzeug.exceptions import BadRequest


routes_blueprint = Blueprint("routes", __name__)


@routes_blueprint.route("/api/test_limit", methods=["GET"])
@limiter.limit("5 per minute")
def test():
    return "This is a rate-limited response", HTTPStatus.OK


@routes_blueprint.route("/")
def home():
    return "Welcome to ReelView", HTTPStatus.OK


@routes_blueprint.route("/api/")
def api():
    return "Welcome to the ReelView API", HTTPStatus.OK


@routes_blueprint.route("/api/search", methods=["POST"])
@limiter.limit("1000 per minute")
def search_users():
    """Search for saved users in the database."""
    return handle_request(suggest=True)


@routes_blueprint.route("/api/find", methods=["POST"])
def find_users():
    """Query for usernames on the external source."""
    return handle_request(find=True, add=True)


@routes_blueprint.route("/api/sync", methods=["POST"])
def sync_users():
    """Sync user data with the external source."""
    return handle_request(sync=True)


@routes_blueprint.errorhandler(HTTPException)
def handle_http_exception(e):
    response = e.get_response()
    response.json = {"error": str(e.description), "code": e.code}
    response.content_type = "application/json"
    return response


@routes_blueprint.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify(error=str(e)), 400


@routes_blueprint.errorhandler(Exception)
def handle_generic_exception(e):
    logging.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({"error": "A server error occurred", "code": 500}), 500


@routes_blueprint.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="ratelimit exceeded", details=str(e.description)), 429


# @limiter.request_filter
# def limiter_logging():
#     """This function will run before each request to check if it's being limited."""
#     limit = limiter.get_last_request_limit()
#     if limit and limit.reached:
#         logging.warning(f"Rate limit exceeded for {limit.key} with limit {limit.limit}")
#     return False  # returning False means all requests are checked


# @routes_blueprint.route("/api/compare", methods=["POST"])
# # @limiter.limit("10 per minute") # Optional custom limit for this particular route
# def compare_watchlists():
#     try:
#         data = request.get_json()
#         if not data or "usernames" not in data:
#             logging.error("Request payload is either empty or missing 'usernames'")
#             return jsonify({"error": "Bad request, missing data"}), 400

#         usernames = data["usernames"]
#         if not isinstance(usernames, list) or not all(
#             isinstance(name, str) for name in usernames
#         ):
#             logging.error("Usernames invalid: %s", usernames)
#             return (
#                 jsonify(
#                     {
#                         "error": "Bad request, 'usernames' invalid, should be a list of strings"
#                     }
#                 ),
#                 400,
#             )

#         if not usernames:
#             logging.error("Empty list of usernames provided")
#             return jsonify({"error": "No usernames provided"}), 400

#         logging.info("Usernames: %s", usernames)

#         # Fetch user details and movies
#         user_details = {}
#         movie_details = {}
#         movie_counts = defaultdict(set)
#         for username in usernames:
#             user = add_or_update_user(username)
#             if not user:
#                 user_details[username] = {"exists": False}
#                 continue
#             user_movies = user.movies
#             user_details[username] = {
#                 "exists": True,
#                 "movie_count": len(user_movies) if user else 0,
#                 "last_updated": user.last_updated.strftime("%Y-%m-%d %H:%M:%S"),
#             }
#             for user_movie in user_movies:
#                 movie = user_movie.movie
#                 movie_counts[movie.id].add(username)
#                 if movie.id not in movie_details:
#                     movie_details[movie, id] = {
#                         "id": movie.id,
#                         "title": movie.title,
#                         "slug": movie.slug,
#                     }

#         # Find the intersection of movies
#         intersection = defaultdict(list)
#         for movie_id, users in movie_counts.items():
#             if len(users) > 1:
#                 degree = len(users)
#                 movie_info = {
#                     **movie_details[movie_id],
#                     "users": list(users),
#                 }
#                 intersection[degree].append(movie_info)

#         # Sort the intersection by degree and then by movie title
#         intersection = {
#             k: sorted(v, key=lambda item: item["name"])
#             for k, v in sorted(
#                 intersection.items(), reverse=True, key=lambda item: item[0]
#             )
#         }

#         logging.info(user_details)
#         return jsonify(
#             {
#                 "movies": intersection,
#                 "user_details": user_details,
#             }
#         )
#     except KeyError as ke:
#         logging.error("Key error in request handling: %s", ke)
#         traceback.print_exc()
#         return jsonify({"error": "Failed to process request due to missing data"}), 500
#     except ValueError as ve:
#         logging.error("Value error in input data: %s", ve)
#         return jsonify({"error": "Invalid input"}), 400
#     except Exception as e:
#         logging.error("Unhandled exception: %s", e)
#         logging.error("Traceback details: %s", traceback.format_exc())
#         return jsonify({"error": "Internal Server Error"}), 500
