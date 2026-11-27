
import unittest
from unittest.mock import patch

from app.agent import run_agent


class AgentTests(unittest.TestCase):

    @patch("app.agent.MAX_AGENT_STEPS", 2)
    @patch("app.agent.chat")
    def test_agent_stops_at_maximum_steps(self, mock_chat):

        # Simulate the model repeatedly requesting a ticket lookup.
        repeated_tool_call = {
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "get_ticket",
                        "arguments": {"ticket_id": "INC-2041"},
                    }
                }
            ],
        }

        # The first two responses request tools.
        # The third response is the final answer after the limit.
        mock_chat.side_effect = [
            repeated_tool_call,
            repeated_tool_call,
            {"content": "Stopped safely."},
        ]

        result = run_agent("Hello")

        self.assertEqual(mock_chat.call_count, 3)
        self.assertEqual(result["steps"], 2)
        self.assertEqual(len(result["trace"]), 2)
        self.assertEqual(result["answer"], "Stopped safely.")
        self.assertIn("notice", result)

    @patch("app.agent.chat")
    @patch("app.agent.knowledge_search_tool")
    def test_policy_question_triggers_knowledge_search(
        self,
        mock_knowledge_search,
        mock_chat
    ):

        mock_knowledge_search.return_value = {
            "ok": True,
            "matches": [
                {
                    "section": "VPN Troubleshooting",
                    "text": "Restart the VPN client.",
                    "similarity": 0.95,
                }
            ],
        }

        mock_chat.return_value = {
            "content": (
                "According to VPN Troubleshooting, "
                "restart the VPN client."
            ),
            "tool_calls": [],
        }

        result = run_agent("How do I troubleshoot VPN issues?")

        mock_knowledge_search.assert_called_once()
        mock_chat.assert_called_once()

        self.assertIn("VPN Troubleshooting", result["answer"])
        self.assertEqual(len(result["trace"]), 1)
        self.assertEqual(
            result["trace"][0]["tool"],
            "search_it_knowledge"
        )


if __name__ == "__main__":
    unittest.main()
