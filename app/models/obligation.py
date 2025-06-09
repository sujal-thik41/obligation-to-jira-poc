from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class Obligation(BaseModel):
    """Model representing a single obligation extracted from a document."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    obligation_text: str
    section: Optional[str] = None
    deadline: Optional[str] = None
    party_name: str
    priority: str = "Medium"  # Default priority is Medium
    source_document: Optional[str] = None
    source_page: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    jira_issue_id: Optional[str] = None
    
    def update(self, **kwargs):
        """Update obligation fields and set updated_at timestamp."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()


class ObligationUpdate(BaseModel):
    """Model for updating obligation details."""
    obligation_text: Optional[str] = None
    section: Optional[str] = None
    deadline: Optional[str] = None
    party_name: Optional[str] = None
    priority: Optional[str] = None


class ObligationResponse(BaseModel):
    """Model for obligation response with pagination."""
    obligations: List[Obligation]
    total: int
    page: int
    page_size: int
    total_pages: int
