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

"""External status and cloud platform tools for DevPulse."""

import json
import os
import urllib.error
import urllib.request


def check_github_platform_status(component_name: str = "") -> str:
    """Queries the public GitHub Status API to check operational health of GitHub developer tools.

    Args:
        component_name: Optional filter for specific component (e.g. 'Actions', 'Git Operations', 'Copilot', 'API Requests', 'Webhooks').

    Returns:
        Formatted operational status summary for GitHub platform services.
    """
    api_url = os.getenv(
        "GITHUB_STATUS_API_URL", "https://www.githubstatus.com/api/v2/summary.json"
    )

    try:
        req = urllib.request.Request(
            api_url, headers={"User-Agent": "DevPulse-SupportAgent/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        overall_status = data.get("status", {}).get("description", "Unknown")
        components = data.get("components", [])

        if component_name:
            filtered = [
                c
                for c in components
                if component_name.lower() in c.get("name", "").lower()
            ]
            if not filtered:
                return (
                    f"No GitHub component found matching '{component_name}'. "
                    f"Overall GitHub Status: {overall_status}."
                )

            comp = filtered[0]
            return f"GitHub Component '{comp.get('name')}': Status is '{comp.get('status').upper()}'."

        summary_list = []
        for c in components[:8]:
            if c.get("name"):
                summary_list.append(f"• {c.get('name')}: {c.get('status').upper()}")

        return (
            f"GitHub Platform Status: {overall_status}\n"
            f"Component Breakdown:\n" + "\n".join(summary_list)
        )
    except urllib.error.URLError as e:
        return f"Unable to fetch GitHub platform status: {e.reason}"
    except Exception as e:
        return f"Error querying GitHub Status API: {str(e)}"
