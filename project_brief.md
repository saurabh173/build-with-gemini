# My agent: Dev & IT Support Assistant (DevPulse)

One-liner: A conversational agent that helps developers and IT teams troubleshoot technical errors, query knowledge bases, and manage support tickets.

Tool coverage:
- Memory: Remembers developer tech stack, active environment settings, and recent ticket history across sessions.
- Tools: `search_knowledge_base` (search technical docs and runbooks), `create_support_ticket` (log issues to system), and `fetch_system_status` (check service health).
- Catalog/UI: IT ticket dashboard, knowledge base solution cards, and diagnostic status tables.
- Image gen: Generates system architecture diagrams or diagnostic workflow charts.
- Sandbox: Evaluates diagnostic code snippets, parses log files, or calculates uptime metrics.

Core rails (everyone): memory, tools, eval, deploy, frontend
My stretch menu (pick later): A2UI ticket cards, RAG Engine knowledge base, Code Sandbox diagnostics
First eval question: "Given a '504 Gateway Timeout' error in service auth-api, search the runbook and output the root cause and a severity 2 support ticket."
