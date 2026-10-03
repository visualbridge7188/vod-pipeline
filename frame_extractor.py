import json
import subprocess
import sys
from pathlib import Path

def extract_frame(video_path, time_str, out_path, width=1024):
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-ss", time_str,
        "-i", str(video_path),
        "-frames:v", "1",
        "-vf", f"scale={width}:-2",
        "-q:v", "3",
        str(out),
    ]
    return subprocess.run(cmd, capture_output=True).returncode == 0

def extract_hybrid_frames(video_path, outline_json_path, out_dir="frames"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    data = json.loads(Path(outline_json_path).read_text(encoding="utf-8"))
    
    for ch in data.get("chapters", []):
        n = ch["n"]
        start_time = ch["start"]
        banner = out / f"ch_{n:02d}_banner.jpg"
        ok = extract_frame(video_path, start_time, banner)
        print(f"Chapter {n:02d} ({start_time}): {'Banner OK' if ok else 'Failed'}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python frame_extractor.py <video-path> <outline-json>")
        sys.exit(1)
    extract_hybrid_frames(sys.argv[1], sys.argv[2])

