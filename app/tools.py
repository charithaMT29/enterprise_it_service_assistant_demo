ASSETS = {
    "AST-1001": {
        "device": "Dell Latitude 5440",
        "employee": "Nisha Rao",
        "department": "Finance",
        "status": "In service",
    },
    "AST-1002": {
        "device": "HP EliteBook 840",
        "employee": "Arjun Mehta",
        "department": "Engineering",
        "status": "In service",
    },
    "AST-1003": {
        "device": "Lenovo ThinkPad T14",
        "employee": "Maya Sen",
        "department": "Operations",
        "status": "Under repair",
    },
    "AST-1004": {
        "device": "Dell Precision 3581",
        "employee": "Kabir Das",
        "department": "Engineering",
        "status": "In service",
    },
}

TICKETS = {
    "INC-2041": {
        "category": "Laptop display",
        "priority": "High",
        "status": "In progress",
        "assigned_team": "Endpoint Support",
    },
    "INC-2042": {
        "category": "VPN access",
        "priority": "Medium",
        "status": "Waiting for user",
        "assigned_team": "Network Support",
    },
    "INC-2043": {
        "category": "Printer issue",
        "priority": "Low",
        "status": "Resolved",
        "assigned_team": "Workplace Technology",
    },
    "INC-2044": {
        "category": "Email access",
        "priority": "High",
        "status": "Open",
        "assigned_team": "Identity Support",
    },
}

SUPPORT_TEAMS = [
    {
        "team": "Endpoint Support",
        "responsibilities": "Laptops, desktops, monitors and peripherals",
    },
    {
        "team": "Network Support",
        "responsibilities": "VPN, Wi-Fi, connectivity and network access",
    },
    {
        "team": "Identity Support",
        "responsibilities": "Account access, passwords and authentication",
    },
    {
        "team": "Workplace Technology",
        "responsibilities": "Printers, meeting rooms and collaboration devices",
    },
]

INCIDENT_DRAFTS = []

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_asset",
            "description": "Look up a fictional IT asset using its asset tag.",
            "parameters": {
                "type": "object",
                "properties": {
                    "asset_tag": {"type": "string"}
                },
                "required": ["asset_tag"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_ticket",
            "description": "Look up a fictional IT service ticket using its ticket ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"}
                },
                "required": ["ticket_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_support_teams",
            "description": "List IT support teams and their responsibilities.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prepare_incident_draft",
            "description": "Prepare an incident report draft for human review. Never submit it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "asset_tag": {"type": "string"},
                    "issue_description": {"type": "string"},
                    "priority": {
                        "type": "string",
                        "enum": ["High", "Medium", "Low"],
                    },
                },
                "required": [
                    "asset_tag",
                    "issue_description",
                    "priority",
                ],
            },
        },
    },
]


def execute_tool(name, arguments):
    """Allowlist, validate and execute only approved IT tools."""

    if not isinstance(arguments, dict):
        return {
            "ok": False,
            "error": "Tool arguments must be a JSON object.",
        }

    if name == "get_asset":
        asset_tag = str(arguments.get("asset_tag", "")).strip().upper()

        if not asset_tag or len(asset_tag) > 20:
            return {"ok": False, "error": "Please provide a valid asset tag."}

        asset = ASSETS.get(asset_tag)

        if not asset:
            return {
                "ok": False,
                "error": f"Asset {asset_tag} was not found.",
            }

        return {"ok": True, "asset_tag": asset_tag, **asset}

    if name == "get_ticket":
        ticket_id = str(arguments.get("ticket_id", "")).strip().upper()

        if not ticket_id or len(ticket_id) > 20:
            return {"ok": False, "error": "Please provide a valid ticket ID."}

        ticket = TICKETS.get(ticket_id)

        if not ticket:
            return {
                "ok": False,
                "error": f"Ticket {ticket_id} was not found.",
            }

        return {"ok": True, "ticket_id": ticket_id, **ticket}

    if name == "list_support_teams":
        return {
            "ok": True,
            "teams": SUPPORT_TEAMS,
        }

    if name == "prepare_incident_draft":
        asset_tag = str(arguments.get("asset_tag", "")).strip().upper()
        issue_description = str(
            arguments.get("issue_description", "")
        ).strip()
        priority = str(arguments.get("priority", "")).strip().capitalize()

        if asset_tag not in ASSETS:
            return {"ok": False, "error": "Unknown asset tag."}

        if not issue_description or len(issue_description) > 500:
            return {
                "ok": False,
                "error": "Provide an issue description (maximum 500 characters).",
            }

        if priority not in ["High", "Medium", "Low"]:
            return {
                "ok": False,
                "error": "Priority must be High, Medium or Low.",
            }

        draft = {
            "draft_id": f"ID-{len(INCIDENT_DRAFTS) + 1:03d}",
            "asset_tag": asset_tag,
            "device": ASSETS[asset_tag]["device"],
            "issue_description": issue_description,
            "priority": priority,
            "status": "DRAFT - HUMAN REVIEW REQUIRED",
            "submitted": False,
        }

        INCIDENT_DRAFTS.append(draft)

        return {"ok": True, **draft}

    return {
        "ok": False,
        "error": f"Tool '{name}' is not approved.",
    }
