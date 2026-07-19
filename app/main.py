from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.models import CartoonVideoRequest, CartoonVideoResponse
from app.prompt_generator import generate_video_prompt
from app.video_generator import generate_video


BASE_DIRECTORY = Path(__file__).resolve().parent.parent

STATIC_DIRECTORY = BASE_DIRECTORY / "static"
VIDEO_DIRECTORY = BASE_DIRECTORY / "generated_videos"


app = FastAPI(
    title="AI Cartoon Video Generator",
    description=(
        "Generate cartoon prompts using LangChain and videos "
        "using a Hugging Face text-to-video model."
    ),
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIRECTORY),
    name="static",
)

app.mount(
    "/generated-videos",
    StaticFiles(directory=VIDEO_DIRECTORY),
    name="generated-videos",
)


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIRECTORY / "index.html")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Cartoon Video Generator",
    }


@app.post(
    "/api/generate-video",
    response_model=CartoonVideoResponse,
)
def create_cartoon_video(
    request: CartoonVideoRequest,
):
    try:
        generated_prompt = generate_video_prompt(request)

        filename = generate_video(generated_prompt)

        video_url = f"/generated-videos/{filename}"
        download_url = f"/api/download/{filename}"

        return CartoonVideoResponse(
            success=True,
            generated_prompt=generated_prompt,
            video_url=video_url,
            download_url=download_url,
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {error}",
        ) from error


@app.get("/api/download/{filename}")
def download_video(filename: str):
    safe_filename = Path(filename).name
    video_path = VIDEO_DIRECTORY / safe_filename

    if video_path.suffix.lower() != ".mp4":
        raise HTTPException(
            status_code=400,
            detail="Invalid video file.",
        )

    if not video_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Video not found.",
        )

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=safe_filename,
    )