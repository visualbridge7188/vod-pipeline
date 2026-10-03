import subprocess
import sys
from pathlib import Path

def download_video(url, out_dir="downloads", use_cookie=True):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    target_tmpl = str(out / "video.%(ext)s")
    
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
        "--merge-output-format", "mp4",
        "--write-sub", "--write-auto-sub",
        "--sub-lang", "ko,en",
        "--sub-format", "vtt",
        "-o", target_tmpl,
        "--no-playlist",
    ]
    if use_cookie:
        cmd.extend(["--cookies-from-browser", "chrome"])
    cmd.append(url)
    
    print(f"[downloader] Running: {' '.join(cmd)}")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        raise RuntimeError(f"Download failed with exit code {res.returncode}")
    
    video_path = out / "video.mp4"
    print(f"[downloader] Download completed: {video_path}")
    return str(video_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python downloader.py <video-url>")
        sys.exit(1)
    download_video(sys.argv[1])

