from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, StringConstraints


class AttachSheet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    game: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    from_number: int
    to_number: int
    total_captures: int


class Recompute(BaseModel):
    model_config = ConfigDict(extra="forbid")
    game: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]


class MakeupSheet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    game: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    from_number: int
    to_number: int
    total_captures: int


class SignGroup(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plan: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    makeup: Optional[MakeupSheet] = None
