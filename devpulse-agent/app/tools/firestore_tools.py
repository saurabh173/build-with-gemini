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

"""Firestore tools for managing DevPulse support tickets."""

import datetime
from google.cloud import firestore

# IMPORTANT: Project ID is explicitly hardcoded as required for Cloud Run / Agent Platform deployment
# to prevent google.auth.default() or GOOGLE_CLOUD_PROJECT from resolving to numeric project numbers.
PROJECT_ID = "qwiklabs-gcp-01-d85174ee446b"
COLLECTION_NAME = "support_tickets"


def _get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with the hardcoded GCP project ID."""
    return firestore.Client(project=PROJECT_ID)


def create_support_ticket(
    ticket_id: str,
    title: str,
    service: str,
    severity: str,
    description: str,
    created_by: str = "dev_team",
) -> str:
    """Creates a new support ticket in the Firestore database.

    Args:
        ticket_id: Unique identifier for the ticket (e.g., 'TICK-104').
        title: Short title summarizing the issue.
        service: Name of affected service (e.g., 'auth-api', 'user-service').
        severity: Severity level (e.g., 'SEV-1', 'SEV-2', 'SEV-3').
        description: Detailed explanation of error logs or symptoms.
        created_by: Email or username of the reporter (default: 'dev_team').

    Returns:
        Confirmation message with ticket details.
    """
    db = _get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(ticket_id)
    
    ticket_data = {
        "ticket_id": ticket_id,
        "title": title,
        "service": service,
        "severity": severity.upper(),
        "status": "OPEN",
        "description": description,
        "created_by": created_by,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "notes": [],
    }
    
    doc_ref.set(ticket_data)
    return (
        f"Support ticket '{ticket_id}' successfully created in Firestore.\n"
        f"Service: {service} | Severity: {severity.upper()} | Status: OPEN\n"
        f"Title: {title}"
    )


def get_support_ticket(ticket_id: str) -> str:
    """Retrieves details of a support ticket from Firestore by ticket ID.

    Args:
        ticket_id: The unique ticket identifier (e.g., 'TICK-101').

    Returns:
        String representation of the ticket details or an error message if not found.
    """
    db = _get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(ticket_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        return f"Ticket '{ticket_id}' not found in Firestore."
        
    data = doc.to_dict()
    notes_str = "\n  - ".join(data.get("notes", [])) if data.get("notes") else "None"
    return (
        f"--- Ticket Details: {data.get('ticket_id')} ---\n"
        f"Title: {data.get('title')}\n"
        f"Service: {data.get('service')}\n"
        f"Severity: {data.get('severity')}\n"
        f"Status: {data.get('status')}\n"
        f"Reporter: {data.get('created_by')}\n"
        f"Created At: {data.get('created_at')}\n"
        f"Description: {data.get('description')}\n"
        f"Resolution Notes:\n  - {notes_str}"
    )


def list_support_tickets(service: str = "", status: str = "") -> str:
    """Lists support tickets stored in Firestore with optional filters.

    Args:
        service: Optional filter by service name (e.g., 'auth-api').
        status: Optional filter by status ('OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED').

    Returns:
        Formatted summary of matching support tickets.
    """
    db = _get_firestore_client()
    query = db.collection(COLLECTION_NAME)
    
    if service:
        query = query.where("service", "==", service)
    if status:
        query = query.where("status", "==", status.upper())
        
    docs = list(query.stream())
    if not docs:
        filters = []
        if service:
            filters.append(f"service='{service}'")
        if status:
            filters.append(f"status='{status.upper()}'")
        filter_str = f" matching {', '.join(filters)}" if filters else ""
        return f"No support tickets found{filter_str}."

    results = []
    for doc in docs:
        d = doc.to_dict()
        results.append(
            f"[{d.get('ticket_id')}] ({d.get('severity')}) {d.get('title')} "
            f"| Service: {d.get('service')} | Status: {d.get('status')}"
        )
        
    return f"Found {len(results)} ticket(s):\n" + "\n".join(results)


def update_ticket_status(ticket_id: str, status: str, notes: str = "") -> str:
    """Updates the status and optional resolution notes of a support ticket.

    Args:
        ticket_id: The ticket ID to update (e.g., 'TICK-101').
        status: New status ('OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED').
        notes: Optional note explaining status update or root cause analysis.

    Returns:
        Confirmation message of the update.
    """
    db = _get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(ticket_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        return f"Cannot update: Ticket '{ticket_id}' not found in Firestore."

    new_status = status.upper()
    updates = {"status": new_status}
    
    if notes:
        existing_notes = doc.to_dict().get("notes", [])
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        existing_notes.append(f"[{timestamp}] {notes}")
        updates["notes"] = existing_notes
        
    doc_ref.update(updates)
    return f"Ticket '{ticket_id}' updated successfully to status '{new_status}'."
