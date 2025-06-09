from typing import Dict, Type
from app.core.config import settings
from .base import ProjectManagementTool
from .jira import JiraProjectManagement
from .mock_jira import MockJiraProjectManagement


class ProjectManagementFactory:
    """
    Factory class for creating project management tool instances.
    This allows easy extension to support additional tools in the future.
    """
    
    # Registry of available project management tools
    _registry: Dict[str, Type[ProjectManagementTool]] = {
        "jira": JiraProjectManagement,
        # Add more tools here as they are implemented
        # "trello": TrelloProjectManagement,
        # "asana": AsanaProjectManagement,
    }
    
    @classmethod
    def get_tool(cls, tool_name: str = None) -> ProjectManagementTool:
        """
        Get an instance of the specified project management tool.
        If no tool is specified, use the default from settings.
        
        Args:
            tool_name: Name of the tool to use (e.g., "jira", "trello")
            
        Returns:
            An instance of the requested ProjectManagementTool
            
        Raises:
            ValueError: If the requested tool is not supported
        """
        # Use default tool if none specified
        if not tool_name:
            tool_name = settings.DEFAULT_PROJECT_MANAGEMENT_TOOL.lower()
        else:
            tool_name = tool_name.lower()
        
        # Check if the tool is supported
        if tool_name not in cls._registry:
            supported_tools = ", ".join(cls._registry.keys())
            raise ValueError(
                f"Unsupported project management tool: {tool_name}. "
                f"Supported tools are: {supported_tools}"
            )
        
        # Use mock implementation for Jira if credentials are not set
        if tool_name == "jira" and (not settings.JIRA_SERVER_URL or not settings.JIRA_API_TOKEN):
            from app.utils.logger import ColorLogger as log
            log.warning("Jira credentials not found. Using mock Jira implementation.")
            return MockJiraProjectManagement()
        
        # Create and return an instance of the tool
        tool_class = cls._registry[tool_name]
        return tool_class()
