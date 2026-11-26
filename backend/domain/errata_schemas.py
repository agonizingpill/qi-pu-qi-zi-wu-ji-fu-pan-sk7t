from typing import Annotated

from pydantic import BaseModel, ConfigDict, FiniteFloat, StringConstraints

class IssueErratum(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    flag: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    corrigendum: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
