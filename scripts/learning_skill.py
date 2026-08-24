#!/usr/bin/env python3
"""learning-plan-skill CLI:Markdown + Git 学习仓库脚手架。零第三方依赖。"""
import argparse
import html as html_mod
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "templates"
MODES = {"auto", "strong", "qa"}
DIRS = [
    "raw", "dialogue", "notes", "tests", "labs", "experiments",
    "videos", "readings", "coursepacks", "synthesis", ".learning_skill",
]

JUDGE_STUB = '''#!/usr/bin/env python3
"""评测机入口:规划期写好并 commit(先写后做)。

要求:
- 一条命令跑完,输出 PASS / FAIL,退出码 0 / 1
- 覆盖边界用例
- 存在可对照的标准解时,加随机数据 + 暴力参考解对拍(stress testing)
"""
import sys


def main():
    print("FAIL: judge 尚未实现。请在用户开始做题之前写好评测逻辑并 commit。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
'''


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def stamp():
    return datetime.now().strftime("%Y-%m-%d-%H%M%S")


def slugify(text):
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text)
    return text.strip("-") or "untitled"


def render(name, data):
    s = (TEMPLATE_DIR / name).read_text(encoding="utf-8")
    for k, v in data.items():
        s = s.replace("{{" + k + "}}", str(v))
    return s


def write_if_missing(path, content):
    if not path.exists():
        path.write_text(content, encoding="utf-8")
        return True
    return False


def append_text(path, text):
    with path.open("a", encoding="utf-8") as f:
        f.write(text)


def run_git(cwd, args):
    if not shutil.which("git"):
        return False, "git not found"
    p = subprocess.run(["git"] + args, cwd=str(cwd), text=True, capture_output=True)
    return p.returncode == 0, (p.stdout + p.stderr).strip()


def read_meta(path):
    meta = path / ".learning_skill" / "metadata.json"
    if meta.exists():
        return json.loads(meta.read_text(encoding="utf-8"))
    return {"topic": path.name, "mode": "auto", "goal": ""}


def ensure_repo_dirs(path):
    for d in DIRS:
        (path / d).mkdir(parents=True, exist_ok=True)


def init_cmd(args):
    path = Path(args.path).expanduser().resolve()
    if args.mode not in MODES:
        raise SystemExit(f"invalid mode: {args.mode} (choices: {sorted(MODES)})")
    path.mkdir(parents=True, exist_ok=True)
    ensure_repo_dirs(path)
    data = {"topic": args.topic, "goal": args.goal, "mode": args.mode, "created": now()}
    created = []
    files = {
        "README.md": render("project_README.md", data),
        "mission.md": render("mission.md", data),
        "profile.md": render("profile.md", data),
        "plan.md": render("plan.md", data),
        "state.md": render("state.md", data),
        "resources.md": render("resources.md", data),
        ".gitignore": "__pycache__/\n*.pyc\n.DS_Store\n.tmp/\n",
    }
    for rel, content in files.items():
        if write_if_missing(path / rel, content):
            created.append(rel)
    meta = path / ".learning_skill" / "metadata.json"
    metadata = dict(data)
    metadata["version"] = "0.6.0"
    meta.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    inside, _ = run_git(path, ["rev-parse", "--is-inside-work-tree"])
    if inside:
        print("notice: 该路径位于一个已有 git 仓库内部,学习记录会提交到外层仓库;"
              "如需独立仓库,请改用仓库之外的路径。")
    elif not args.no_git:
        run_git(path, ["init"])
        run_git(path, ["add", "."])
        run_git(path, ["commit", "-m", "init: create learning repo"])
    print(f"created learning repo: {path}")
    if created:
        print("created files: " + ", ".join(created))
    print("next: 与用户完成需求确认,把结果写入 mission.md 并请用户确认。")


def session_cmd(args):
    path = Path(args.path).expanduser().resolve()
    ensure_repo_dirs(path)
    meta = read_meta(path)
    title = args.title or "session"
    s = stamp() + "-" + slugify(title)
    data = {"title": title, "topic": meta.get("topic", path.name),
            "mode": meta.get("mode", "auto"), "created": now()}
    raw = path / "raw" / f"{s}.md"
    dialogue = path / "dialogue" / f"{s}.md"
    write_if_missing(raw, render("raw_session.md", data))
    write_if_missing(dialogue, render("session.md", data))
    print(f"created raw: {raw}")
    print(f"created dialogue: {dialogue}")


def lab_cmd(args):
    path = Path(args.path).expanduser().resolve()
    ensure_repo_dirs(path)
    labs = path / "labs"
    nums = []
    for d in labs.iterdir():
        m = re.match(r"lab(\d+)", d.name)
        if d.is_dir() and m:
            nums.append(int(m.group(1)))
    n = (max(nums) + 1) if nums else 1
    name = f"lab{n:02d}-{slugify(args.name)}"
    p = labs / name
    for sub in ["starter", "solution", "judge"]:
        (p / sub).mkdir(parents=True, exist_ok=True)
    write_if_missing(p / "README.md", render("lab_README.md", {"name": args.name, "created": now()}))
    write_if_missing(p / "judge" / "run.py", JUDGE_STUB)
    print(f"created lab: {p}")
    print("reminder: 评测机先写后做——在用户开始做题之前完成 judge/ 并 commit。")


def video_cmd(args):
    path = Path(args.path).expanduser().resolve()
    ensure_repo_dirs(path)
    title = args.title
    vdir = path / "videos" / slugify(title)
    kdir = vdir / "keyframes"
    kdir.mkdir(parents=True, exist_ok=True)
    data = {
        "title": title,
        "created": now(),
        "overview": args.overview or "待补充（完成建档前必须依据真实字幕/转写填写）",
        "stage": args.stage,
        "role": args.role,
    }
    write_if_missing(vdir / "README.md", render("video_README.md", data))
    (vdir / "source.txt").write_text(str(args.source) + "\n", encoding="utf-8")

    if args.transcript:
        src = Path(args.transcript).expanduser()
        if src.exists() and src.is_file():
            (vdir / "transcript.md").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            (vdir / "transcript.md").write_text(
                f"# Transcript\n\n未找到转写文件:{args.transcript}\n"
                "请确认路径,或将转写内容手动粘贴到本文件。\n", encoding="utf-8")
            print(f"warning: 转写文件不存在: {args.transcript}")
    else:
        write_if_missing(vdir / "transcript.md", "# Transcript\n\n待补充。\n")

    write_if_missing(vdir / "visual-notes.md", render("visual_notes.md", data))
    write_if_missing(vdir / "multimodal-summary.md", render("multimodal_summary.md", data))
    write_if_missing(vdir / "questions.md", render("video_questions.md", data))

    source_path = Path(args.source).expanduser()
    extracted = False
    if source_path.exists():
        if shutil.which("ffmpeg"):
            out = str(kdir / "frame-%05d.jpg")
            if args.mode == "scene":
                vf = ["-vf", "select='gt(scene,0.25)'", "-vsync", "vfr"]
            else:
                vf = ["-vf", f"fps=1/{max(1, args.every_seconds)}"]
            cmd = (["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(source_path)] + vf + ["-q:v", "2", out])
            proc = subprocess.run(cmd, text=True, capture_output=True)
            if proc.returncode == 0:
                extracted = True
            else:
                append_text(vdir / "questions.md",
                            "\n## Frame extraction error\n\n```text\n" + proc.stderr.strip() + "\n```\n")
        else:
            append_text(vdir / "questions.md",
                        "\n## Frame extraction skipped\n\nffmpeg not found。可手动放入截图或关键帧。\n")
    else:
        append_text(vdir / "questions.md",
                    "\n## Source note\n\nsource 不是本地文件。请先依法获取可分析的视频文件,或手动放入关键帧。\n")

    res = path / "resources.md"
    if res.exists():
        use = args.overview or "待补充(入选理由必填)"
        append_text(res, f"| {title} | video | {args.source} | {args.stage} | {use} | 待补充 | videos/{slugify(title)}/ |\n")
    print(f"created video record: {vdir}")
    if not args.overview:
        print("warning: 视频介绍仍为空;依据真实字幕/转写补完 README 的 Overview 后才算建档完成。")
    print(f"keyframes {'extracted' if extracted else 'directory ready'}: {kdir}")


def course_cmd(args):
    path = Path(args.path).expanduser().resolve()
    ensure_repo_dirs(path)
    title = args.title
    cdir = path / "coursepacks" / slugify(title)
    for d in ["materials", "assets"]:
        (cdir / d).mkdir(parents=True, exist_ok=True)
    data = {"title": title, "source": args.source, "created": now()}
    write_if_missing(cdir / "README.md", render("coursepack_README.md", data))
    write_if_missing(cdir / "schedule.md", render("schedule.md", data))
    write_if_missing(cdir / "extracted-parts.md", render("extracted_parts.md", data))
    write_if_missing(cdir / "notes.md", f"# Notes\n\n- Course: {title}\n- Created: {now()}\n\n")
    if args.syllabus:
        parsed = urlparse(args.syllabus)
        if parsed.scheme in {"http", "https"}:
            (cdir / "syllabus.url").write_text(args.syllabus + "\n", encoding="utf-8")
        else:
            src = Path(args.syllabus).expanduser()
            if src.exists():
                shutil.copy2(src, cdir / src.name)
            else:
                print(f"warning: syllabus 文件不存在: {src}")
    res = path / "resources.md"
    if res.exists():
        append_text(res, f"| {title} | coursepack | {args.source} | 待补充 | 只抽取服务目标的部分(理由必填) | 待补充 | coursepacks/{slugify(title)}/ |\n")
    print(f"created coursepack: {cdir}")


def synthesis_cmd(args):
    path = Path(args.path).expanduser().resolve()
    ensure_repo_dirs(path)
    sdir = path / "synthesis"
    data = {"created": now()}
    write_if_missing(sdir / "source-map.md", render("synthesis_source_map.md", data))
    write_if_missing(sdir / "objective-map.md", render("synthesis_objective_map.md", data))
    write_if_missing(sdir / "conflicts.md", render("synthesis_conflicts.md", data))
    write_if_missing(sdir / "selected-path.md", render("synthesis_selected_path.md", data))
    print(f"created synthesis workspace: {sdir}")


def add_resource_cmd(args):
    path = Path(args.path).expanduser().resolve()
    res = path / "resources.md"
    if not res.exists():
        res.write_text(render("resources.md", {"topic": path.name}), encoding="utf-8")
    append_text(res, f"| {args.name} | {args.type} | {args.source} | {args.stage} | {args.use} | {args.level} | {args.notes} |\n")
    print(f"added resource to {res}")


def status_cmd(args):
    path = Path(args.path).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"not found: {path}")
    meta = read_meta(path)
    print(f"path: {path}")
    print(f"topic: {meta.get('topic', path.name)}")
    print(f"mode: {meta.get('mode', 'auto')}")
    state = path / "state.md"
    if state.exists():
        print("\n--- state.md ---")
        print(state.read_text(encoding="utf-8").strip())
    ok, out = run_git(path, ["status", "--short"])
    if ok:
        print("\n--- git status --short ---")
        print(out or "clean")


def commit_cmd(args):
    path = Path(args.path).expanduser().resolve()
    ok, _ = run_git(path, ["rev-parse", "--is-inside-work-tree"])
    if not ok:
        ok, out = run_git(path, ["init"])
        if not ok:
            raise SystemExit(out)
    run_git(path, ["add", "."])
    clean, _ = run_git(path, ["diff", "--cached", "--quiet"])
    if clean:
        print("nothing to commit")
        return
    ok, out = run_git(path, ["commit", "-m", args.message])
    if ok:
        print("committed: " + args.message)
        return
    if "user.name" in out or "user.email" in out or "Please tell me who you are" in out:
        print("hint: 未配置 git 身份。运行:\n"
              "  git config user.name 'Your Name'\n"
              "  git config user.email 'you@example.com'")
    raise SystemExit(out)


def audit_cmd(args):
    """检查学习仓库的资料入口是否唯一、可见、可进入。"""
    path = Path(args.path).expanduser().resolve()
    errors = []
    for name in ["labs", "videos", "readings", "coursepacks"]:
        if not (path / name).is_dir():
            errors.append(f"missing canonical directory: {name}/")

    root_readme = path / "README.md"
    if root_readme.exists():
        root_text = root_readme.read_text(encoding="utf-8")
        for name in ["labs/", "videos/", "readings/", "coursepacks/"]:
            if name not in root_text:
                errors.append(f"root README lacks directory-map entry: {name}")

    labs = path / "labs"
    if labs.is_dir():
        for item in labs.iterdir():
            if not item.is_dir():
                continue
            if item.is_symlink():
                errors.append(f"lab entry must not be a symlink: {item.relative_to(path)}")
                continue
            has_handout = any(item.glob("*.pdf"))
            if not ((item / "README.md").exists() or (item / "tests").exists() or has_handout):
                errors.append(f"lab lacks README/handout/tests: {item.relative_to(path)}")
            if (item / ".git").exists():
                ok, _ = run_git(item, ["rev-parse", "HEAD"])
                if not ok:
                    errors.append(f"lab git/submodule HEAD is not resolvable: {item.relative_to(path)}")

    videos = path / "videos"
    if videos.is_dir():
        for item in videos.iterdir():
            if not item.is_dir():
                continue
            if item.is_symlink():
                errors.append(f"video entry must not be a symlink: {item.relative_to(path)}")
                continue
            readme = item / "README.md"
            if not readme.exists():
                errors.append(f"video entry lacks README: {item.relative_to(path)}")
                continue
            text = readme.read_text(encoding="utf-8")
            if "## Overview" not in text and not re.search(r"(?m)^##\s+0?1[.)]", text):
                errors.append(f"video README lacks per-video overview: {readme.relative_to(path)}")
            if "## Role in plan" not in text and "对应 Stage" not in text and not re.search(r"Stage\s+\d+", text):
                errors.append(f"video README lacks stage/role mapping: {readme.relative_to(path)}")
            manifest = item / "manifest.json"
            if manifest.exists():
                try:
                    entries = json.loads(manifest.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    errors.append(f"invalid video manifest: {manifest.relative_to(path)}")
                else:
                    if isinstance(entries, list):
                        missing = [str(e.get("id")) for e in entries if e.get("id") and str(e.get("id")) not in text]
                        if missing:
                            errors.append(f"video README misses {len(missing)} manifest entries: {readme.relative_to(path)}")

    readings = path / "readings"
    if readings.is_dir():
        pdfs = list(readings.rglob("*.pdf"))
        if pdfs and not ((readings / "README.md").exists() or any(readings.glob("*index*.md"))):
            errors.append("readings with local PDFs must have README/index")
        for pdf in pdfs:
            try:
                valid = pdf.read_bytes()[:4] == b"%PDF"
            except OSError:
                valid = False
            if not valid:
                errors.append(f"invalid PDF file: {pdf.relative_to(path)}")

    forbidden = {"labs", "assignments", "videos", "readings", "supplements"}
    coursepacks = path / "coursepacks"
    if coursepacks.is_dir():
        for course in coursepacks.iterdir():
            if not course.is_dir():
                continue
            for name in forbidden:
                duplicate = course / name
                if duplicate.exists():
                    errors.append(f"duplicate material entry inside coursepack: {duplicate.relative_to(path)}")

    if errors:
        print("layout audit FAIL")
        for error in errors:
            print("- " + error)
        raise SystemExit(1)
    print("layout audit PASS")


def entry_cmd(args):
    """生成 index.html:plan.md 与 resources.md 的派生链接聚合页。纯链接,无任何进度元素。"""
    path = Path(args.path).expanduser().resolve()
    meta = read_meta(path)
    esc = html_mod.escape

    stages = []
    plan = path / "plan.md"
    if plan.exists():
        for ln in plan.read_text(encoding="utf-8").splitlines():
            if ln.startswith("## Stage"):
                stages.append(ln[3:].strip())

    rows = []
    res = path / "resources.md"
    if res.exists():
        for ln in res.read_text(encoding="utf-8").splitlines():
            s = ln.strip()
            if not s.startswith("|"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) < 7 or cells[0] in ("Name", "待补充") or set(cells[0]) <= set("- :"):
                continue
            rows.append(cells)

    def link(cell):
        c = cell.strip()
        if c.startswith("http://") or c.startswith("https://"):
            label = c if len(c) <= 64 else c[:61] + "..."
            return f'<a href="{esc(c)}">{esc(label)}</a>'
        return esc(c)

    def item(cells):
        return (f"<li><strong>{esc(cells[0])}</strong>({esc(cells[1])})— "
                f"{link(cells[2])}<br><span class='why'>{esc(cells[4])}</span></li>")

    used = set()
    sections = []
    for st in stages:
        lis = []
        for i, c in enumerate(rows):
            if c[3] and (c[3] in st or st.startswith(c[3])):
                lis.append(item(c))
                used.add(i)
        body = "<ul>" + "".join(lis) + "</ul>" if lis else "<p class='why'>暂无已登记资料。</p>"
        sections.append(f"<h2>{esc(st)}</h2>{body}")
    rest = [item(c) for i, c in enumerate(rows) if i not in used]
    if rest:
        sections.append("<h2>其他资料</h2><ul>" + "".join(rest) + "</ul>")

    doc = f"""<!doctype html>
<html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(meta.get('topic', '学习入口'))}</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem;line-height:1.65;color:#222}}
h1{{font-size:1.5rem}} h2{{font-size:1.15rem;margin-top:1.6rem;border-bottom:1px solid #ddd;padding-bottom:.2rem}}
li{{margin:.45rem 0}} .why{{color:#666;font-size:.9rem}} .nav a{{margin-right:1rem}}
footer{{margin-top:2.5rem;color:#888;font-size:.85rem;border-top:1px solid #eee;padding-top:.8rem}}
</style></head><body>
<h1>{esc(meta.get('topic', ''))}</h1>
<p>{esc(meta.get('goal', ''))}</p>
<p class="nav"><a href="mission.md">mission</a><a href="plan.md">plan</a><a href="state.md">state</a><a href="resources.md">resources</a></p>
{''.join(sections)}
<footer>本页是 plan.md 与 resources.md 的派生快照(生成于 {now()}),只做链接聚合。计划修订后可重新生成:
<code>python scripts/learning_skill.py entry &lt;repo&gt;</code>。本页不含进度统计——这不是管理面板。</footer>
</body></html>
"""
    out = path / "index.html"
    out.write_text(doc, encoding="utf-8")
    print(f"generated entry page: {out}")


def main():
    p = argparse.ArgumentParser(prog="learning_skill", description="Markdown + Git learning-state helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init")
    i.add_argument("path")
    i.add_argument("--topic", required=True)
    i.add_argument("--goal", default="待补充")
    i.add_argument("--mode", default="auto", choices=sorted(MODES))
    i.add_argument("--no-git", action="store_true")
    i.set_defaults(func=init_cmd)

    s = sub.add_parser("session")
    s.add_argument("path")
    s.add_argument("--title", default="session")
    s.set_defaults(func=session_cmd)

    la = sub.add_parser("lab")
    la.add_argument("path")
    la.add_argument("--name", required=True)
    la.set_defaults(func=lab_cmd)

    st = sub.add_parser("status")
    st.add_argument("path")
    st.set_defaults(func=status_cmd)

    c = sub.add_parser("commit")
    c.add_argument("path")
    c.add_argument("--message", required=True)
    c.set_defaults(func=commit_cmd)

    r = sub.add_parser("resource")
    r.add_argument("path")
    r.add_argument("--name", required=True)
    r.add_argument("--type", default="unknown")
    r.add_argument("--source", default="待补充")
    r.add_argument("--stage", default="待补充")
    r.add_argument("--use", default="待补充")
    r.add_argument("--level", default="待补充")
    r.add_argument("--notes", default="")
    r.set_defaults(func=add_resource_cmd)

    v = sub.add_parser("video")
    v.add_argument("path")
    v.add_argument("--title", required=True)
    v.add_argument("--source", required=True)
    v.add_argument("--transcript")
    v.add_argument("--overview", help="依据真实字幕/转写写的一段视频介绍")
    v.add_argument("--stage", default="待补充")
    v.add_argument("--role", default="supplement", choices=["main", "preview", "supplement"])
    v.add_argument("--mode", default="interval", choices=["interval", "scene"])
    v.add_argument("--every-seconds", type=int, default=30)
    v.set_defaults(func=video_cmd)

    co = sub.add_parser("course")
    co.add_argument("path")
    co.add_argument("--title", required=True)
    co.add_argument("--source", required=True)
    co.add_argument("--syllabus")
    co.set_defaults(func=course_cmd)

    sy = sub.add_parser("synthesis")
    sy.add_argument("path")
    sy.set_defaults(func=synthesis_cmd)

    au = sub.add_parser("audit")
    au.add_argument("path")
    au.set_defaults(func=audit_cmd)

    e = sub.add_parser("entry")
    e.add_argument("path")
    e.set_defaults(func=entry_cmd)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
