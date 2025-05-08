from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """Configuration for LLM settings."""

    provider: str = Field(
        ..., description="LLM provider (anthropic, openai, ollama, lmstudio)"
    )
    model: str = Field(..., description="Model name to use")
    temperature: float = Field(
        0.7, description="Temperature for generation (0.0 to 1.0)"
    )
    max_tokens: int = Field(4000, description="Maximum tokens to generate")


class Course(BaseModel):
    """Course data model representing a complete educational course."""

    title: str = Field(..., description="Course title")
    description: str = Field(..., description="Course description")
    target_audience: str = Field(..., description="Target audience for the course")
    language: str = Field("English", description="Language of the course")
    version: str = Field("1.0", description="Course version")
    author: str = Field(..., description="Course author")

    # Optional fields
    skill_level: Optional[str] = Field(
        None, description="Skill level (Beginner, Intermediate, Advanced)"
    )
    prerequisites: Optional[str] = Field(None, description="Course prerequisites")
    estimated_duration: Optional[str] = Field(
        None, description="Estimated duration to complete the course"
    )

    # LLM Configuration
    llm_config: LLMConfig = Field(
        ..., description="Primary LLM configuration for course generation"
    )

    # Additional LLM Configurations
    additional_llm_configs: List[LLMConfig] = Field(
        default_factory=list,
        description="Additional LLM configurations for course generation",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the course to a dictionary suitable for YAML serialization."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Course":
        """Create a Course instance from a dictionary (loaded from YAML)."""
        return cls(**data)
