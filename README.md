# Enterprise IT Service & Asset Operations Assistant

## Project Overview

The Enterprise IT Service & Asset Operations Assistant is a locally running AI-powered application designed to help users with common IT support and asset management queries.

The application uses FastAPI, Ollama, and a local language model. It can retrieve asset and ticket information, identify support teams, search the IT operations knowledge guide, and prepare incident drafts for human review.

## Technologies Used

- **Python** – Application logic
- **FastAPI** – Backend API
- **Ollama** – Local LLM runtime
- **Qwen 2.5 3B** – Chat model
- **nomic-embed-text** – Embedding model
- **HTML, CSS, JavaScript** – Frontend
- **Unittest** – Automated testing

## Project Structure

```text
Enterprise_IT_Service_Assistant/
│
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── config.py
│   ├── knowledge.py
│   ├── main.py
│   ├── ollama_client.py
│   └── tools.py
│
├── data/
│   └── it_operations_guide.md
│
├── static/
│   ├── app.js
│   ├── index.html
│   └── style.css
│
├── tests/
│   ├── test_agent.py
│   ├── test_api.py
│   ├── test_knowledge.py
│   └── test_tools.py
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Prerequisites

- Python 3.10 or later
- Ollama installed and running
- The following Ollama models:
  - `qwen2.5:3b`
  - `nomic-embed-text:latest`

## Setup Instructions

### 1. Clone or extract the project

Open a terminal in the project directory.

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 5. Configure environment variables

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Keep `.env` local. Do not include it in the submission.

### 6. Download the Ollama models

```powershell
ollama pull qwen2.5:3b
ollama pull nomic-embed-text:latest
```

Make sure Ollama is running before starting the application.

## Running the Application

Start the FastAPI server using:

```powershell
uvicorn app.main:app --reload
```

Open the application in your browser:

```text
http://127.0.0.1:8000
```

### API and Health Endpoints

- **Application:** `http://127.0.0.1:8000`
- **API documentation:** `http://127.0.0.1:8000/docs`
- **Health check:** `http://127.0.0.1:8000/health`
- **Chat endpoint:** `POST http://127.0.0.1:8000/api/chat`

## Main Features

- Retrieve IT asset information.
- Retrieve incident and support ticket information.
- List support teams and their responsibilities.
- Search the IT operations guide using retrieval-augmented generation (RAG).
- Prepare incident drafts with validation.
- Use a bounded Plan–Act–Observe agent workflow.
- Display the assistant's response and activity trace in the frontend.
- Keep incident drafts subject to human review.

## Available Tools

The assistant uses controlled Python tools to perform specific IT operations:

- `get_asset` – Retrieves asset details.
- `get_ticket` – Retrieves ticket details.
- `list_support_teams` – Lists support teams and their responsibilities.
- `search_it_knowledge` – Searches the IT operations knowledge guide.
- `prepare_incident_draft` – Prepares an incident draft for human review.

## Knowledge Base

The knowledge base is located at:

```text
data/it_operations_guide.md
```

It contains IT operations guidance covering laptop replacement, incident priorities, VPN troubleshooting, lost or stolen devices, software installation, and ticket escalation.

The assistant retrieves relevant knowledge from this document to support its answers.

## Running Tests

Run the automated test suite from the project root directory:

```powershell
python -m unittest discover -s tests -v
```

The tests cover the agent workflow, API endpoints, knowledge retrieval, and IT operation tools.

## Safety and Limitations

- The application runs using locally hosted Ollama models.
- The agent is restricted by a maximum number of execution steps.
- The assistant uses controlled tools to retrieve and process IT information.
- Incident drafts are prepared for human review and are not automatically submitted.
- If the required information is unavailable in the knowledge base, the assistant should communicate that it could not find the information rather than inventing an answer.

## Testing Status

The project test suite contains 21 automated tests. All 21 tests passed during the final project verification.

