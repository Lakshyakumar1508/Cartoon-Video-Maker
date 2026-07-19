const videoForm = document.getElementById("videoForm");

const characterInput = document.getElementById("character");
const storyInput = document.getElementById("story");
const animationStyleInput =
    document.getElementById("animationStyle");
const languageInput = document.getElementById("language");
const audienceInput = document.getElementById("audience");
const aspectRatioInput = document.getElementById("aspectRatio");
const durationInput = document.getElementById("duration");
const includeDialogueInput =
    document.getElementById("includeDialogue");

const generateButton =
    document.getElementById("generateButton");
const buttonText = document.getElementById("buttonText");
const buttonLoader = document.getElementById("buttonLoader");

const statusBox = document.getElementById("statusBox");

const emptyResult = document.getElementById("emptyResult");
const loadingResult = document.getElementById("loadingResult");
const videoResult = document.getElementById("videoResult");

const generatedVideo =
    document.getElementById("generatedVideo");
const downloadButton =
    document.getElementById("downloadButton");
const generatedPrompt =
    document.getElementById("generatedPrompt");

const copyPromptButton =
    document.getElementById("copyPromptButton");


function showStatus(message, type = "error") {
    statusBox.textContent = message;
    statusBox.className = `status-box ${type}`;
}


function hideStatus() {
    statusBox.textContent = "";
    statusBox.className = "status-box hidden";
}


function setLoading(isLoading) {
    generateButton.disabled = isLoading;

    if (isLoading) {
        buttonText.textContent = "Generating...";
        buttonLoader.classList.remove("hidden");

        emptyResult.classList.add("hidden");
        videoResult.classList.add("hidden");
        loadingResult.classList.remove("hidden");
    } else {
        buttonText.textContent = "Generate Cartoon Video";
        buttonLoader.classList.add("hidden");
        loadingResult.classList.add("hidden");
    }
}


videoForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    hideStatus();

    const character = characterInput.value.trim();
    const story = storyInput.value.trim();

    if (!character && !story) {
        showStatus(
            "Please enter a character description or a story."
        );

        return;
    }

    const requestData = {
        character: character || null,
        story: story || null,
        animation_style: animationStyleInput.value,
        language: languageInput.value,
        target_audience: audienceInput.value,
        aspect_ratio: aspectRatioInput.value,
        duration_seconds: Number(durationInput.value),
        include_dialogue: includeDialogueInput.checked,
    };

    setLoading(true);

    try {
        const response = await fetch("/api/generate-video", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(requestData),
        });

        let responseData;

        try {
            responseData = await response.json();
        } catch {
            throw new Error(
                "The server returned an invalid response."
            );
        }

        if (!response.ok) {
            let errorMessage = "Video generation failed.";

            if (typeof responseData.detail === "string") {
                errorMessage = responseData.detail;
            } else if (Array.isArray(responseData.detail)) {
                errorMessage = responseData.detail
                    .map((error) => error.msg)
                    .join(", ");
            }

            throw new Error(errorMessage);
        }

        generatedVideo.src =
            `${responseData.video_url}?time=${Date.now()}`;

        generatedVideo.load();

        downloadButton.href = responseData.download_url;
        generatedPrompt.textContent =
            responseData.generated_prompt;

        videoResult.classList.remove("hidden");

        showStatus(
            "Your cartoon video was generated successfully.",
            "success"
        );

        generatedVideo.scrollIntoView({
            behavior: "smooth",
            block: "center",
        });
    } catch (error) {
        emptyResult.classList.remove("hidden");

        showStatus(
            error.message ||
            "Something went wrong while generating the video."
        );
    } finally {
        setLoading(false);
    }
});


copyPromptButton.addEventListener("click", async () => {
    const promptText = generatedPrompt.textContent.trim();

    if (!promptText) {
        return;
    }

    try {
        await navigator.clipboard.writeText(promptText);

        copyPromptButton.textContent = "Copied";

        setTimeout(() => {
            copyPromptButton.textContent = "Copy";
        }, 1500);
    } catch {
        showStatus(
            "Prompt could not be copied automatically."
        );
    }
});