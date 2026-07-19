import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.models import CartoonVideoRequest

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

PROMPT_MODEL = os.getenv(
    "PROMPT_MODEL",
    "llama-3.3-70b-versatile",
)

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY was not found. Add it to the .env file."
    )

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert cartoon director and AI text-to-video prompt engineer.

Convert the user's character description or story into one detailed,
production-quality English prompt for a text-to-video AI model.

Requirements:

- Maintain a consistent character throughout the video.
- Fully describe the character's appearance, clothing, colors,
  expressions, and personality.
- Describe the environment in vivid detail.
- Focus on one coherent animated scene.
- Include character actions, emotions, and movement.
- Include cinematic camera shots and movements.
- Describe lighting, atmosphere, colors, and animation quality.
- Respect the requested animation style and aspect ratio.
- Make the content suitable for the selected audience.
- Include dialogue only when requested.
- Avoid copyrighted characters.
- Avoid subtitles, logos, watermarks, text overlays, UI elements,
  artifacts, distortions, blurry quality, extra limbs, or deformed faces.

Finish with a concise negative prompt.

Return ONLY the final prompt.
No explanations.
No headings.
No Markdown.
""",
        ),
        (
            "human",
            """
Character:
{character}

Story:
{story}

Animation Style:
{animation_style}

Language:
{language}

Target Audience:
{target_audience}

Aspect Ratio:
{aspect_ratio}

Duration:
{duration_seconds} seconds

Include Dialogue:
{include_dialogue}

Generate a production-ready cinematic cartoon video prompt.
""",
        ),
    ]
)

chat_model = ChatGroq(
    api_key=GROQ_API_KEY,
    model=PROMPT_MODEL,
    temperature=0.7,
    max_tokens=600,
)

prompt_chain = (
    prompt_template
    | chat_model
    | StrOutputParser()
)


def generate_video_prompt(
    request: CartoonVideoRequest,
) -> str:

    character = (
        request.character.strip()
        if request.character
        else (
            "Create an original, colorful, expressive cartoon character suitable for kids."
        )
    )

    story = (
        request.story.strip()
        if request.story
        else (
            "Create a short, funny, heartwarming animated story with a happy ending."
        )
    )

    try:
        result = prompt_chain.invoke(
            {
                "character": character,
                "story": story,
                "animation_style": request.animation_style,
                "language": request.language,
                "target_audience": request.target_audience,
                "aspect_ratio": request.aspect_ratio,
                "duration_seconds": request.duration_seconds,
                "include_dialogue": (
                    "Yes"
                    if request.include_dialogue
                    else "No"
                ),
            }
        )

        result = result.strip()

        if not result:
            raise RuntimeError(
                "Groq returned an empty prompt."
            )

        return result

    except Exception as error:
        raise RuntimeError(
            f"Groq prompt generation failed: {error}"
        ) from error