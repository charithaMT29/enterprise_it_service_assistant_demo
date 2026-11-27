
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.main import app


class APITests(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    @patch("app.main.run_agent")
    def test_valid_chat_request(self, mock_agent):
        mock_agent.return_value = {
            "answer": "Hello! How can I help?",
            "trace": [],
            "steps": 1,
        }

        response = self.client.post(
            "/api/chat",
            json={"message": "Hello"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "Hello! How can I help?")
        mock_agent.assert_called_once()

    def test_message_too_short(self):
        response = self.client.post(
            "/api/chat",
            json={"message": "A"},
        )

        self.assertEqual(response.status_code, 422)

    def test_message_too_long(self):
        response = self.client.post(
            "/api/chat",
            json={"message": "A" * 1201},
        )

        self.assertEqual(response.status_code, 422)

    @patch("app.main.run_agent")
    def test_agent_error_returns_502(self, mock_agent):
        mock_agent.side_effect = RuntimeError("Simulated agent failure")

        response = self.client.post(
            "/api/chat",
            json={"message": "Hello"},
        )

        self.assertEqual(response.status_code, 502)
        self.assertIn("assistant encountered an error", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
