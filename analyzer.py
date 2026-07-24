from pydub import AudioSegment
import os
import shutil


def _gaseste_ffmpeg():
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")

    if ffmpeg_path and ffprobe_path:
        return ffmpeg_path, ffprobe_path

    cale_winget = os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages"
    )
    if os.path.isdir(cale_winget):
        for radacina, _, fisiere in os.walk(cale_winget):
            if "ffmpeg.exe" in fisiere and "ffprobe.exe" in fisiere:
                return (
                    os.path.join(radacina, "ffmpeg.exe"),
                    os.path.join(radacina, "ffprobe.exe"),
                )

    raise FileNotFoundError(
        "Nu am găsit ffmpeg/ffprobe. Instalează-le cu 'winget install ffmpeg' "
        "sau descarcă-le de pe https://ffmpeg.org și adaugă-le în PATH."
    )


_ffmpeg, _ffprobe = _gaseste_ffmpeg()
AudioSegment.converter = _ffmpeg
AudioSegment.ffprobe = _ffprobe


def get_audio_duration(file_path):
    audio = AudioSegment.from_file(file_path)
    return len(audio) / 1000


def split_audio(file_path, output_folder="temp", chunk_seconds=90):

    os.makedirs(output_folder, exist_ok=True)

    for f in os.listdir(output_folder):
        if f.endswith(".mp3"):
            os.remove(os.path.join(output_folder, f))

    audio = AudioSegment.from_file(file_path)
    duration = len(audio)
    files = []

    for start in range(0, duration, chunk_seconds * 1000):
        end = min(start + chunk_seconds * 1000, duration)
        chunk = audio[start:end]

        filename = os.path.join(output_folder, f"chunk_{start // 1000}.mp3")
        chunk.export(filename, format="mp3")
        files.append(filename)

    return files
