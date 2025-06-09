from typing import Dict, Any, List, Optional
from app.services.project_management.factory import ProjectManagementFactory
from app.utils.logger import ColorLogger as log


async def get_all_issues(project_tool: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get all issues from the project management tool.
    
    Args:
        project_tool: Optional name of the project management tool to use
        
    Returns:
        List of issues
    """
    try:
        pm_tool = ProjectManagementFactory.get_tool(project_tool)
        
        # This will need to be implemented in the specific project management tool classes
        # For now, we'll use a generic approach for Jira
        if hasattr(pm_tool, "search_issues"):
            return await pm_tool.search_issues()
        else:
            log.warning(f"The selected project management tool doesn't support searching for issues")
            return []
    except Exception as e:
        log.error(f"Error getting issues: {str(e)}")
        return []


async def get_issue_details(issue_id: str, project_tool: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed information about a specific issue.
    
    Args:
        issue_id: ID of the issue to retrieve
        project_tool: Optional name of the project management tool to use
        
    Returns:
        Issue details
    """
    try:
        pm_tool = ProjectManagementFactory.get_tool(project_tool)
        return await pm_tool.get_issue(issue_id)
    except Exception as e:
        log.error(f"Error getting issue details: {str(e)}")
        return {"error": str(e)}


async def update_issue_status(issue_id: str, status: str, project_tool: Optional[str] = None) -> Dict[str, Any]:
    """
    Update the status of an issue.
    
    Args:
        issue_id: ID of the issue to update
        status: New status for the issue
        project_tool: Optional name of the project management tool to use
        
    Returns:
        Updated issue details
    """
    try:
        pm_tool = ProjectManagementFactory.get_tool(project_tool)
        return await pm_tool.update_issue(issue_id, status=status)
    except Exception as e:
        log.error(f"Error updating issue status: {str(e)}")
        return {"error": str(e)}


async def update_issue_details(issue_id: str, update_data: Dict[str, Any], project_tool: Optional[str] = None) -> Dict[str, Any]:
    """
    Update various details of an issue.
    
    Args:
        issue_id: ID of the issue to update
        update_data: Dictionary containing fields to update
        project_tool: Optional name of the project management tool to use
        
    Returns:
        Updated issue details
    """
    try:
        pm_tool = ProjectManagementFactory.get_tool(project_tool)
        return await pm_tool.update_issue(issue_id, **update_data)
    except Exception as e:
        log.error(f"Error updating issue details: {str(e)}")
        return {"error": str(e)}


async def delete_issue(issue_id: str, project_tool: Optional[str] = None) -> Dict[str, Any]:
    """
    Delete an issue.
    
    Args:
        issue_id: ID of the issue to delete
        project_tool: Optional name of the project management tool to use
        
    Returns:
        Success status
    """
    try:
        pm_tool = ProjectManagementFactory.get_tool(project_tool)
        success = await pm_tool.delete_issue(issue_id)
        
        if success:
            return {"success": True, "message": f"Issue {issue_id} successfully deleted"}
        else:
            return {"success": False, "message": f"Failed to delete issue {issue_id}"}
    except Exception as e:
        log.error(f"Error deleting issue: {str(e)}")
        return {"success": False, "error": str(e)}
