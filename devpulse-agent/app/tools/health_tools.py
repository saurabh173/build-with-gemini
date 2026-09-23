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

"""Service health inspection tools for DevPulse."""

import time
import urllib.error
import urllib.request


def fetch_service_health(service_name: str) -> str:
    """Checks the live health, latency, and operational status of a service endpoint.

    Args:
        service_name: Name or ID of the service (e.g., 'auth-api', 'user-service', 'notification-service').

    Returns:
        Formatted summary string with status, latency in milliseconds, and HTTP status code.
    """
    clean_name = service_name.lower().strip()

    endpoints = {
        "auth-api": "https://httpbin.org/status/200",
        "user-service": "https://httpbin.org/status/200",
        "notification-service": "https://httpbin.org/status/200",
    }

    target_url = endpoints.get(clean_name, "https://httpbin.org/status/200")

    start_time = time.time()
    try:
        req = urllib.request.Request(
            target_url, headers={"User-Agent": "DevPulse-HealthChecker/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            status_code = response.getcode()
            status_text = "HEALTHY" if status_code == 200 else "DEGRADED"
            return (
                f"Service: '{clean_name}'\n"
                f"Status: {status_text} (HTTP {status_code})\n"
                f"Latency: {latency_ms} ms\n"
                f"Endpoint Checked: {target_url}"
            )
    except urllib.error.HTTPError as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return (
            f"Service: '{clean_name}'\n"
            f"Status: DEGRADED (HTTP {e.code})\n"
            f"Latency: {latency_ms} ms\n"
            f"Details: {e.reason}"
        )
    except Exception as e:
        return f"Service: '{clean_name}'\nStatus: UNREACHABLE\nDetails: {str(e)}"
