from typing import Optional

from pydantic import BaseModel, Field


class RetrievedResults(BaseModel):
    """
    The model for returned records and / errors.
    """
    results: list[dict] = Field(
        default_factory=list,
        description="A list of dictionaries returned by a query",
    )
    error: Optional[str] = Field(
        default=None,
        description="The optional error message returned by a query",
    )
