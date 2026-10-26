#!/usr/bin/env python3
"""Does this browser script click an application-SUBMIT control?

Reads a script on stdin and prints GATE if its click target looks like an
application submit control, ALLOW otherwise. Used by guard_no_submit.py.

It judges the CLICK TARGET, not the script's vocabulary. Matching "apply" or
"submit" anywhere in a script denies harmless work: typing a review prompt that
mentions an application, or clicking "Next" to read a page titled "Applicant
Form". Matching only a narrow keyword list lets a hyphenated
'button.send-application' through. So: take the expression up to the click,
resolve one hop back through a variable declaration, and match a wide keyword set.

    python submit_click_match.py --selftest
"""
import re, sys

CLICK = re.compile(r"\.click\b|\.submit\b|requestSubmit|dispatchEvent\s*\([^)]*[\"']click", re.I)
KEY = re.compile(r"appl(y|ication)|submit|send[ _-]?appl", re.I)
BOUND = re.compile(r"[;{}\n]")
# A form submission is a submission whatever the form is called.
HARD = re.compile(r"requestSubmit\s*\(|\.submit\s*\(", re.I)


def is_submit_click(s):
    if HARD.search(s):
        return True
    for m in CLICK.finditer(s):
        head = s[:m.start()]
        bounds = list(BOUND.finditer(head))
        expr = head[bounds[-1].end():] if bounds else head
        if KEY.search(expr[-200:]):
            return True
        v = re.search(r"([A-Za-z_$][\w$]*)\s*$", expr)
        if v:
            decl = re.findall(r"(?:const|let|var)\s+" + re.escape(v.group(1)) + r"\s*=([^;\n]*)", head)
            if decl and KEY.search(decl[-1]):
                return True
    return False


DENY = [
    ('() => { const b=[...document.querySelectorAll("button")].find(e=>/^apply$/i.test(e.textContent)); b.click(); }', "Apply button via variable"),
    ('() => document.querySelector("button.send-application").click()', "hyphenated send-application"),
    ('() => document.querySelector("form#job").requestSubmit()', "requestSubmit on a form"),
    ('() => { const b=document.querySelector("[data-testid=submit-application]"); b.click(); }', "submit-application testid"),
    ('() => { const btn=[...document.querySelectorAll("button")].find(x=>/send application/i.test(x.textContent)); btn.click(); }', "Send application text match"),
    ('() => document.querySelector("#applicationSubmit").click()', "applicationSubmit id"),
    ('() => { document.querySelector("#submit-application").dispatchEvent(new Event("click")); }', "dispatchEvent click on a submit control"),
]
ALLOW = [
    ('async () => { document.execCommand("insertText",false,"review this job application. VERDICT: READY TO SUBMIT"); const b=document.querySelector("button[data-testid=send-button]"); b.click(); }', "typing a review prompt, then sending it"),
    ('async () => { const next=[...document.querySelectorAll("button")].find(e=>/^next$/i.test(e.textContent)); next.click(); return document.body.innerText; }', "paging an Applicant Form to read it"),
    ('() => document.querySelector("#apply-btn").textContent', "pure read of an apply button"),
    ('() => { const m=[...document.querySelectorAll("button")].find(x=>/Add files/i.test(x.textContent)); m.click(); }', "opening an attach menu"),
    ('() => { const c=document.querySelector("button.cancel"); c.click(); }', "cancel button"),
    ('() => { const t=document.querySelector("[role=tab]"); t.click(); return document.title; }', "clicking a tab"),
]


def selftest():
    bad = 0
    for s, label in DENY:
        ok = is_submit_click(s)
        print(f"{'ok  ' if ok else 'FAIL'}  expect GATE   {label}")
        bad += not ok
    for s, label in ALLOW:
        ok = not is_submit_click(s)
        print(f"{'ok  ' if ok else 'FAIL'}  expect ALLOW  {label}")
        bad += not ok
    print(f"\n{len(DENY) + len(ALLOW) - bad}/{len(DENY) + len(ALLOW)} passed")
    return 1 if bad else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    print("GATE" if is_submit_click(sys.stdin.read()) else "ALLOW")
