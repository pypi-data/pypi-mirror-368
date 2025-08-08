import tempfile
import subprocess
import io

def overlay_audio_ffmpeg(video_bytes: bytes, audio_bytes: bytes) -> io.BytesIO | None:
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as video_file, \
             tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as audio_file, \
             tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as output_file:

            video_file.write(video_bytes)
            audio_file.write(audio_bytes)
            video_file.flush()
            audio_file.flush()

            command = [
                "ffmpeg", "-y",
                "-i", video_file.name,
                "-i", audio_file.name,
                "-c:v", "copy",
                "-c:a", "aac",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                output_file.name
            ]

            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            with open(output_file.name, "rb") as f:
                return io.BytesIO(f.read())

    except Exception as e:
        print("FFmpeg audio overlay failed:", e)
        return None
