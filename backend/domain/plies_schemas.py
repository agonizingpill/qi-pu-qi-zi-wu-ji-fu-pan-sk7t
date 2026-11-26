from typing import Annotated

from pydantic import BaseModel, ConfigDict, FiniteFloat, StringConstraints

class AttachPly(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    game: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    number: int
    gap: FiniteFloat
    capture_claim: int
    repeat_move: bool


class VerifyReplay(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ply: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    actual: int
