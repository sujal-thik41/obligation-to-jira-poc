from typing import Dict, Any, List, Optional
from app.services.project_management.factory import ProjectManagementFactory
from app.utils.logger import ColorLogger as log


async def create_obligation_issue(obligation: Dict[str, Any], party_name: str, 
                                 tool_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Create an issue in the project management tool for a legal obligation.
    
    Args:
        obligation: The obligation dictionary containing details
        party_name: The name of the party responsible for the obligation
        tool_name: Optional name of the project management tool to use
        
    Returns:
        Dict containing the created issue details
    """
    try:
        # Get the appropriate project management tool
        pm_tool = ProjectManagementFactory.get_tool(tool_name)
        
        # Extract obligation details
        obligation_text = obligation.get("obligation_text", "")
        section = obligation.get("section", "Unknown")
        deadline = obligation.get("deadline", "Not specified")
        priority = obligation.get("priority", "Medium")
        
        # Create a descriptive title
        title = f"Legal Obligation: {obligation_text[:50]}..." if len(obligation_text) > 50 else f"Legal Obligation: {obligation_text}"
        
        # Create a detailed description
        description = f"""
## Legal Obligation Details

**Obligation Text:**
{obligation_text}

**Responsible Party:** {party_name}

**Section:** {section}

**Deadline:** {deadline}

**Additional Notes:**
This obligation was automatically extracted from a legal document.
"""
        
        # Add labels for better organization
        labels = ["legal-obligation", f"party-{party_name.lower().replace(' ', '-')}"]
        
        # Map priority from obligation to Jira priority
        priority = "Medium"  # Default priority
        if deadline and "immediate" in deadline.lower():
            priority = "High"
        elif deadline and "no" in deadline.lower() and "deadline" in deadline.lower():
            priority = "Low"
        
        # Create the issue in the project management tool
        log.info(f"Creating issue for obligation: {obligation_text[:50]}...")
        issue = await pm_tool.create_issue(
            title=title,
            description=description,
            priority=priority,
            labels=labels,
            lock_description=True  # Always lock the description for legal obligations
        )
        
        return issue
    except Exception as e:
        log.error(f"Error creating issue for obligation: {str(e)}")
        return {"error": str(e)}


async def create_issues_for_all_obligations(obligations_data: List[Dict[str, Any]], 
                                           tool_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Create issues for all obligations in the provided data.
    
    Args:
        obligations_data: List of obligation data dictionaries
        tool_name: Optional name of the project management tool to use
        
    Returns:
        List of responses from issue creation
    """
    results = []
    
    # Process each result in the obligations data
    for result in obligations_data:
        if "parties" in result:
            for party in result["parties"]:
                party_name = party["name"]
                
                if "obligations" in party:
                    log.info(f"Processing {len(party['obligations'])} obligations for {party_name}")
                    
                    for obligation in party["obligations"]:
                        response = await create_obligation_issue(obligation, party_name, tool_name)
                        results.append({
                            "party": party_name,
                            "obligation": obligation,
                            "issue_response": response
                        })
    
    return results
