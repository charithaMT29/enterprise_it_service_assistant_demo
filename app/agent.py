
import json
import re

from .ollama_client import chat
from .config import MAX_AGENT_STEPS
from .knowledge import retrieve_knowledge
from .tools import TOOL_DEFINITIONS, execute_tool


SYSTEM_PROMPT = """You are a helpful assistant for Northstar Enterprise Services IT support.

Use retrieved IT knowledge to answer policy and troubleshooting questions.
Always mention the relevant guide section title when guide evidence is used.

IMPORTANT KNOWLEDGE RULES:
- Base policy explanations ONLY on retrieved guide content.
- Never invent escalation teams, managers, procedures or policy rules.
- If the guide does not contain the requested information, say so clearly.
- Never invent asset data, ticket information or tool results.

TOOL SELECTION RULES:
- Use get_asset for a specific asset or asset tag.
- Use get_ticket for a specific ticket or ticket ID.
- Use list_support_teams for support teams and their responsibilities.
- Use prepare_incident_draft only when asked to prepare an incident draft.
- Never invent asset tags, ticket IDs or tool arguments.

INCIDENT RULES:
- Never claim that an incident has been submitted or approved.
- An incident can only be prepared as a draft for human review.

Keep responses clear, helpful and concise."""


def requires_knowledge_search(message):
    """Identify questions that need evidence from the IT operations guide."""

    message = message.lower()

    knowledge_keywords = [
        "policy",
        "procedure",
        "escalation",
        "escalate",
        "unresolved",
        "troubleshoot",
        "troubleshooting",
        "replacement",
        "lost or stolen",
        "stolen device",
        "software installation",
        "incident priority",
        "priority guide",
        "vpn",
        "reimbursement",
        "reimburse",
        "personal internet",
        "internet connection",
        "it operations guide",
    ]

    return any(keyword in message for keyword in knowledge_keywords)


def requires_operational_tools(message):
    """Identify requests that need operational IT tools."""

    message = message.lower()

    operational_keywords = [
        "asset",
        "asset tag",
        "device details",
        "ticket",
        "ticket id",
        "incident",
        "support team",
        "support teams",
        "team responsibilities",
    ]

    return any(keyword in message for keyword in operational_keywords)


def knowledge_search_tool(question):
    """Search the IT operations guide for relevant information."""

    results = retrieve_knowledge(question)

    return {
        "ok": bool(results),
        "matches": [
            {
                "section": item["title"],
                "text": item["text"],
                "similarity": item["score"],
            }
            for item in results
        ],
    }


def all_tool_definitions():
    """Return all approved tools, including knowledge search."""

    knowledge_tool = {
        "type": "function",
        "function": {
            "name": "search_it_knowledge",
            "description": (
                "Search the IT operations guide for relevant policies "
                "and troubleshooting information."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"}
                },
                "required": ["question"],
            },
        },
    }

    return TOOL_DEFINITIONS + [knowledge_tool]


def run_tool(name, args):
    """Execute only approved tools with validated arguments."""

    if not isinstance(args, dict):
        return {
            "ok": False,
            "error": "Tool arguments must be a JSON object.",
        }

    if name == "search_it_knowledge":
        question = str(args.get("question", "")).strip()

        if not question or len(question) > 500:
            return {
                "ok": False,
                "error": "Knowledge search question is empty or too long.",
            }

        return knowledge_search_tool(question)

    return execute_tool(name, args)


def run_agent(user_message, history=None):
    """Run a bounded agent loop with reliable multi-tool execution."""

    history = history or []
    trace = []
    used_tools = set()

    message_lower = user_message.lower()

    # Detect a ticket ID.
    ticket_match = re.search(
        r"\bINC-\d{4}\b",
        user_message.upper(),
    )

    # Detect a request for team responsibilities.
    team_phrases = [
        "support team",
        "support teams",
        "team responsibility",
        "team responsibilities",
        "team responsible",
        "responsible team",
        "assigned team",
        "which team handles",
        "team handles",
        "responsibilities of",
    ]

    asks_team_responsibilities = any(
        phrase in message_lower
        for phrase in team_phrases
    )

    # Retrieve guide evidence when required.
    knowledge_result = None

    if requires_knowledge_search(user_message):
        knowledge_result = knowledge_search_tool(user_message)

        trace.append({
            "step": len(trace) + 1,
            "tool": "search_it_knowledge",
            "arguments": {"question": user_message},
            "result": knowledge_result,
        })

    # Handle combined ticket and team-responsibility requests.
    # Both Python tools are executed directly and deterministically.
    if ticket_match and asks_team_responsibilities:

        ticket_id = ticket_match.group(0)

        ticket_result = run_tool(
            "get_ticket",
            {"ticket_id": ticket_id},
        )

        used_tools.add("get_ticket")

        trace.append({
            "step": len(trace) + 1,
            "tool": "get_ticket",
            "arguments": {"ticket_id": ticket_id},
            "result": ticket_result,
        })

        if not ticket_result.get("ok"):
            answer = ticket_result.get(
                "error",
                "The requested ticket could not be found.",
            )

            return {
                "answer": answer,
                "trace": trace,
                "steps": len(trace),
            }

        # Execute the second tool.
        teams_result = run_tool(
            "list_support_teams",
            {},
        )

        used_tools.add("list_support_teams")

        trace.append({
            "step": len(trace) + 1,
            "tool": "list_support_teams",
            "arguments": {},
            "result": teams_result,
        })

        if not teams_result.get("ok"):
            return {
                "answer": (
                    f"Incident {ticket_id} was found, but the support "
                    "team responsibilities could not be retrieved."
                ),
                "trace": trace,
                "steps": len(trace),
            }

        # Prepare the answer using actual tool results.
        team_name = ticket_result.get(
            "assigned_team",
            "Unknown team",
        )

        teams = teams_result.get("teams", [])

        team_info = next(
            (
                team
                for team in teams
                if team.get("team") == team_name
            ),
            None,
        )

        if team_info:
            responsibilities = team_info.get(
                "responsibilities",
                "No responsibilities are available.",
            )
        else:
            responsibilities = (
                "The team's responsibilities were not found "
                "in the available support team records."
            )

        answer = (
            f"Incident {ticket_result['ticket_id']} is in the category "
            f"of {ticket_result['category']}. "
            f"It has {ticket_result['priority']} priority and is "
            f"currently {ticket_result['status']}. "
            f"It is assigned to {team_name}. "
            f"{team_name} is responsible for {responsibilities.lower()}."
        )

        return {
            "answer": answer,
            "trace": trace,
            "steps": len(trace),
        }

    # Build the normal assistant conversation.
    system_content = SYSTEM_PROMPT

    if knowledge_result is not None:
        system_content += (
            "\n\nMANDATORY RETRIEVED IT GUIDE EVIDENCE:\n"
            "Use only the following retrieved content when explaining "
            "IT policies or procedures. Do not add unsupported details.\n"
            + json.dumps(
                knowledge_result,
                ensure_ascii=False,
            )
        )

    messages = [
        {
            "role": "system",
            "content": system_content,
        }
    ]

    messages.extend(history[-8:])

    messages.append({
        "role": "user",
        "content": user_message,
    })

    # Select tools according to the request.
    if knowledge_result is not None:
        if requires_operational_tools(user_message):
            available_tools = TOOL_DEFINITIONS
        else:
            available_tools = []
    else:
        available_tools = all_tool_definitions()

    # Bounded agent loop.
    for step in range(MAX_AGENT_STEPS):

        assistant_message = chat(
            messages,
            tools=available_tools,
        )

        calls = assistant_message.get("tool_calls", [])

        if not calls:
            answer = assistant_message.get("content") or (
                "I could not prepare an answer. Please try again."
            )

            return {
                "answer": answer,
                "trace": trace,
                "steps": len(trace) + step + 1,
            }

        messages.append(assistant_message)

        allowed_names = {
            item["function"]["name"]
            for item in available_tools
        }

        for call in calls:

            function = call.get("function", {})
            name = function.get("name", "")
            arguments = function.get("arguments", {})

            if not isinstance(arguments, dict):
                arguments = {}

            if name not in allowed_names:
                result = {
                    "ok": False,
                    "error": (
                        "This tool is not available "
                        "for the current request."
                    ),
                }
            else:
                result = run_tool(name, arguments)

            trace.append({
                "step": len(trace) + 1,
                "tool": name,
                "arguments": arguments,
                "result": result,
            })

            messages.append({
                "role": "tool",
                "content": json.dumps(
                    result,
                    ensure_ascii=False,
                ),
            })

    # Final response after reaching the maximum number of tool cycles.
    messages.append({
        "role": "system",
        "content": (
            "The tool-step limit has been reached. Summarize only "
            "the results already obtained. Do not call more tools."
        ),
    })

    final = chat(messages)

    final_answer = final.get("content") or (
        "The request reached its tool-step limit. "
        "Please try a simpler question."
    )

    return {
        "answer": final_answer,
        "trace": trace,
        "steps":  MAX_AGENT_STEPS,
        "notice": "Maximum agent steps reached.",
    }
