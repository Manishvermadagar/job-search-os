#!/usr/bin/env python3
"""ceiling_quote.py - quote the career bank verbatim for a review prompt.

A reviewer applies a rule exactly as it is framed in the prompt, even when the
real file is attached. Restating from memory what the career bank grants (merging
two lines into one, getting a line number wrong) makes the reviewer block claims
that are the career bank's own sentences. So never type what the ceiling grants:
generate it.

    python engine/ceiling_quote.py 12 18 24
    python engine/ceiling_quote.py --grep "routing"
    python engine/ceiling_quote.py --verbs        # every line with a construction verb
    python engine/ceiling_quote.py --demo --grep "hired"

Output is a paste-ready block of `career-bank.md:N - "..."` lines.
"""
import argparse, os, re, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERBS = r"\b(built|build|building|shipped|developed|designed|created|implemented|coded|engineered|architected|launched|led)\b"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lines", nargs="*", type=int, help="line numbers to quote")
    ap.add_argument("--grep", help="quote every line matching this text (case-insensitive)")
    ap.add_argument("--verbs", action="store_true", help="quote every line carrying a construction verb")
    ap.add_argument("--demo", action="store_true", help="read examples/sample-career-bank.md")
    a = ap.parse_args()

    bank = os.path.join(REPO, "examples", "sample-career-bank.md") if a.demo else \
        os.path.join(REPO, "resume-data", "career-bank.md")
    if not os.path.exists(bank):
        sys.exit(f"career bank not found: {os.path.relpath(bank, REPO)}")
    with open(bank, encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()

    nums = list(a.lines)
    if a.grep:
        rx = re.compile(re.escape(a.grep), re.I)
        nums += [i for i, L in enumerate(lines, 1) if rx.search(L)]
    if a.verbs:
        rx = re.compile(VERBS, re.I)
        nums += [i for i, L in enumerate(lines, 1) if rx.search(L) and not L.lstrip().startswith("#")]
    if not nums:
        ap.print_help()
        return 2

    print("QUOTED VERBATIM FROM career-bank.md - paste as-is; do not paraphrase into a prompt.\n")
    for n in sorted(set(nums)):
        if not 1 <= n <= len(lines):
            print(f"  career-bank.md:{n} - !! OUT OF RANGE (file has {len(lines)} lines)")
            continue
        t = re.sub(r"\s*\[tags:[^\]]*\]\s*$", "", re.sub(r"^[-*]\s*", "", lines[n - 1].strip()))
        print(f'  career-bank.md:{n} - "{t}"')
    return 0


if __name__ == "__main__":
    sys.exit(main())
