from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.dependencies import CurrentUser
from app.core.prompt_manager import prompt_manager

router = APIRouter()

class PromptUpdate(BaseModel):
    text: str

@router.get("/prompts")
async def list_prompts(current_user: CurrentUser):
    """List all registered system prompts."""
    # Ensure user has permission
    if current_user.role not in ["doctor", "nurse", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage prompts."
        )
    return await prompt_manager.list_all_prompts()

@router.get("/prompts/{name}")
async def get_prompt(name: str, current_user: CurrentUser):
    """Get a specific system prompt."""
    if current_user.role not in ["doctor", "nurse", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage prompts."
        )
    all_prompts = await prompt_manager.list_all_prompts()
    if name not in all_prompts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt '{name}' not found."
        )
    return all_prompts[name]

@router.put("/prompts/{name}")
async def update_prompt(name: str, payload: PromptUpdate, current_user: CurrentUser):
    """Update/Override a system prompt."""
    if current_user.role not in ["doctor", "nurse", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage prompts."
        )
    all_prompts = await prompt_manager.list_all_prompts()
    if name not in all_prompts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt '{name}' not found."
        )
    await prompt_manager.set_prompt(name, payload.text)
    return {"message": f"Prompt '{name}' successfully updated.", "name": name}

@router.delete("/prompts/{name}")
async def reset_prompt(name: str, current_user: CurrentUser):
    """Reset a system prompt to its default markdown file content."""
    if current_user.role not in ["doctor", "nurse", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage prompts."
        )
    all_prompts = await prompt_manager.list_all_prompts()
    if name not in all_prompts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt '{name}' not found."
        )
    await prompt_manager.reset_prompt(name)
    return {"message": f"Prompt '{name}' successfully reset to default.", "name": name}
