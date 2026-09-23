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

"""Script to create a Serverless Vertex AI RAG Corpus and import text file."""

import vertexai
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr

PROJECT_ID = "qwiklabs-gcp-01-d85174ee446b"
LOCATION = "us-central1"
GCS_PATH = "gs://devpulse-assets-qwiklabs-gcp-01-d85174ee446b/rag/pg49513.txt"

PARSING_PROMPT = (
    "Extract the individual useful facts, remedies, and herbal descriptions described in this text. "
    "Ignore and omit all metadata, boilerplate, licensing text, and table of contents. "
    "Output clean, self-contained prose."
)

vertexai.init(project=PROJECT_ID, location=LOCATION)

# 1. Switch region's RAG managed DB to serverless mode
cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
try:
    rag.update_rag_engine_config(
        rag_engine_config=rag.RagEngineConfig(
            name=cfg,
            rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
        )
    )
    print("Updated RAG engine config to serverless mode.")
except Exception as e:
    print(f"Serverless config notice: {e}")

# 2. Create corpus in serverless mode with text-embedding-005
corpus = rag.create_corpus(
    display_name="culpeper-herbal-corpus",
    embedding_model_config=rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-005"
    ),
)
print("CREATED_CORPUS_NAME:", corpus.name)

# 3. Import + parse + chunk + embed
print(f"Importing files from {GCS_PATH} into corpus {corpus.name}...")
resp = rag.import_files(
    corpus_name=corpus.name,
    paths=[GCS_PATH],
    transformation_config=rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
    ),
    llm_parser=rag.LlmParserConfig(
        model_name="gemini-1.5-flash", custom_parsing_prompt=PARSING_PROMPT
    ),
)
print("IMPORTED_FILES_COUNT:", getattr(resp, "imported_rag_files_count", 1))
