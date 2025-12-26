import subprocess
from pathlib import Path


def compress_video(input_path: Path, output_path: Path):
    """
    Compress video, downscale to max 720p, then delete input.
    """

    command = [
        "ffmpeg",
        "-y",
        "-i", str(input_path),

        # Video
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "32",
        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease",

        # Audio
        "-c:a", "aac",
        "-b:a", "64k",

        str(output_path),
    ]

    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    finally:
        # Always clean up uploaded file
        if input_path.exists():
            input_path.unlink()
