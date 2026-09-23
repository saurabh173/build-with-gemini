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

"""Seed script for DevPulse Firestore support_tickets collection."""

import datetime
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-01-d85174ee446b"
COLLECTION_NAME = "support_tickets"

SEED_TICKETS = [
    {
        "ticket_id": "TICK-101",
        "title": "504 Gateway Timeout error in auth-api service",
        "service": "auth-api",
        "severity": "SEV-2",
        "status": "OPEN",
        "description": "High response latency (> 5000ms) leading to 504 Gateway Timeout errors during user authentication.",
        "created_by": "alex@devpulse.internal",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "notes": ["Initial triage: Upstream Redis token cache unreachable."],
    },
    {
        "ticket_id": "TICK-102",
        "title": "Database connection pool exhaustion in user-service",
        "service": "user-service",
        "severity": "SEV-1",
        "status": "IN_PROGRESS",
        "description": "Max connections (100/100) reached on primary PostgreSQL instance causing cascading HTTP 500 errors.",
        "created_by": "sre-oncall@devpulse.internal",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "notes": ["Workaround applied: Restarted app pods to drop stale connections. Investigating connection leak."],
    },
    {
        "ticket_id": "TICK-103",
        "title": "Memory leak on background worker in notification-service",
        "service": "notification-service",
        "severity": "SEV-3",
        "status": "RESOLVED",
        "description": "Worker memory usage increases linearly until OOMKilled every 12 hours.",
        "created_by": "dev-team@devpulse.internal",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "notes": ["Patched unclosed HTTP session objects in webhooks dispatcher.", "Verified stable memory consumption."],
    },
]


def seed_database():
    """Populates Firestore with initial seed ticket items."""
    print(f"Connecting to Firestore database for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection(COLLECTION_NAME)

    for ticket in SEED_TICKETS:
        doc_ref = collection.document(ticket["ticket_id"])
        doc_ref.set(ticket)
        print(f"Seeded ticket: {ticket['ticket_id']} ({ticket['title']})")

    print(f"\nSuccessfully seeded {len(SEED_TICKETS)} tickets into Firestore collection '{COLLECTION_NAME}'!")


if __name__ == "__main__":
    seed_database()
