import aiohttp
import json
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.config import settings
from app.utils.logger import ColorLogger as log
from .base import ProjectManagementTool


class JiraProjectManagement(ProjectManagementTool):
    """
    Jira implementation of the ProjectManagementTool interface.
    """
    
    def __init__(self):
        self.server_url = settings.JIRA_SERVER_URL
        self.email = settings.JIRA_EMAIL
        self.api_token = settings.JIRA_API_TOKEN
        self.project_key = settings.JIRA_PROJECT_KEY
        self.issue_type = settings.JIRA_ISSUE_TYPE
        
        # Remove trailing slash if present
        if self.server_url.endswith('/'):
            self.server_url = self.server_url[:-1]
            
        self.api_url = f"{self.server_url}/rest/api/3"
        
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to the Jira API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response data as dictionary
        """
        url = f"{self.api_url}/{endpoint}"
        auth = aiohttp.BasicAuth(self.email, self.api_token)
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Log the request details for debugging
        log.info(f"Making request to Jira API: {method} {url}")
        if data:
            log.info(f"Request data: {data}")
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method=method,
                    url=url,
                    auth=auth,
                    headers=headers,
                    json=data
                ) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        log.error(f"Jira API error: {response.status} - {error_text}")
                        return {"error": error_text, "status_code": response.status}
                    
                    # Handle 204 No Content responses (common for PUT/DELETE operations)
                    if response.status == 204:
                        return {"success": True}
                    
                    # For other successful responses, parse JSON
                    try:
                        return await response.json()
                    except Exception as e:
                        # If response cannot be parsed as JSON, return text content
                        content = await response.text()
                        return {"content": content, "success": True}
            except Exception as e:
                log.error(f"Error making request to Jira API: {str(e)}")
                return {"error": str(e)}
    
    async def create_issue(self, title: str, description: str, **kwargs) -> Dict[str, Any]:
        """
        Create an issue in Jira.
        
        Args:
            title: The title/summary of the issue
            description: The description of the issue
            **kwargs: Additional fields for the issue
                - priority: Issue priority (e.g., "High", "Medium", "Low")
                - labels: List of labels to add to the issue
                - assignee: Account ID of the assignee
                - lock_description: Boolean to indicate if description should be non-editable (default: True)
                
        Returns:
            Dict containing the created issue details
        """
        log.info(f"Creating Jira issue: {title}")
        
        # Format description for Jira's Atlassian Document Format
        description_adf = {
            "version": 1,
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": description
                        }
                    ]
                }
            ]
        }
        
        # Build the issue data
        issue_data = {
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "summary": title,
                "description": description_adf,
                "issuetype": {
                    "name": self.issue_type
                }
            }
        }
        
        # Check if we should lock the description field
        lock_description = kwargs.get("lock_description", True)
        
        # Add optional fields if provided
        if "priority" in kwargs:
            issue_data["fields"]["priority"] = {
                "name": kwargs["priority"]
            }
            
        if "labels" in kwargs and isinstance(kwargs["labels"], list):
            issue_data["fields"]["labels"] = kwargs["labels"]
            
        if "assignee" in kwargs:
            issue_data["fields"]["assignee"] = {
                "id": kwargs["assignee"]
            }
        
        response = await self._make_request("POST", "issue", issue_data)
        
        if "error" in response:
            log.error(f"Failed to create Jira issue: {response['error']}")
        else:
            issue_key = response.get('key')
            log.success(f"Successfully created Jira issue with ID: {issue_key or 'Unknown'}")
            
            # Set jira.issue.editable=false to make the entire issue non-editable
            if issue_key and lock_description:
                try:
                    # Set the issue.editable property to false
                    editable_data = {
                        "jira.issue.editable": "false"
                    }
                    
                    # Use the properties endpoint to set the issue as non-editable
                    editable_response = await self._make_request(
                        "PUT",
                        f"issue/{issue_key}/properties/jira.issue.editable",
                        editable_data
                    )
                    
                    if editable_response and "error" in editable_response:
                        log.warning(f"Failed to set issue as non-editable: {editable_response['error']}")
                    else:
                        log.success(f"Successfully set issue {issue_key} as non-editable")
                except Exception as e:
                    log.warning(f"Error setting issue as non-editable: {str(e)}")
            
            # If we need to lock the description field and issue was created successfully
            if lock_description and issue_key:
                try:
                    # Add a comment to the issue indicating that the description is locked
                    comment_data = {
                        "body": {
                            "version": 1,
                            "type": "doc",
                            "content": [
                                {
                                    "type": "panel",
                                    "attrs": {
                                        "panelType": "warning"
                                    },
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "text": "⚠️ IMPORTANT: This issue is linked to a legal obligation. The description should not be modified.",
                                                    "marks": [{"type": "strong"}]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                    
                    # Add the comment to the issue
                    try:
                        comment_response = await self._make_request(
                            "POST",
                            f"issue/{issue_key}/comment",
                            comment_data
                        )
                        
                        if comment_response and "error" in comment_response:
                            log.warning(f"Failed to add lock comment: {comment_response['error']}")
                        else:
                            log.success(f"Added description lock notice to issue {issue_key}")
                    except Exception as e:
                        log.warning(f"Error adding comment: {str(e)}")
                    
                    # Set the issue.editable=false property to make the description field non-editable
                    try:
                        # This is the key part that makes the description non-editable in Jira UI
                        editable_data = {
                            "fields": {
                                "description": {
                                    "editable": False
                                }
                            }
                        }
                        
                        # Use the field configuration endpoint to make the description field non-editable
                        editable_response = await self._make_request(
                            "PUT",
                            f"issue/{issue_key}/editable",
                            editable_data
                        )
                        
                        if editable_response and "error" in editable_response:
                            log.warning(f"Failed to set description as non-editable: {editable_response['error']}")
                        else:
                            log.success(f"Successfully set description field as non-editable for issue {issue_key}")
                            
                        # Try another approach - set field properties directly
                        field_props = {
                            "update": {
                                "issueProperties": [
                                    {
                                        "key": "description.editable",
                                        "value": False
                                    }
                                ]
                            }
                        }
                        
                        props_response = await self._make_request(
                            "PUT",
                            f"issue/{issue_key}",
                            field_props
                        )
                        
                        if props_response and "error" in props_response:
                            log.warning(f"Failed to set issue properties: {props_response['error']}")
                        
                    except Exception as e:
                        log.warning(f"Error setting editable property: {str(e)}")
                        
                except Exception as e:
                    log.error(f"Error while trying to lock description field: {str(e)}")
            
        return response
    
    async def get_issue(self, issue_id: str) -> Dict[str, Any]:
        """
        Get issue details by ID.
        
        Args:
            issue_id: The ID of the issue to retrieve
            
        Returns:
            Dict containing the issue details
        """
        log.info(f"Getting Jira issue: {issue_id}")
        response = await self._make_request("GET", f"issue/{issue_id}")
        
        if "error" in response:
            log.error(f"Failed to get Jira issue {issue_id}: {response['error']}")
            
        return response
    
    async def update_issue(self, issue_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing issue.
        
        Args:
            issue_id: The ID of the issue to update
            **kwargs: Fields to update
                - title/summary: The title/summary of the issue
                - description: The description of the issue
                - priority: Issue priority (e.g., "High", "Medium", "Low")
                - labels: List of labels to add to the issue
                - assignee: Account ID of the assignee
                - status: The status to transition the issue to
                
        Returns:
            Dict containing the updated issue details
        """
        log.info(f"Updating Jira issue: {issue_id}")
        
        update_data = {"fields": {}}
        
        # Update summary if provided
        if "title" in kwargs or "summary" in kwargs:
            summary = kwargs.get("title", kwargs.get("summary"))
            update_data["fields"]["summary"] = summary
            
        # Update description if provided
        if "description" in kwargs:
            description_adf = {
                "version": 1,
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": kwargs["description"]
                            }
                        ]
                    }
                ]
            }
            update_data["fields"]["description"] = description_adf
            
        # Update priority if provided
        if "priority" in kwargs:
            # Jira expects specific priority names like "Highest", "High", "Medium", "Low", "Lowest"
            # Map common variations to standard Jira priority names
            priority_map = {
                "highest": "Highest",
                "higher": "High",
                "high": "High",
                "medium": "Medium",
                "normal": "Medium",
                "low": "Low",
                "lowest": "Lowest"
            }
            
            priority_value = kwargs["priority"].lower()
            standard_priority = priority_map.get(priority_value, "Medium")
            
            update_data["fields"]["priority"] = {
                "name": standard_priority
            }
            
        # Update labels if provided
        if "labels" in kwargs and isinstance(kwargs["labels"], list):
            update_data["fields"]["labels"] = kwargs["labels"]
            
        # Completely remove assignee handling
        if "assignee" in kwargs:
            del kwargs["assignee"]
        
        response = await self._make_request("PUT", f"issue/{issue_id}", update_data)
        
        # Handle status transition if provided
        if "status" in kwargs and "error" not in response:
            # Get available transitions
            transitions = await self._make_request("GET", f"issue/{issue_id}/transitions")
            
            if "error" not in transitions and "transitions" in transitions:
                # Find the transition ID for the requested status
                transition_id = None
                for transition in transitions["transitions"]:
                    if transition["to"]["name"].lower() == kwargs["status"].lower():
                        transition_id = transition["id"]
                        break
                
                if transition_id:
                    # Perform the transition
                    transition_data = {
                        "transition": {
                            "id": transition_id
                        }
                    }
                    await self._make_request("POST", f"issue/{issue_id}/transitions", transition_data)
        
        # No assignee handling
        
        if "error" in response:
            log.error(f"Failed to update Jira issue {issue_id}: {response['error']}")
        else:
            log.success(f"Successfully updated Jira issue: {issue_id}")
            
        return response
    

    async def delete_issue(self, issue_id: str) -> bool:
        """
        Delete an issue.
        
        Args:
            issue_id: The ID of the issue to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        log.info(f"Deleting Jira issue: {issue_id}")
        response = await self._make_request("DELETE", f"issue/{issue_id}")
        
        if "error" in response:
            log.error(f"Failed to delete Jira issue {issue_id}: {response['error']}")
            return False
        
        log.success(f"Successfully deleted Jira issue: {issue_id}")
        return True
        
    async def search_issues(self, jql: str = None) -> Dict[str, Any]:
        """
        Search for issues in Jira using JQL (Jira Query Language).
        
        Args:
            jql: JQL query string to search with. If None, will search for all issues in the project.
            
        Returns:
            Dict containing the search results
        """
        log.info("Searching for Jira issues")
        
        # If no JQL is provided, search for all issues in the project
        if jql is None:
            jql = f"project = {self.project_key} ORDER BY created DESC"
        
        # Build the search request
        search_data = {
            "jql": jql,
            "startAt": 0,
            "maxResults": 50,  # Limit to 50 results by default
            "fields": ["summary", "description", "status", "assignee", "created", "updated", "priority", "labels"]
        }
        
        response = await self._make_request("POST", "search", search_data)
        
        if "error" in response:
            log.error(f"Failed to search Jira issues: {response['error']}")
        else:
            issue_count = response.get("total", 0)
            log.success(f"Successfully retrieved {issue_count} Jira issues")
            
        return response
