# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types
from app.tools.firestore_tools import (
    create_support_ticket,
    get_support_ticket,
    list_support_tickets,
    update_ticket_status,
)
from app.tools.health_tools import fetch_service_health
from app.tools.external_status_tools import check_github_platform_status
from app.tools.maps_tools import geocode_address, find_nearby_places
from app.tools.rag_tools import query_knowledge_base
from app.tools.image_tools import generate_system_diagram


async def generate_memories_callback(callback_context: CallbackContext):
    """Callback to extract durable memories after each turn."""
    await callback_context.add_session_to_memory()
    return None


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name="projects/414535294406/locations/us-east1/reasoningEngines/5127587869296164864/sandboxEnvironments/632562233599066112"
    ),
    instruction=(
        "You are DevPulse, a Developer and IT Support Assistant. You assist developers "
        "and IT engineers with troubleshooting technical issues, tracking system status, "
        "and managing support tickets in Firestore.\n"
        "You have access to tools for creating, looking up, listing, and updating support tickets.\n"
        "You also have a secure Agent Engine Python code execution sandbox. To run code safely in the sandbox, write standard ```python code blocks."
    ),
    tools=[
        PreloadMemoryTool(),
        query_knowledge_base,
        generate_system_diagram,
        fetch_service_health,
        check_github_platform_status,
        geocode_address,
        find_nearby_places,
        create_support_ticket,
        get_support_ticket,
        list_support_tickets,
        update_ticket_status,
        get_weather,
        get_current_time,
    ],
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
