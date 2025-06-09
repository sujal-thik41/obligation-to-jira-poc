from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class ProjectManagementTool(ABC):
    """
    Abstract base class for project management tools.
    Any new project management tool integration should implement this interface.
    """
    
    @abstractmethod
    async def create_issue(self, title: str, description: str, **kwargs) -> Dict[str, Any]:
        """
        Create an issue in the project management tool.
        
        Args:
            title: The title of the issue
            description: The description of the issue
            **kwargs: Additional arguments specific to the project management tool
            
        Returns:
            Dict containing the created issue details
        """
        pass
    
    @abstractmethod
    async def get_issue(self, issue_id: str) -> Dict[str, Any]:
        """
        Get issue details by ID.
        
        Args:
            issue_id: The ID of the issue to retrieve
            
        Returns:
            Dict containing the issue details
        """
        pass
    
    @abstractmethod
    async def update_issue(self, issue_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing issue.
        
        Args:
            issue_id: The ID of the issue to update
            **kwargs: Fields to update
            
        Returns:
            Dict containing the updated issue details
        """
        pass
    
    @abstractmethod
    async def delete_issue(self, issue_id: str) -> bool:
        """
        Delete an issue.
        
        Args:
            issue_id: The ID of the issue to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
