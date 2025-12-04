"""Pydantic models for agentrx."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class TemplateData(BaseModel):
    """Data used to fill the markdown template."""

    title: str = Field(..., description="Document title")
    description: Optional[str] = Field(None, description="Short description")
    tags: List[str] = Field(default_factory=list, description="List of tags")

    class Config:
        extra = "forbid"
