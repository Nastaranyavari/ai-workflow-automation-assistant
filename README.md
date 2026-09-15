# AI Workflow Automation Assistant

An AI-powered workflow automation assistant that combines **LLM reasoning, tool calling, document processing, database operations, and workflow automation** in a modular backend architecture.

The system receives user requests, determines the required task, invokes appropriate tools through a LangGraph-based agent, processes uploaded PDF documents, stores structured records in PostgreSQL, and can trigger external workflows through n8n.

---

## Overview

The assistant is designed to handle multiple types of tasks through a single conversational interface.

Examples include:

* Calculating values
* Reading and summarizing PDF documents
* Saving information into a database
* Searching previously stored records
* Triggering external n8n workflows
* Combining multiple tools to complete a task

The core idea is to let the LLM determine **which tool should be used and when**, while keeping the actual operations implemented as independent Python tools.

---

## Architecture

```text
                         ┌─────────────────────┐
                         │      Frontend       │
                         │   HTML / CSS / JS   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Django REST API  │
                         │      /api/assistant │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  AssistantService   │
                         │ Request Processing  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   LangGraph Agent  │
                         │  Agent Orchestration│
                         └──────────┬──────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
            ┌──────────┐      ┌──────────┐     ┌──────────┐
            │   PDF    │      │ Database │     │Calculator│
            │   Tool   │      │   Tools  │     │   Tool   │
            └──────────┘      └─────┬────┘     └──────────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │ Django ORM    │
                            └───────┬───────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │  PostgreSQL   │
                            │    Docker     │
                            └───────────────┘

                         ┌─────────────────────┐
                         │        n8n          │
                         │ Workflow Automation │
                         └─────────────────────┘
```

---

## Key Features

### AI Agent

The application uses a **LangGraph-based agent** to orchestrate tasks and decide which tools should be invoked.

The agent supports tool calling for:

* `calculate`
* `read_pdf`
* `save_record`
* `search_records`

The agent maintains execution state and supports session-based conversations.

---

### PDF Processing

Users can upload PDF documents through the API.

The system:

1. Receives the uploaded file.
2. Stores it under `data/uploads/`.
3. Registers document metadata in PostgreSQL.
4. Passes the file path to the agent.
5. Allows the agent to invoke the PDF reading tool.
6. Uses the extracted text as part of the task execution.

Current PDF extraction is implemented using `pypdf`.

---

### Database Operations

The application uses Django ORM for application-level database operations.

The main models are:

#### Document

Stores uploaded document metadata.

```text
Document
├── id
├── filename
├── file_path
└── created_at
```

#### Record

Stores information generated or saved by the assistant.

```text
Record
├── id
├── title
├── content
├── document (optional)
└── created_at
```

The `document` relationship is currently optional so records can exist independently of a specific uploaded document.

---

### PostgreSQL

PostgreSQL is used as the main application database.

The database runs through Docker Compose:

```text
Django
   │
   ▼
Django ORM
   │
   ▼
psycopg
   │
   ▼
PostgreSQL 16
```

Database configuration is separated from the application logic, allowing the backend to interact with PostgreSQL through Django's ORM.

---

### Workflow Automation with n8n

The assistant can trigger external workflows through n8n.

The n8n integration is used to extend the capabilities of the agent beyond the Python application itself.

Typical workflow examples include:

* Processing and saving document summaries
* Triggering external automation
* Sending task results to an external workflow

The integration is implemented as a dedicated service rather than being embedded directly inside the agent logic.

---

### LLM Provider

The application uses an OpenAI-compatible client to communicate with OpenRouter.

The provider is isolated behind:

```text
app/services/openrouter_provider.py
```

This keeps LLM communication separate from the agent orchestration logic.

Configuration is provided through environment variables:

```env
OPENROUTER_API_KEY=your_api_key
OPENROUTER_MODEL=your_model
```

---

## Project Structure

```text
ai_workflow_assistant/
│
├── app/
│   ├── agent/
│   │   └── graph.py
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   ├── services/
│   │   ├── n8n_service.py
│   │   └── openrouter_provider.py
│   │
│   └── tools/
│       ├── calculator.py
│       ├── database_tool.py
│       └── pdf_tool.py
│
├── backend/
│   ├── manage.py
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   └── assistant/
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       │
│       └── services/
│           └── assistant_service.py
│
├── data/
│   ├── uploads/
│   └── checkpoints.db
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── tests/
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Request Flow

A typical request follows this pipeline:

```text
User Request
     │
     ▼
Frontend
     │
     ▼
POST /api/assistant/
     │
     ▼
Serializer Validation
     │
     ▼
AssistantService
     │
     ├── Save uploaded file
     ├── Create Document metadata
     │
     ▼
LangGraph Agent
     │
     ▼
LLM
     │
     ├──────────────┬───────────────┬──────────────┐
     ▼              ▼               ▼              ▼
Calculator      PDF Reader      Database       n8n Service
                                   │
                                   ▼
                              PostgreSQL
```

---

## API

### Assistant Endpoint

```http
POST /api/assistant/
```

The endpoint accepts multipart form data.

### Parameters

| Parameter    | Type   | Required | Description                     |
| ------------ | ------ | -------: | ------------------------------- |
| `message`    | string |      Yes | User's request                  |
| `session_id` | string |      Yes | Conversation/session identifier |
| `file`       | file   |       No | Optional PDF document           |

Example:

```text
message:
"Summarize this document and save it to the database."

session_id:
"demo-session-001"

file:
contract.pdf
```

### Response

```json
{
    "status": "completed",
    "response": "..."
}
```

---

## Agent State

The LangGraph agent maintains a structured state during execution.

```python
class AgentState(TypedDict):
    messages: list
    file_path: str | None
    status: str
    session_id: str
    task: str | None
    record_id: int | None
    n8n_result: dict | None
```

This state allows different nodes and tools to share execution information without tightly coupling the individual components.

---

## Tool Architecture

Tools are implemented independently from the agent.

```text
LangGraph Agent
      │
      ▼
Tool Selection
      │
      ├── calculate()
      ├── read_pdf()
      ├── save_record()
      └── search_records()
```

This architecture allows tools to be added or replaced without rewriting the entire agent.

---

## LangGraph Checkpointing

LangGraph uses SQLite checkpointing to persist agent execution state.

The checkpoint database is stored separately from the application PostgreSQL database:

```text
data/checkpoints.db
```

This separation allows:

* PostgreSQL → application data
* SQLite checkpoint → LangGraph execution state

These two databases serve different responsibilities.

---

## Docker

PostgreSQL is provided through Docker Compose.

Start the database:

```bash
docker compose up -d db
```

Check the running containers:

```bash
docker compose ps
```

Expected PostgreSQL service:

```text
ai_workflow_postgres
```

PostgreSQL is exposed on:

```text
localhost:5432
```

---

## Local Development

### 1. Clone the repository

```bash
git clone <repository-url>
cd ai_workflow_assistant
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_api_key
OPENROUTER_MODEL=your_model
```

Do not commit `.env` to the repository.

### 5. Start PostgreSQL

```bash
docker compose up -d db
```

### 6. Apply migrations

From the `backend` directory:

```bash
python manage.py migrate
```

### 7. Run Django

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

---

## Database Migrations

When Django models change:

```bash
python manage.py makemigrations
```

Then:

```bash
python manage.py migrate
```

---

## Testing

Run the test suite with:

```bash
python -m pytest
```

The project also supports direct testing of the database layer through Django shell:

```bash
python manage.py shell
```

Example:

```python
from app.tools.database_tool import save_record, search_records

save_record(
    "Example",
    "Example content"
)

search_records("Example")
```

---

## Design Principles

The project follows several engineering principles:

### Separation of Concerns

Different responsibilities are isolated:

```text
API
 ↓
Service Layer
 ↓
Agent
 ↓
Tools
 ↓
External Systems / Database
```

### Modular Tooling

Tools are independent Python functions and can be extended without tightly coupling them to the agent.

### Provider Isolation

LLM communication is isolated behind a provider layer, making it easier to replace or add providers.

### Database Abstraction

Application database operations use Django ORM instead of embedding raw SQL inside the agent.

### Stateful Agent Execution

LangGraph checkpointing provides persistence for agent execution state.

### External Workflow Integration

n8n functionality is isolated in its own service rather than being directly embedded into the agent.

---

## Technology Stack

| Technology              | Purpose                      |
| ----------------------- | ---------------------------- |
| Python                  | Core application             |
| Django                  | Backend framework            |
| Django REST Framework   | REST API                     |
| LangGraph               | Agent orchestration          |
| OpenRouter              | LLM provider                 |
| OpenAI SDK              | OpenAI-compatible API client |
| PostgreSQL              | Application database         |
| Django ORM              | Database abstraction         |
| pypdf                   | PDF text extraction          |
| n8n                     | Workflow automation          |
| Docker Compose          | PostgreSQL infrastructure    |
| HTML / CSS / JavaScript | Frontend                     |
| pytest                  | Testing                      |

---

## Current Capabilities

* [x] LLM-powered agent
* [x] LangGraph orchestration
* [x] Tool calling
* [x] PDF upload
* [x] PDF text extraction
* [x] PDF summarization
* [x] Database record creation
* [x] Database search
* [x] PostgreSQL integration
* [x] Django ORM
* [x] Document metadata storage
* [x] LangGraph checkpointing
* [x] n8n integration
* [x] Session-based agent execution
* [x] REST API
* [x] Browser-based frontend
* [x] Dockerized PostgreSQL

---

## Future Improvements

Potential future improvements include:

* Authentication and user management
* User-specific document ownership
* Linking generated records to their source documents
* Document-level search and filtering
* Background task processing
* Better error handling and retry strategies
* Automated API tests
* Production deployment
* Observability and structured logging
* More robust document processing
* Support for additional document formats

---

## Project Goal

The goal of this project is to demonstrate how an AI assistant can be engineered as a **modular software system**, rather than simply wrapping an LLM in a chat interface.

The project focuses on the integration of:

**LLM + Agent Orchestration + Tools + Backend API + Database + Document Processing + Workflow Automation**

while maintaining clear separation between business logic, infrastructure, AI components, and external services.
