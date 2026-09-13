from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TriageRequest(BaseModel):
    """Boundary schema for UI/script input; patient IDs are synthetic allowlisted values."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    patient_id: str | None = Field(default=None, pattern=r"^SYN-PCOS-(0[1-9]|1[0-2])$")
    question: str = Field(min_length=3, max_length=800)

    @field_validator("question")
    @classmethod
    def no_controls(cls, value: str) -> str:
        if any(ord(char) < 32 and char not in "\n\t" for char in value):
            raise ValueError("A pergunta contém caracteres de controle inválidos.")
        return value


class Source(BaseModel):
    source_id: str
    title: str
    version: str
    excerpt: str = Field(max_length=900)
    score: float = 0.0


class AuditEvent(BaseModel):
    """Deliberately excludes question, patient record, name, contacts and free text."""

    run_id: str
    node: str
    status: Literal["ok", "blocked", "abstained", "error"]
    decision: str
    source_ids: list[str] = Field(default_factory=list)
    latency_ms: int = Field(ge=0)
