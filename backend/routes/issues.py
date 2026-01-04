from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional, List
from datetime import datetime
from uuid import uuid4
from auth import verify_token
from database import issues_db, projects_db
from models import IssueCreate, IssueUpdate, IssueStatusUpdate

router = APIRouter(prefix="/api/issues", tags=["issues"])


def get_user_from_token(authorization: Optional[str] = Header(None)):
    """Extract and verify user from authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided"
        )
    
    try:
        token = authorization.split(" ")[1]
        payload = verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token"
            )
        return payload.get("userId")
    except (IndexError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )


@router.get("", response_model=list)
async def get_issues(project_id: Optional[str] = None, authorization: Optional[str] = Header(None)):
    """Get issues, optionally filtered by project"""
    user_id = get_user_from_token(authorization)
    
    result = []
    for issue in issues_db.values():
        if project_id:
            if issue["projectId"] != project_id:
                continue
            # Check if user is member of project
            project = projects_db.get(project_id)
            if project and user_id not in project["members"]:
                continue
        
        result.append({
            "id": issue["id"],
            "title": issue["title"],
            "description": issue["description"],
            "projectId": issue["projectId"],
            "createdBy": issue["createdBy"],
            "assignedTo": issue["assignedTo"],
            "status": issue["status"],
            "priority": issue["priority"],
            "createdAt": issue["createdAt"]
        })
    
    return result


@router.post("", response_model=dict)
async def create_issue(issue: IssueCreate, authorization: Optional[str] = Header(None)):
    """Create a new issue"""
    user_id = get_user_from_token(authorization)
    
    # Check if project exists
    project = projects_db.get(issue.projectId)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is member of project
    if user_id not in project["members"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create issues in this project"
        )
    
    issue_id = f"issue-{uuid4().hex[:8]}"
    new_issue = {
        "id": issue_id,
        "title": issue.title,
        "description": issue.description or "",
        "projectId": issue.projectId,
        "createdBy": user_id,
        "assignedTo": issue.assignedTo,
        "status": "open",
        "priority": issue.priority or "medium",
        "createdAt": datetime.now().isoformat()
    }
    
    issues_db[issue_id] = new_issue
    
    return new_issue


@router.get("/{issue_id}", response_model=dict)
async def get_issue(issue_id: str, authorization: Optional[str] = Header(None)):
    """Get issue details"""
    user_id = get_user_from_token(authorization)
    
    issue = issues_db.get(issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check if user has access to project
    project = projects_db.get(issue["projectId"])
    if project and user_id not in project["members"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this issue"
        )
    
    return issue


@router.put("/{issue_id}", response_model=dict)
async def update_issue(issue_id: str, updates: IssueUpdate, authorization: Optional[str] = Header(None)):
    """Update issue"""
    user_id = get_user_from_token(authorization)
    
    issue = issues_db.get(issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check if user is issue creator
    if issue["createdBy"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only issue creator can update"
        )
    
    if updates.title:
        issue["title"] = updates.title
    if updates.description is not None:
        issue["description"] = updates.description
    if updates.priority:
        issue["priority"] = updates.priority
    if updates.assignedTo is not None:
        issue["assignedTo"] = updates.assignedTo
    
    return issue


@router.patch("/{issue_id}/status", response_model=dict)
async def update_issue_status(issue_id: str, update: IssueStatusUpdate, authorization: Optional[str] = Header(None)):
    """Update issue status"""
    user_id = get_user_from_token(authorization)
    
    issue = issues_db.get(issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check if user is in project
    project = projects_db.get(issue["projectId"])
    if project and user_id not in project["members"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this issue"
        )
    
    issue["status"] = update.status
    
    return issue


@router.delete("/{issue_id}", response_model=dict)
async def delete_issue(issue_id: str, authorization: Optional[str] = Header(None)):
    """Delete issue"""
    user_id = get_user_from_token(authorization)
    
    issue = issues_db.get(issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Only creator can delete
    if issue["createdBy"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only issue creator can delete"
        )
    
    del issues_db[issue_id]
    
    return {"message": f"Issue {issue_id} deleted"}


@router.get("/project/{project_id}/stats", response_model=dict)
async def get_project_stats(project_id: str, authorization: Optional[str] = Header(None)):
    """Get issue statistics for a project"""
    user_id = get_user_from_token(authorization)
    
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if user_id not in project["members"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    open_count = 0
    closed_count = 0
    in_progress_count = 0
    
    for issue in issues_db.values():
        if issue["projectId"] == project_id:
            if issue["status"] == "open":
                open_count += 1
            elif issue["status"] == "closed":
                closed_count += 1
            elif issue["status"] == "in-progress":
                in_progress_count += 1
    
    return {
        "projectId": project_id,
        "open": open_count,
        "closed": closed_count,
        "inProgress": in_progress_count,
        "total": open_count + closed_count + in_progress_count
    }
