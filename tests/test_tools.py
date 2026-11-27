import unittest
from app.tools import execute_tool, INCIDENT_DRAFTS

class ToolTests(unittest.TestCase):

    def test_valid_asset(self):
        result = execute_tool("get_asset", {"asset_tag": "AST-1001"})
        self.assertTrue(result["ok"])
        self.assertEqual(result["employee"], "Nisha Rao")

    def test_unknown_asset(self):
        result = execute_tool("get_asset", {"asset_tag": "AST-9999"})
        self.assertFalse(result["ok"])

    def test_ticket_lookup(self):
        result = execute_tool("get_ticket", {"ticket_id": "INC-2041"})
        self.assertTrue(result["ok"])
        self.assertEqual(result["assigned_team"], "Endpoint Support")

    def test_support_team_list(self):
        result = execute_tool("list_support_teams", {})
        self.assertEqual(len(result["teams"]), 4)

    def test_unapproved_tool(self):
        result = execute_tool("delete_asset", {})
        self.assertIn("error", result)

    def test_incident_draft(self):
        result = execute_tool(
            "prepare_incident_draft",
            {
                "asset_tag": "AST-1001",
                "issue_description": "Laptop screen is flickering",
                "priority": "High",
            },
        )
        self.assertTrue(result["ok"])
        self.assertTrue(result["status"].startswith("DRAFT"))
        self.assertFalse(result["submitted"])

    def test_invalid_asset_for_draft(self):
        result = execute_tool(
            "prepare_incident_draft",
            {
                "asset_tag": "AST-9999",
                "issue_description": "Laptop is not working",
                "priority": "High",
            },
        )
        self.assertFalse(result["ok"])

    def test_empty_issue_description(self):
        result = execute_tool(
            "prepare_incident_draft",
            {
                "asset_tag": "AST-1001",
                "issue_description": "",
                "priority": "High",
            },
        )
        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
