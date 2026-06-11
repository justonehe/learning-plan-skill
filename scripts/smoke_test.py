#!/usr/bin/env python3
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cli = root / "scripts" / "learning_skill.py"


def run(*a):
    subprocess.check_call([sys.executable, str(cli), *a])


with tempfile.TemporaryDirectory() as d:
    repo = Path(d) / "demo-learning"
    run("init", str(repo), "--topic", "demo", "--goal", "test", "--mode", "auto", "--no-git")
    run("session", str(repo), "--title", "first")
    run("lab", str(repo), "--name", "demo lab")
    t = Path(d) / "t.md"
    t.write_text("# Transcript\n\nhello\n", encoding="utf-8")
    run("video", str(repo), "--title", "demo video", "--source", "https://example.com/v", "--transcript", str(t))
    run("course", str(repo), "--title", "demo course", "--source", "https://example.com/c")
    run("synthesis", str(repo))
    run("resource", str(repo), "--name", "Demo Book", "--type", "textbook",
        "--source", "https://example.com/book", "--stage", "Stage 1", "--use", "主线", "--level", "intro")
    run("entry", str(repo))
    required = [
        "README.md", "mission.md", "profile.md", "plan.md", "state.md", "resources.md",
        "raw", "dialogue",
        "labs/lab01-demo-lab/README.md", "labs/lab01-demo-lab/judge/run.py",
        "videos/demo-video/README.md", "videos/demo-video/transcript.md", "videos/demo-video/keyframes",
        "coursepacks/demo-course/README.md", "coursepacks/demo-course/extracted-parts.md",
        "synthesis/source-map.md", "synthesis/selected-path.md",
        "index.html",
    ]
    missing = [x for x in required if not (repo / x).exists()]
    if missing:
        raise SystemExit("missing: " + ", ".join(missing))
    html = (repo / "index.html").read_text(encoding="utf-8")
    if "Demo Book" not in html:
        raise SystemExit("entry page missing resource link")
    tr = (repo / "videos/demo-video/transcript.md").read_text(encoding="utf-8")
    if "hello" not in tr:
        raise SystemExit("transcript not copied")
print("smoke test passed")
