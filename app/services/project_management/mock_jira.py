from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
from app.utils.logger import ColorLogger as log
from .base import ProjectManagementTool

class MockJiraProjectManagement(ProjectManagementTool):
    """
    Mock implementation of the Jira API for development and testing purposes.
    This allows the application to function without actual Jira credentials.
    """
    
    def __init__(self):
        # In-memory storage for mock issues
        self._issues = {}
        log.info("Initialized Mock Jira Project Management")
    
    async def create_issue(self, title: str, description: str, 
                          priority: str = "Medium", 
                          labels: List[str] = None,
                          lock_description: bool = True) -> Dict[str, Any]:
        """
        Create a mock issue.
        
        Args:
            title: Issue title
            description: Issue description
            priority: Issue priority (Low, Medium, High)
            labels: List of labels to apply to the issue
            
        Returns:
            Dictionary with issue details
        """
        # Generate a mock issue ID
        issue_id = str(uuid.uuid4())
        
        # Create the issue object
        issue = {
            "id": issue_id,
            "key": f"MOCK-{issue_id[:8].upper()}",
            "title": title,
            "description": description,
            "priority": priority,
            "labels": labels or [],
            "status": "To Do",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "url": f"https://mock-jira.example.com/browse/MOCK-{issue_id[:8].upper()}",
            "description_locked": lock_description
        }
        
        # Store the issue
        self._issues[issue_id] = issue
        
        log.info(f"Created mock Jira issue: {issue['key']} - {title}")
        
        return issue
    
    async def get_all_issues(self) -> List[Dict[str, Any]]:
        """
        Get all mock issues.
        
        Returns:
            List of issue dictionaries
        """
        return list(self._issues.values())
    
    async def get_issue(self, issue_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific mock issue.
        
        Args:
            issue_id: ID of the issue to retrieve
            
        Returns:
            Issue dictionary if found, None otherwise
        """
        return self._issues.get(issue_id)
    
    async def update_issue_status(self, issue_id: str, status: str) -> Optional[Dict[str, Any]]:
        """
        Update the status of a mock issue.
        
        Args:
            issue_id: ID of the issue to update
            status: New status
            
        Returns:
            Updated issue dictionary if found, None otherwise
        """
        if issue_id in self._issues:
            self._issues[issue_id]["status"] = status
            self._issues[issue_id]["updated_at"] = datetime.now().isoformat()
            return self._issues[issue_id]
        return None
    
    async def update_issue(self, issue_id: str, title: str = None, 
                          description: str = None, priority: str = None, 
                          labels: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update a mock issue.
        
        Args:
            issue_id: ID of the issue to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional)
            labels: New labels (optional)
            
        Returns:
            Updated issue dictionary if found, None otherwise
        """
        if issue_id in self._issues:
            issue = self._issues[issue_id]
            
            if title is not None:
                issue["title"] = title
            if description is not None:
                issue["description"] = description
            if priority is not None:
                issue["priority"] = priority
            if labels is not None:
                issue["labels"] = labels
                
            issue["updated_at"] = datetime.now().isoformat()
            return issue
        return None
    
    async def delete_issue(self, issue_id: str) -> bool:
        """
        Delete a mock issue.
        
        Args:
            issue_id: ID of the issue to delete
            
        Returns:
            True if deleted, False if not found
        """
        if issue_id in self._issues:
            del self._issues[issue_id]
            return True
        return False
