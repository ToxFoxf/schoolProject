from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional
from datetime import datetime
from uuid import uuid4
from auth import verify_token
from database import projects_db, users_db
from models import ProjectCreate, ProjectUpdate

router = APIRouter(prefix="/api/projects", tags=["projects"])


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
async def get_projects(authorization: Optional[str] = Header(None)):
    """Get all projects for the current user"""
    user_id = get_user_from_token(authorization)
    
    user_projects = []
    for project in projects_db.values():
        if user_id in project["members"]:
            user_projects.append({
                "id": project["id"],
                "name": project["name"],
                "description": project["description"],
                "createdBy": project["createdBy"],
                "members": project["members"],
                "status": project["status"],
                "createdAt": project["createdAt"]
            })
    
    return user_projects


@router.post("", response_model=dict)
async def create_project(project: ProjectCreate, authorization: Optional[str] = Header(None)):
    """Create a new project"""
    user_id = get_user_from_token(authorization)
    
    project_id = f"proj-{uuid4().hex[:8]}"
    new_project = {
        "id": project_id,
        "name": project.name,
        "description": project.description or "",
        "createdBy": user_id,
        "members": [user_id] + (project.members or []),
        "status": "active",
        "createdAt": datetime.now().isoformat()
    }
    
    projects_db[project_id] = new_project
    
    return new_project


@router.get("/{project_id}", response_model=dict)
async def get_project(project_id: str, authorization: Optional[str] = Header(None)):
    """Get project details"""
    user_id = get_user_from_token(authorization)
    
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is member
    if user_id not in project["members"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this project"
        )
    
    return project


@router.put("/{project_id}", response_model=dict)
async def update_project(project_id: str, updates: ProjectUpdate, authorization: Optional[str] = Header(None)):
    """Update project"""
    user_id = get_user_from_token(authorization)
    
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Only creator can update
    if project["createdBy"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project creator can update"
        )
    
    if updates.name:
        project["name"] = updates.name
    if updates.description is not None:
        project["description"] = updates.description
    if updates.status:
        project["status"] = updates.status
    if updates.members:
        project["members"] = list(set(project["members"] + updates.members))
    
    return project


@router.delete("/{project_id}", response_model=dict)
async def delete_project(project_id: str, authorization: Optional[str] = Header(None)):
    """Delete project"""
    user_id = get_user_from_token(authorization)
    
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Only creator can delete
    if project["createdBy"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project creator can delete"
        )
    
    del projects_db[project_id]
    
    return {"message": f"Project {project_id} deleted"}


@router.post("/{project_id}/members", response_model=dict)
async def add_member(project_id: str, member_id: str, authorization: Optional[str] = Header(None)):
    """Add member to project"""
    user_id = get_user_from_token(authorization)
    
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Only creator can add members
    if project["createdBy"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project creator can add members"
        )
    
    if member_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if member_id not in project["members"]:
        project["members"].append(member_id)
    
    return project


@router.delete("/{project_id}/members/{member_id}", response_model=dict)
async def remove_member(project_id: str, member_id: str, authorization: Optional[str] = Header(None)):
    """Remove member from project"""
    user_id = get_user_from_token(authorization)
    
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Only creator can remove members
    if project["createdBy"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project creator can remove members"
        )
    
    if member_id in project["members"]:
        project["members"].remove(member_id)
    
    return project
