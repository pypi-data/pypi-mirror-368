"""
Pydantic models for GitHub objects.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class Label(BaseModel):
    """Represents a GitHub label."""

    id: str
    name: str
    color: str
    description: Optional[str] = None


class Issue(BaseModel):
    """Represents a GitHub issue."""

    id: str
    number: int
    title: str
    body: str
    state: Optional[str] = None
    project_items: list = Field(default_factory=list)
    assignees: list = Field(default_factory=list)
    labels: List[Label] = Field(default_factory=list)
    parent: Optional["Issue"] = None
    sub_issues: List["Issue"] = Field(default_factory=list)

    # Custom fields
    sprint: Optional[str] = None
    estimate: Optional[int] = None
    status: Optional[str] = None
    is_archived: bool = Field(default=False, alias="isArchived")


class ProjectV2Item(BaseModel):
    """Represents a ProjectV2 item."""

    id: str
    content: Optional[Issue] = None
    status: Optional[str] = None
    estimate: Optional[int] = None
    is_archived: bool = Field(default=False, alias="isArchived")


class Project(BaseModel):
    """Represents a GitHub project."""

    id: str
    title: str
    number: int
    url: str