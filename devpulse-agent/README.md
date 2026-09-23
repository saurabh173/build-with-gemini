# DevPulse — Developer & IT Support Assistant

**DevPulse** is an autonomous AI assistant built with the **Google Agent Development Kit (ADK)** and deployed on **Google Cloud Agent Platform (Agent Runtime)**. DevPulse empowers software engineers and IT operations teams to monitor system health, manage Firestore support tickets, query grounded technical knowledge via Vertex AI RAG, generate system architecture diagrams, and perform geospatial lookups.

The agent includes a lightweight **FastAPI proxy and web chat frontend** deployed on **Google Cloud Run**, featuring **A2UI v0.8 rich component rendering** for interactive cards, columns, and system status dashboards.

---

## 🌟 Key Capabilities & Integrated Tools

### 1. 📋 Support Ticket Management (Google Cloud Firestore)
- **`create_support_ticket`**: Creates structured IT support tickets (service name, severity, issue description) directly in Firestore.
- **`get_support_ticket`**: Retrieves specific support tickets by ticket ID.
- **`list_support_tickets`**: Lists support tickets filtered by status (`OPEN`, `IN_PROGRESS`, `RESOLVED`).
- **`update_ticket_status`**: Updates ticket status and appends resolution notes in Firestore.

### 2. 📚 Grounded Technical Knowledge Base (Vertex AI RAG Engine)
- **`query_knowledge_base`**: Grounded technical search powered by a **Serverless Vertex AI RAG Corpus**. Queries indexed documentation and technical reference texts to answer infrastructure questions.

### 3. 📐 Architecture Diagram Generation (Gemini & Cloud Storage)
- **`generate_system_diagram`**: Generates high-quality technical diagrams using `gemini-3.1-flash-lite-image` in the `global` region.
- **Cloud Storage Integration**: Automatically uploads raw image bytes to a public Google Cloud Storage bucket and returns a public HTTPS URL for inline browser rendering.
- **Playground Artifacts**: Saves generated images to the ADK Playground Artifacts panel via `tool_context.save_artifact`.

### 4. 🗺️ Geospatial & Location Services (Google Maps APIs)
- **`geocode_address`**: Converts physical addresses into latitude and longitude coordinates using the **Google Maps Geocoding API**.
- **`find_nearby_places`**: Locates nearby places of interest (e.g. data centers, hospitals, tech offices) using the **Google Maps Places API (New)**.

### 5. 🟢 System Health & External API Monitoring
- **`fetch_service_health`**: Performs live HTTP status and latency checks on microservices.
- **`check_github_platform_status`**: Queries the live **GitHub Status API** (`https://www.githubstatus.com/api/v2/summary.json`) for component-level operational status (Git operations, Webhooks, API requests, Actions, Pull Requests).

### 6. 🧠 Memory Bank (Long-Term Conversational Memory)
- **`PreloadMemoryTool`**: Preloads durable memories into conversation context.
- **`generate_memories_callback`**: Callback wired to `after_agent_callback` (`add_session_to_memory`) to automatically extract and persist key developer facts across chat sessions.

### 7. 🔒 Sandboxed Code Execution
- **`SafeAgentEngineSandboxCodeExecutor`**: Safely executes Python code snippets inside Google Cloud Agent Platform isolated sandboxes (`AgentEngineSandboxCodeExecutor`).

### 8. 🎨 Rich UI Rendering (A2UI v0.8)
- System prompt generated using `A2uiSchemaManager` (v0.8) and `BasicCatalog`.
- **`a2ui_callback`**: `after_model_callback` that formats A2UI JSON output into `<a2a_datapart_json>` structures for native card rendering.

---

## 🛠️ Tech Stack & Google Cloud Services

- **Framework**: Google ADK (Agent Development Kit), A2A Protocol SDK, FastAPI
- **LLM Models**: `gemini-flash-latest` (Reasoning & Tools), `gemini-3.1-flash-lite-image` (Diagram Generation)
- **Google Cloud Services**:
  - **Vertex AI Agent Engine / Agent Runtime** (Deployment & Orchestration)
  - **Vertex AI RAG Engine** (Vector search & grounded retrieval)
  - **Google Cloud Firestore** (Support ticket persistence)
  - **Google Cloud Storage** (Generated image asset storage)
  - **Google Maps Platform** (Geocoding & Places APIs)
  - **Google Cloud Run** (Web chat proxy hosting)

---

## 📁 Repository Structure

```
devpulse-agent/
├── app/
│   ├── agent.py               # Main ADK Agent & App definition with A2UI & tools
│   ├── a2ui_utils.py          # A2UI callback and datapart formatting utilities
│   ├── fast_api_app.py        # FastAPI app wrapper for ADK
│   └── tools/
│       ├── firestore_tools.py # Firestore support ticket management tools
│       ├── health_tools.py    # Microservice health check tool
│       ├── external_status_tools.py # GitHub platform status tool
│       ├── image_tools.py     # Gemini image generation & Cloud Storage upload
│       ├── maps_tools.py      # Google Maps Geocoding & Places (New) tools
│       └── rag_tools.py       # Vertex AI RAG Corpus retrieval tool
├── frontend/
│   ├── main.py                # FastAPI proxy server (A2A protocol client)
│   ├── requirements.txt       # Frontend dependencies
│   └── static/
│       └── index.html         # Responsive Chat UI with A2UI card renderer
├── agents-cli-manifest.yaml   # Agent deployment manifest
└── pyproject.toml             # Python dependencies and project settings
```

---

## 🚀 Setup & Local Execution Instructions

### Prerequisites

- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) or standard `pip`
- Google Cloud SDK (`gcloud`) authenticated with Application Default Credentials (`gcloud auth application-default login`)

### 1. Local Agent Execution (CLI)

1. Clone the repository and navigate to the project directory:
   ```bash
   cd devpulse-agent
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Run the agent locally using `agents-cli`:
   ```bash
   uv run agents-cli run "Check health of auth-api service"
   ```

4. Launch the ADK Web interface:
   ```bash
   uv run adk web --port 8080 --allow_origins "*" --reload_agents
   ```

---

### 2. Local Web Frontend Execution

1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```

2. Export environment variables for your deployed Reasoning Engine:
   ```bash
   export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_ID>/locations/<LOCATION>/reasoningEngines/<ENGINE_ID>"
   export AGENT_DIRECTORY="app"
   ```

3. Run the FastAPI proxy server:
   ```bash
   uv run python main.py
   ```
   Access the chat interface in your browser at `http://localhost:8080`.

---

### 3. Deploying to Google Cloud

#### Deploy Agent to Agent Runtime:
```bash
agents-cli deploy \
  --project <PROJECT_ID> \
  --region us-east1 \
  --service-name devpulse-agent \
  --update-env-vars GOOGLE_MAPS_API_KEY=<YOUR_MAPS_API_KEY>
```

#### Deploy Web Frontend to Cloud Run:
```bash
gcloud run deploy devpulse-frontend \
  --source=./frontend \
  --project=<PROJECT_ID> \
  --region=us-east1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="<REASONING_ENGINE_RESOURCE_NAME>",AGENT_DIRECTORY="app"
```

#### Grant Cloud Run IAM Permissions:
```bash
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member="serviceAccount:<CLOUD_RUN_SERVICE_ACCOUNT>" \
  --role="roles/aiplatform.user"
```
