"""
Knowledge Base Document - per-business RAG corpus.

Stores user-uploaded documents (FAQ, price list, policies, after-care notes
etc.) along with chunked text and embeddings. The AI assistant retrieves
relevant chunks at query time via the `search_knowledge_base` tool.
"""
from beanie import Document
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class KnowledgeChunk(BaseModel):
    """A single embedded chunk of a knowledge document."""
    text: str
    embedding: List[float] = Field(default_factory=list)  # 1536-d (text-embedding-3-small)
    # Detected language of the chunk text. Used by hybrid retrieval to
    # decide whether keyword scoring is meaningful (same-lang) or whether
    # we should lean on the multilingual embedding alone (cross-lang).
    # One of: tr | en | ru | de | other
    language: str = "other"


class KnowledgeDocument(Document):
    business_id: str
    title: str
    source_type: str = "text"  # text | file
    filename: Optional[str] = None
    mime_type: Optional[str] = None

    # Raw original content (for display/edit)
    raw_content: str = ""

    # Pre-computed chunks ready for retrieval
    chunks: List[KnowledgeChunk] = Field(default_factory=list)

    # Model used for embedding (so we can re-index later if changed)
    embedding_model: str = "text-embedding-3-small"

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "knowledge_documents"
        indexes = ["business_id"]


class KnowledgeGap(Document):
    """
    Customer questions the assistant could NOT confidently answer from the
    knowledge base. Logged automatically so the business owner can spot
    information they should add.
    """
    business_id: str
    question: str
    language: str = "tr"
    session_id: Optional[str] = None
    best_score: float = 0.0          # top retrieval score (0 = no hits)
    hit_count: int = 0                # how many times the same/similar question came up
    status: str = "open"             # open | resolved | dismissed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

    class Settings:
        name = "knowledge_gaps"
        indexes = ["business_id", "status"]
