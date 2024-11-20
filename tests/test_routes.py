# test_routes.py
from flask_testing import TestCase
from app import create_app
from app.extensions import db
from config import TestingConfig


class TestRoutes(TestCase):
    def create_app(self):
        # Create an instance of the Flask app configured for testing
        app = create_app(TestingConfig)
        app.config["TESTING"] = True
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_route_with_valid_input(self):
        valid_input = {"usernames": ["evilnik"]}
        response = self.client.post("/api/search", json=valid_input)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.data, b"Expected response")

    def test_route_with_no_input(self):
        response = self.client.post("/api/search")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            b"error" in response.data
        )  # Assert that the response indicates an error

    def test_route_with_invalid_input(self):
        invalid_input = {"invalid_key": "some_data"}
        response = self.client.post("/api/search", json=invalid_input)
        self.assertEqual(response.status_code, 400)
        # Assert that the response indicates an error
        self.assertTrue(b"error" in response.data)

    def test_rate_limiting(self):
        for _ in range(5):  # Assuming the limit is 5 requests per minute
            response = self.client.get("/api/test_limit")
            self.assertEqual(response.status_code, 200)

        # This request should fail due to rate limiting
        response = self.client.get("/api/test_limit")
        self.assertEqual(response.status_code, 429)


# Run the tests
if __name__ == "__main__":
    import unittest

    unittest.main()
