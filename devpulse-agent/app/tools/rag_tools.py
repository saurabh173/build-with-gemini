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

"""RAG Engine retrieval tools for DevPulse."""

import vertexai
from vertexai.preview import rag

PROJECT_ID = "qwiklabs-gcp-01-d85174ee446b"
RAG_LOCATION = "us-central1"
CORPUS_NAME = (
    "projects/414535294406/locations/us-central1/ragCorpora/8812620880996728832"
)


def query_knowledge_base(query: str) -> str:
    """Searches the grounded RAG knowledge base corpus (Culpeper's Complete Herbal & technical docs) for relevant passages.

    Args:
        query: What to look up or search for in the knowledge base.

    Returns:
        Matched passages from the corpus or a notice if no relevant content is found.
    """
    vertexai.init(project=PROJECT_ID, location=RAG_LOCATION)
    try:
        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=CORPUS_NAME)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=4),
        )
        contexts = getattr(resp.contexts, "contexts", [])
        passages = [
            c.text.strip() for c in contexts if getattr(c, "text", "").strip()
        ]
        if not passages:
            return "No relevant passages found in the knowledge base."
        return "\n\n---\n\n".join(passages)
    except Exception as e:
        return f"Knowledge base lookup error: {str(e)}"
