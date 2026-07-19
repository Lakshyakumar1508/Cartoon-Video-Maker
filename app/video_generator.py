import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

VIDEO_MODEL = os.getenv(
    "VIDEO_MODEL",
    "Wan-AI/Wan2.2-TI2V-5B",
)

VIDEO_PROVIDER = os.getenv(
    "VIDEO_PROVIDER",
    "fal-ai",
)

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN was not found in the .env file.")


BASE_DIRECTORY = Path(__file__).resolve().parent.parent

VIDEO_DIRECTORY = BASE_DIRECTORY / "generated_videos"
VIDEO_DIRECTORY.mkdir(parents=True, exist_ok=True)


video_client = InferenceClient(
    provider=VIDEO_PROVIDER,
    api_key=HF_TOKEN,
    timeout=600,
)


def generate_video(prompt: str) -> str:
    """
    Generate a video using a Hugging Face text-to-video provider.

    Returns:
        Name of the generated MP4 file.
    """

    try:
        video_result = video_client.text_to_video(
            prompt,
            model=VIDEO_MODEL,
        )

        filename = f"cartoon_{uuid.uuid4().hex}.mp4"
        output_path = VIDEO_DIRECTORY / filename

        if isinstance(video_result, bytes):
            video_bytes = video_result

        elif isinstance(video_result, bytearray):
            video_bytes = bytes(video_result)

        elif hasattr(video_result, "read"):
            video_bytes = video_result.read()

        else:
            raise RuntimeError(
                "The video provider returned an unsupported response."
            )

        if not video_bytes:
            raise RuntimeError(
                "The video provider returned an empty video."
            )

        output_path.write_bytes(video_bytes)

        return filename

    except Exception as error:
        raise RuntimeError(
            f"Video generation failed: {error}"
        ) from error
