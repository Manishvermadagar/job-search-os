"""Shared helpers for the engine's check programs.

Every check takes one argument, the application folder, and exits 0 (pass) or
1 (fail) with the reason on stdout. Paths inside channels.json are resolved
against the application folder first, then against the repo root.
"""
import json, os, re, shutil, subprocess, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CHECKS = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.dirname(CHECKS)
REPO = os.path.dirname(ENGINE)
CHANNEL_STATES = ("INTENDED", "NOT_AVAILABLE", "DEFERRED")


def folder_arg():
    if len(sys.argv) < 2:
        print("usage: <check>.py <application folder>")
        sys.exit(2)
    return os.path.abspath(sys.argv[1])


def is_demo(folder):
    """Demo runs (folders named demo-*) read the fictional sample career bank,
    never the user's real one. Same rule as CLAUDE.md's demo mode."""
    return os.path.basename(os.path.normpath(folder)).startswith("demo-")


def career_bank(folder):
    if os.environ.get("JSO_CAREER_BANK"):
        return os.environ["JSO_CAREER_BANK"]
    if is_demo(folder):
        return os.path.join(REPO, "examples", "sample-career-bank.md")
    return os.path.join(REPO, "resume-data", "career-bank.md")


def resolve(folder, p):
    p = str(p)
    if os.path.isabs(p):
        return p
    local = os.path.join(folder, p)
    return local if os.path.exists(local) else os.path.join(REPO, p)


def read(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def load_json(folder, name, default=None):
    p = os.path.join(folder, name)
    if not os.path.exists(p):
        return default
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except ValueError as e:
        fail_now([f"{name} is not valid JSON: {e}"])


def channels(folder):
    d = load_json(folder, "channels.json")
    if d is None:
        fail_now(["no channels.json - the 'channels' step writes it"])
    return d


def intended(folder):
    return {k: v for k, v in channels(folder).items() if (v or {}).get("status") == "INTENDED"}


def answers(folder):
    """Every answer file any INTENDED channel sends, as (channel, relpath, abspath)."""
    out = []
    for key, ch in intended(folder).items():
        for a in ((ch.get("contains") or {}).get("answers") or []):
            out.append((key, str(a), resolve(folder, a)))
    return out


def answer_id(relpath):
    return os.path.splitext(os.path.basename(relpath))[0]


def nonempty(path):
    return os.path.exists(path) and os.path.getsize(path) > 0


def extract_text(path):
    """Text as an employer reads it: extracted from the rendered file."""
    low = path.lower()
    if low.endswith(".pdf"):
        if not shutil.which("pdftotext"):
            return None
        r = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True,
                           text=True, encoding="utf-8", errors="ignore")
        return r.stdout
    if low.endswith(".docx"):
        try:
            from docx import Document
        except ImportError:
            return None
        return "\n".join(p.text for p in Document(path).paragraphs)
    return read(path)


def last_verdict(text, name, verdict_re):
    """The verdict that counts for one named file: the LAST verdict found after the
    file's LAST mention. Earlier passes on an older draft do not count."""
    i = text.rfind(name)
    if i < 0:
        return None
    hits = re.findall(verdict_re, text[i:], re.I)
    return hits[-1].upper() if hits else None


def fail_now(problems, header="CHECK FAILED"):
    print(header + ":")
    for p in problems:
        print("  - " + p)
    sys.exit(1)


def finish(problems, ok_msg, header="CHECK FAILED"):
    if problems:
        fail_now(problems, header)
    print(ok_msg)
    sys.exit(0)
