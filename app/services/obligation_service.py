from typing import List, Dict, Any, Optional
from app.models.obligation import Obligation, ObligationUpdate
import json
import os
from datetime import datetime
import uuid
from app.utils.logger import ColorLogger as log

# Simple in-memory storage for obligations
# In a production environment, this would be replaced with a database
_obligations_store: List[Obligation] = []

# File path for persistence (simple JSON file)
OBLIGATIONS_FILE = "obligations_data.json"


def _save_obligations_to_file():
    """Save obligations to a JSON file for persistence."""
    try:
        # Custom JSON encoder to handle datetime objects
        def datetime_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
            
        with open(OBLIGATIONS_FILE, "w") as f:
            json.dump([ob.model_dump() for ob in _obligations_store], f, default=datetime_serializer)
    except Exception as e:
        log.error(f"Error saving obligations to file: {str(e)}")


def _load_obligations_from_file():
    """Load obligations from a JSON file if it exists."""
    global _obligations_store
    try:
        if os.path.exists(OBLIGATIONS_FILE):
            with open(OBLIGATIONS_FILE, "r") as f:
                data = json.load(f)
                _obligations_store = [Obligation(**item) for item in data]
                log.info(f"Loaded {len(_obligations_store)} obligations from file")
    except Exception as e:
        log.error(f"Error loading obligations from file: {str(e)}")


# Load obligations when module is imported
_load_obligations_from_file()


def store_obligations(obligations_data: List[Dict[str, Any]]) -> List[Obligation]:
    """
    Store extracted obligations from document analysis.
    
    Args:
        obligations_data: List of obligation data dictionaries
        
    Returns:
        List of stored Obligation objects
    """
    stored_obligations = []
    
    # Process each result in the obligations data
    for result in obligations_data:
        if "parties" in result:
            for party in result["parties"]:
                party_name = party["name"]
                
                if "obligations" in party:
                    log.info(f"Storing {len(party['obligations'])} obligations for {party_name}")
                    
                    for obligation_data in party["obligations"]:
                        obligation = Obligation(
                            obligation_text=obligation_data.get("obligation_text", ""),
                            section=obligation_data.get("section", ""),
                            deadline=obligation_data.get("deadline", "Not specified"),
                            party_name=party_name,
                            source_document=obligation_data.get("source_document", None),
                            source_page=obligation_data.get("page_number", None)
                        )
                        _obligations_store.append(obligation)
                        stored_obligations.append(obligation)
    
    # Save to file for persistence
    _save_obligations_to_file()
    
    return stored_obligations


def get_all_obligations(
    page: int = 1, 
    page_size: int = 10, 
    party_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get all stored obligations with pagination.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        party_name: Filter by party name (optional)
        
    Returns:
        Dictionary with obligations and pagination info
    """
    # Filter by party name if provided
    filtered_obligations = _obligations_store
    if party_name:
        filtered_obligations = [ob for ob in _obligations_store if ob.party_name.lower() == party_name.lower()]
    
    # Calculate pagination
    total_items = len(filtered_obligations)
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
    
    # Ensure page is within valid range
    page = max(1, min(page, total_pages))
    
    # Get paginated results
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_obligations = filtered_obligations[start_idx:end_idx]
    
    # Convert Obligation objects to dictionaries
    paginated_obligations_dict = [ob.model_dump() for ob in paginated_obligations]
    
    return {
        "obligations": paginated_obligations_dict,
        "total": total_items,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "pagination": {
            "has_next": page < total_pages,
            "has_previous": page > 1,
            "next_page": page + 1 if page < total_pages else None,
            "previous_page": page - 1 if page > 1 else None
        }
    }


def get_obligation_by_id(obligation_id: str) -> Optional[Obligation]:
    """
    Get an obligation by its ID.
    
    Args:
        obligation_id: ID of the obligation to retrieve
        
    Returns:
        Obligation object if found, None otherwise
    """
    for obligation in _obligations_store:
        if obligation.id == obligation_id:
            return obligation
    return None


def update_obligation(obligation_id: str, update_data: ObligationUpdate) -> Optional[Obligation]:
    """
    Update an obligation by its ID.
    
    Args:
        obligation_id: ID of the obligation to update
        update_data: Data to update the obligation with
        
    Returns:
        Updated Obligation object if found, None otherwise
    """
    obligation = get_obligation_by_id(obligation_id)
    if obligation:
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        obligation.update(**update_dict)
        
        # Save changes
        _save_obligations_to_file()
        
        return obligation
    return None


def delete_obligation(obligation_id: str) -> bool:
    """
    Delete an obligation by its ID.
    
    Args:
        obligation_id: ID of the obligation to delete
        
    Returns:
        True if deleted, False if not found
    """
    global _obligations_store
    
    for i, obligation in enumerate(_obligations_store):
        if obligation.id == obligation_id:
            _obligations_store.pop(i)
            _save_obligations_to_file()
            return True
    
    return False


def set_jira_issue_id(obligation_id: str, jira_issue_id: str) -> Optional[Obligation]:
    """
    Set the Jira issue ID for an obligation.
    
    Args:
        obligation_id: ID of the obligation
        jira_issue_id: Jira issue ID
        
    Returns:
        Updated Obligation object if found, None otherwise
    """
    obligation = get_obligation_by_id(obligation_id)
    if obligation:
        obligation.jira_issue_id = jira_issue_id
        obligation.updated_at = datetime.now()
        _save_obligations_to_file()
        return obligation
    return None
