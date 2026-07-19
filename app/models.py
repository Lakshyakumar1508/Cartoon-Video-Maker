from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class CartoonVideoRequest(BaseModel):
    character: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Description of the cartoon character",
    )

    story: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Cartoon story or scene",
    )

    animation_style: Literal[
        "3D Cartoon",
        "2D Cartoon",
        "Anime",
        "Clay Animation",
        "Watercolor Animation",
        "Comic Animation",
    ] = "3D Cartoon"

    language: Literal[
        "English",
        "Hindi",
        "Hinglish",
    ] = "Hindi"

    target_audience: Literal[
        "Kids",
        "Family",
        "Teenagers",
        "General Audience",
    ] = "Kids"

    aspect_ratio: Literal[
        "16:9",
        "9:16",
        "1:1",
    ] = "16:9"

    duration_seconds: int = Field(
        default=15,
        ge=10,
        le=30,
    )

    include_dialogue: bool = True

    @model_validator(mode="after")
    def validate_character_or_story(self):
        character = self.character.strip() if self.character else ""
        story = self.story.strip() if self.story else ""

        if not character and not story:
            raise ValueError(
                "Please enter at least a character or a story."
            )

        return self


class CartoonVideoResponse(BaseModel):
    success: bool
    generated_prompt: str
    video_url: str
    download_url: str
