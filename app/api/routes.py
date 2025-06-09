from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, Body, Path
from fastapi.responses import JSONResponse
from datetime import datetime
import json
from app.services.document_reader import extract_text_from_document
from app.services.chunker import chunk_text
from app.services.obligation_extractor import extract_obligation_from_chunks
from app.services.obligation_issue_service import create_issues_for_all_obligations
from app.services.obligation_service import (
    store_obligations,
    get_all_obligations,
    get_obligation_by_id,
    update_obligation,
    delete_obligation,
    set_jira_issue_id
)
from app.services.project_management.issue_service import (
    get_all_issues,
    get_issue_details,
    update_issue_status,
    update_issue_details,
    delete_issue
)
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.models.obligation import ObligationUpdate

# Define Pydantic models for request validation
class IssueStatusUpdate(BaseModel):
    status: str

class IssueDetailsUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    labels: Optional[List[str]] = None

class ObligationBulkCreateRequest(BaseModel):
    obligation_ids: List[str]

router = APIRouter()

@router.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """
    Upload a document (PDF or DOCX) and extract obligations.

    Parameters:
    - file: Document file to analyze (PDF or DOCX)
    - page: Page number for pagination (starts from 1)
    - page_size: Number of obligations per page (max 100)
    """

    # Validate file type
    supported_types = ["application/pdf", 
                      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                      "application/docx"]
    
    if file.content_type not in supported_types:
        raise HTTPException(status_code=400, detail=f"Only PDF and DOCX files are supported. Got: {file.content_type}")

    # Read file bytes (async)
    contents = await file.read()
    pages = extract_text_from_document(contents, file.content_type)
    chunks = chunk_text(pages)

    # Extract all obligations
    all_obligations = await extract_obligation_from_chunks(chunks)
    
    # Add source document info to obligations
    for result in all_obligations:
        if "parties" in result:
            for party in result["parties"]:
                if "obligations" in party:
                    for obligation in party["obligations"]:
                        obligation["source_document"] = file.filename
    
    # Store obligations for later use
    stored_obligations = store_obligations(all_obligations)

    # Calculate pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_obligations = all_obligations[start_idx:end_idx]

    # Calculate total pages
    total_items = len(all_obligations)
    total_pages = (total_items + page_size - 1) // page_size

    return JSONResponse(
        {
            "filename": file.filename,
            "total_chunks": len(chunks),
            "total_obligations": total_items,
            "current_page": page,
            "total_pages": total_pages,
            "page_size": page_size,
            "obligations": paginated_obligations,
            "pagination": {
                "has_next": page < total_pages,
                "has_previous": page > 1,
                "next_page": page + 1 if page < total_pages else None,
                "previous_page": page - 1 if page > 1 else None
            }
        }
    )


@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """
    Upload a PDF file and extract obligations (legacy endpoint).

    Parameters:
    - file: PDF file to analyze
    - page: Page number for pagination (starts from 1)
    - page_size: Number of obligations per page (max 100)
    """
    return await upload_document(file, page, page_size)


@router.post("/create-issues")
async def create_issues(
    obligations_data: List[Dict[str, Any]] = Body(...),
    project_tool: Optional[str] = Query(None, description="Project management tool to use (e.g., jira)")
):
    """
    Create issues in the project management tool for the provided obligations.
    
    Parameters:
    - obligations_data: List of obligation data dictionaries
    - project_tool: Optional project management tool to use (defaults to the one in settings)
    """
    try:
        results = await create_issues_for_all_obligations(obligations_data, project_tool)
        
        # Count successful and failed issue creations
        success_count = 0
        failed_count = 0
        
        for result in results:
            if "issue_response" in result and "error" not in result["issue_response"]:
                success_count += 1
            else:
                failed_count += 1
        
        return JSONResponse(
            {
                "message": f"Created {success_count} issues in the project management tool",
                "success_count": success_count,
                "failed_count": failed_count,
                "results": results
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating issues: {str(e)}")


@router.post("/upload-and-create-issues")
async def upload_and_create_issues(
    file: UploadFile = File(...),
    project_tool: Optional[str] = Query(None, description="Project management tool to use (e.g., jira)")
):
    """
    Upload a document (PDF or DOCX), extract obligations, and create issues in one step.
    
    Parameters:
    - file: Document file to analyze (PDF or DOCX)
    - project_tool: Optional project management tool to use (defaults to the one in settings)
    """
    # Validate file type
    supported_types = ["application/pdf", 
                      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                      "application/docx"]
    
    if file.content_type not in supported_types:
        raise HTTPException(status_code=400, detail=f"Only PDF and DOCX files are supported. Got: {file.content_type}")

    # Read file bytes (async)
    contents = await file.read()
    pages = extract_text_from_document(contents, file.content_type)
    chunks = chunk_text(pages)

    # Extract all obligations
    all_obligations = await extract_obligation_from_chunks(chunks)
    
    # Add source document info to obligations
    for result in all_obligations:
        if "parties" in result:
            for party in result["parties"]:
                if "obligations" in party:
                    for obligation in party["obligations"]:
                        obligation["source_document"] = file.filename
    
    # Store obligations
    stored_obligations = store_obligations(all_obligations)
    
    # Create issues for all obligations
    results = await create_issues_for_all_obligations(all_obligations, project_tool)
    
    # Count successful and failed issue creations
    success_count = 0
    failed_count = 0
    
    for result in results:
        if "issue_response" in result and "error" not in result["issue_response"]:
            success_count += 1
            
            # Update the stored obligation with the Jira issue ID if available
            if "key" in result["issue_response"]:
                obligation_id = None
                if "obligation" in result and "id" in result["obligation"]:
                    obligation_id = result["obligation"]["id"]
                
                if obligation_id:
                    set_jira_issue_id(obligation_id, result["issue_response"]["key"])
        else:
            failed_count += 1
    
    return JSONResponse(
        {
            "filename": file.filename,
            "total_chunks": len(chunks),
            "total_obligations": len(all_obligations),
            "issues_created": success_count,
            "issues_failed": failed_count,
            "results": results
        }
    )


# Obligation Management APIs

@router.get("/obligations")
async def list_obligations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    party_name: Optional[str] = Query(None, description="Filter by party name")
):
    """
    Get all stored obligations with pagination.
    
    Parameters:
    - page: Page number for pagination (starts from 1)
    - page_size: Number of obligations per page (max 100)
    - party_name: Optional filter by party name
    """
    try:
        result = get_all_obligations(page, page_size, party_name)
        
        # Custom JSON encoder for datetime objects
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)
        
        # Convert result to JSON with custom encoder
        json_compatible_result = json.loads(json.dumps(result, cls=DateTimeEncoder))
        return JSONResponse(content=json_compatible_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving obligations: {str(e)}")


@router.get("/obligations/{obligation_id}")
async def get_obligation(
    obligation_id: str = Path(..., description="ID of the obligation to retrieve")
):
    """
    Get details of a specific obligation.
    
    Parameters:
    - obligation_id: ID of the obligation to retrieve
    """
    obligation = get_obligation_by_id(obligation_id)
    if not obligation:
        raise HTTPException(status_code=404, detail=f"Obligation with ID {obligation_id} not found")
    
    # Custom JSON encoder for datetime objects
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return super().default(obj)
    
    # Convert obligation to JSON with custom encoder
    json_compatible_result = json.loads(json.dumps(obligation.model_dump(), cls=DateTimeEncoder))
    return JSONResponse(content=json_compatible_result)


@router.put("/obligations/{obligation_id}")
async def update_obligation_endpoint(
    obligation_id: str = Path(..., description="ID of the obligation to update"),
    update_data: ObligationUpdate = Body(...)
):
    """
    Update details of an obligation.
    
    Parameters:
    - obligation_id: ID of the obligation to update
    - update_data: Updated obligation details
    """
    try:
        # First, get the current obligation to check if it has a Jira issue
        current_obligation = get_obligation_by_id(obligation_id)
        if not current_obligation:
            raise HTTPException(status_code=404, detail=f"Obligation with ID {obligation_id} not found")
        
        # If the obligation has a Jira issue and the update includes changing the text, prevent it
        if current_obligation.jira_issue_id and update_data.obligation_text is not None:
            if update_data.obligation_text != current_obligation.obligation_text:
                raise HTTPException(
                    status_code=400, 
                    detail="Cannot modify obligation text after a Jira issue has been created"
                )
        
        # Proceed with the update
        updated_obligation = update_obligation(obligation_id, update_data)
        if not updated_obligation:
            raise HTTPException(status_code=404, detail=f"Obligation with ID {obligation_id} not found")
        
        # Custom JSON encoder for datetime objects
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)
        
        # Convert updated_obligation to JSON with custom encoder
        json_compatible_result = json.loads(json.dumps(updated_obligation.model_dump(), cls=DateTimeEncoder))
        return JSONResponse(content=json_compatible_result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating obligation: {str(e)}")


@router.delete("/obligations/{obligation_id}")
async def delete_obligation_endpoint(
    obligation_id: str = Path(..., description="ID of the obligation to delete")
):
    """
    Delete an obligation.
    
    Parameters:
    - obligation_id: ID of the obligation to delete
    """
    try:
        success = delete_obligation(obligation_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Obligation with ID {obligation_id} not found")
        return JSONResponse({"success": True, "message": f"Obligation {obligation_id} successfully deleted"})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting obligation: {str(e)}")


@router.post("/obligations/{obligation_id}/create-issue")
async def create_issue_for_obligation(
    obligation_id: str = Path(..., description="ID of the obligation to create an issue for"),
    project_tool: str = Query("jira", description="Project management tool to use (e.g., jira)")
):
    """
    Create a Jira issue for a specific obligation.
    
    Parameters:
    - obligation_id: ID of the obligation to create an issue for
    - project_tool: Optional project management tool to use (defaults to the one in settings)
    """
    try:
        # Get the obligation
        obligation = get_obligation_by_id(obligation_id)
        if not obligation:
            raise HTTPException(status_code=404, detail=f"Obligation with ID {obligation_id} not found")
            
        # Check if an issue already exists
        if obligation.jira_issue_id:
            return JSONResponse({
                "message": f"Issue already exists for this obligation with ID {obligation.jira_issue_id}",
                "issue_id": obligation.jira_issue_id
            })
            
        # Create the issue
        from app.services.obligation_issue_service import create_obligation_issue
        
        obligation_dict = {
            "obligation_text": obligation.obligation_text,
            "section": obligation.section,
            "deadline": obligation.deadline
        }
        
        response = await create_obligation_issue(obligation_dict, obligation.party_name, project_tool)
        
        # Update the obligation with the issue ID if successful
        if "key" in response and "error" not in response:
            updated_obligation = set_jira_issue_id(obligation_id, response["key"])
            return JSONResponse({
                "success": True,
                "message": f"Successfully created issue {response['key']} for obligation {obligation_id}",
                "issue_id": response["key"],
                "obligation": updated_obligation.model_dump() if updated_obligation else None
            })
        else:
            return JSONResponse({
                "success": False,
                "message": "Failed to create issue",
                "error": response.get("error", "Unknown error")
            })
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating issue for obligation: {str(e)}")


@router.post("/obligations/create-issues")
async def create_issues_for_obligations(
    obligation_ids: List[str] = Body(..., description="List of obligation IDs to create issues for"),
    project_tool: str = Query("jira", description="Project management tool to use (e.g., jira)")
):
    """
    Create Jira issues for multiple obligations.
    
    Parameters:
    - obligation_ids: List of obligation IDs to create issues for
    - project_tool: Optional project management tool to use (defaults to the one in settings)
    """
    try:
        results = []
        success_count = 0
        failed_count = 0
        
        from app.services.obligation_issue_service import create_obligation_issue
        
        for obligation_id in obligation_ids:
            # Get the obligation
            obligation = get_obligation_by_id(obligation_id)
            if not obligation:
                results.append({
                    "obligation_id": obligation_id,
                    "success": False,
                    "message": f"Obligation with ID {obligation_id} not found"
                })
                failed_count += 1
                continue
                
            # Skip if an issue already exists
            if obligation.jira_issue_id:
                results.append({
                    "obligation_id": obligation_id,
                    "success": True,
                    "message": f"Issue already exists with ID {obligation.jira_issue_id}",
                    "issue_id": obligation.jira_issue_id
                })
                success_count += 1
                continue
                
            # Create the issue
            obligation_dict = {
                "obligation_text": obligation.obligation_text,
                "section": obligation.section,
                "deadline": obligation.deadline
            }
            
            response = await create_obligation_issue(obligation_dict, obligation.party_name, project_tool)
            
            # Update the obligation with the issue ID if successful
            if "key" in response and "error" not in response:
                updated_obligation = set_jira_issue_id(obligation_id, response["key"])
                results.append({
                    "obligation_id": obligation_id,
                    "success": True,
                    "message": f"Successfully created issue {response['key']}",
                    "issue_id": response["key"]
                })
                success_count += 1
            else:
                results.append({
                    "obligation_id": obligation_id,
                    "success": False,
                    "message": "Failed to create issue",
                    "error": response.get("error", "Unknown error")
                })
                failed_count += 1
        
        return JSONResponse({
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating issues for obligations: {str(e)}")


# Issue Management APIs

@router.get("/issues")
async def list_issues(
    project_tool: Optional[str] = Query(None, description="Project management tool to use (e.g., jira)")
):
    """
    Get all issues from the project management tool.
    
    Parameters:
    - project_tool: Optional project management tool to use (defaults to the one in settings)
    """
    try:
        issues = await get_all_issues(project_tool)
        return JSONResponse({"issues": issues})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving issues: {str(e)}")


@router.get("/issues/{issue_id}")
async def get_issue(
    issue_id: str = Path(..., description="ID of the issue to retrieve"),
    project_tool: Optional[str] = Query(None, description="Project management tool to use (e.g., jira)")
):
    """
    Get details of a specific issue.
    
    Parameters:
    - issue_id: ID of the issue to retrieve
    - project_tool: Optional project management tool to use (defaults to the one in settings)
    """
    try:
        issue = await get_issue_details(issue_id, project_tool)
        
        if "error" in issue:
            raise HTTPException(status_code=404, detail=f"Issue not found: {issue['error']}")
            
        return JSONResponse(issue)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving issue: {str(e)}")


@router.patch("/issues/{issue_id}/status")
async def update_status(
    issue_id: str = Path(..., description="ID of the issue to update"),
    status_update: IssueStatusUpdate = Body(...),
    project_tool: Optional[str] = Query(None, description="Project management tool to use (e.g., jira)")
):
    """
    Update the status of an issue.
    
    Parameters:
    - issue_id: ID of the issue to update
    - status_update: New status information
    - project_tool: Optional project management tool to use (defaults to the one in settings)
    """
    try:
        result = await update_issue_status(issue_id, status_update.status, project_tool)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=f"Failed to update issue status: {result['error']}")
            
        return JSONResponse({
            "message": f"Successfully updated status of issue {issue_id}",
            "issue": result
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating issue status: {str(e)}")


@router.put("/issues/{issue_id}")
async def update_issue(
    issue_id: str = Path(..., description="ID of the issue to update"),
    issue_update: IssueDetailsUpdate = Body(...),
    project_tool: Optional[str] = Query(None, description="Project management tool to use (e.g., jira)")
):
    """
    Update details of an issue.
    
    Parameters:
    - issue_id: ID of the issue to update
    - issue_update: Updated issue details
    - project_tool: Optional project management tool to use (defaults to the one in settings)
    """
    try:
        # Convert Pydantic model to dict, excluding None values
        update_data = {k: v for k, v in issue_update.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        # Validate priority if provided
        if "priority" in update_data:
            valid_priorities = ["highest", "high", "medium", "low", "lowest"]
            if update_data["priority"].lower() not in valid_priorities:
                # Map common variations
                priority_map = {"higher": "high", "normal": "medium"}
                update_data["priority"] = priority_map.get(update_data["priority"].lower(), "medium")
        
        # Remove assignee field completely as requested
        if "assignee" in update_data:
            del update_data["assignee"]
            
        result = await update_issue_details(issue_id, update_data, project_tool)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=f"Failed to update issue: {result['error']}")
            
        response_data = {
            "message": f"Successfully updated issue {issue_id}",
            "issue": result
        }
        
        # No assignee warnings needed
            
        return JSONResponse(response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating issue: {str(e)}")


@router.delete("/issues/{issue_id}")
async def remove_issue(
    issue_id: str = Path(..., description="ID of the issue to delete"),
    project_tool: Optional[str] = Query(None, description="Project management tool to use (e.g., jira)")
):
    """
    Delete an issue.
    
    Parameters:
    - issue_id: ID of the issue to delete
    - project_tool: Optional project management tool to use (defaults to the one in settings)
    """
    try:
        result = await delete_issue(issue_id, project_tool)
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=f"Failed to delete issue: {result.get('error', 'Unknown error')}")
            
        return JSONResponse({
            "message": f"Successfully deleted issue {issue_id}",
            "success": True
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting issue: {str(e)}")

