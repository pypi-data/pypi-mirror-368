from typing import Annotated

from pydantic import BaseModel, StringConstraints

LowerCaseText = Annotated[str | None, StringConstraints(to_lower=True)]


class Text(BaseModel):
    original_text: LowerCaseText = ""
    normalized_text: LowerCaseText = ""
    human_normalized_text: LowerCaseText = ""
    asr_normalized_message: LowerCaseText = ""
    human_normalized_text_with_anaphora: LowerCaseText = ""
