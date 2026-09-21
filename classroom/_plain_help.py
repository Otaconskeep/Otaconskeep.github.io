"""Plain-language helpers and interactive widgets for Classroom lessons."""
from __future__ import annotations

import html as H
import re


def help_widget(mean: str, more: str = "") -> str:
    """Clickable 'What this means' / optional 'More detail' panels."""
    mean = mean.strip()
    more = more.strip()
    if not mean:
        return ""
    more_btn = (
        '<button type="button" class="cr-btn" data-cr="more" aria-expanded="false">More detail</button>'
        if more
        else ""
    )
    more_panel = (
        f'<div class="cr-panel more" hidden><strong>More detail:</strong> {H.escape(more)}</div>'
        if more
        else ""
    )
    return f'''<div class="cr-help">
 <div class="cr-actions">
  <button type="button" class="cr-btn mean" data-cr="mean" aria-expanded="false">What this means</button>
  {more_btn}
 </div>
 <div class="cr-panel mean" hidden><strong>In plain words:</strong> {H.escape(mean)}</div>
 {more_panel}
</div>'''


# Section-title → plain explanation (never mention reading level)
SECTION_PLAIN: dict[str, tuple[str, str]] = {
    "outcomes and vocabulary": (
        "These are the words you will keep hearing. Learn them once so later lessons feel less scary.",
        "If a word shows up again, open this section and match it to the table.",
    ),
    "vocabulary": (
        "This list is your pocket dictionary for the class. You do not need to memorize every word on day one.",
        "Come back here when a later step uses a term you forgot.",
    ),
    "lesson": (
        "This is the teaching part. Read it slowly. The lab comes next so you can try the idea with your hands.",
        "If a paragraph feels dense, tap What this means under that block.",
    ),
    "guided lab": (
        "Do these steps in order, one time, without skipping. Each step should leave proof you can show later.",
        "If a step fails, stop and use Break/fix instead of inventing a new path.",
    ),
    "lab": (
        "This is the hands-on part. Follow the numbered steps and keep notes of what you saw.",
        "",
    ),
    "break/fix exercises": (
        "You break one thing on purpose so you learn how it fails. Then you put it back. This builds real troubleshooting skill.",
        "Change only one thing at a time so you know what caused the failure.",
    ),
    "troubleshooting matrix": (
        "When something goes wrong, start with the matching row. Check the simple causes before you rebuild everything.",
        "Write down the symptom in the same words as the left column if you can.",
    ),
    "troubleshooting": (
        "This is your first-aid chart. Match the problem, then try the checks in order.",
        "",
    ),
    "knowledge check": (
        "Answer in your own words without looking first. This proves you understand, not that you can copy.",
        "If you miss one, re-read that section and try again before the gate.",
    ),
    "practical gate": (
        "These boxes are the pass rules. Check a box only when you have real proof for that line.",
        "“It seems to work” is not enough. Use a test, log, screenshot (secrets removed), or command output.",
    ),
    "2026 correction": (
        "Software screens change. The ideas stay. Prefer current official docs when a button moved.",
        "",
    ),
    "scope and legal boundary": (
        "Stay inside the rules: only use systems and content you are allowed to use. This keeps the class safe and honest.",
        "",
    ),
    "end-to-end architecture": (
        "This picture shows who talks to whom. Follow the arrows like a story from start to finish.",
        "If you get lost later, come back to this diagram first.",
    ),
    "architecture": (
        "This is the map of the system. Know which box does which job before you click around.",
        "",
    ),
    "service contracts before clicking": (
        "Write down names, ports, folders, and who owns the passwords before you connect apps. Planning first saves hours of guessing.",
        "Treat this like a contacts list for your services.",
    ),
    "hardlinks": (
        "A hardlink is two names for the same file on disk. You do not make a second full copy, so you save space.",
        "It only works when both paths are on the same filesystem and permissions allow it.",
    ),
    "persistence": (
        "Containers can be deleted. Your important files must live in a folder or volume that survives recreate.",
        "Always test: destroy the container, bring it back, and prove the data is still there.",
    ),
    "secrets": (
        "Passwords and API keys are secret. Do not put them in public notes, screenshots, or git commits.",
        "If a secret leaks, rotate it (make a new one and retire the old one).",
    ),
}


KIND_PLAIN = {
    "lab": ("Do the steps in order. Keep proof of each success.", "Stop on failure; do not invent extra steps yet."),
    "break": ("Break one piece, watch the failure, then repair it. That is how you learn diagnosis.", ""),
    "quiz": ("Answer from memory first. Then check yourself.", ""),
    "diagram": ("Read the arrows top to bottom. Each box has one job.", ""),
    "vocab": ("These words are tools. Learn what each tool is for.", ""),
    "trouble": ("Match your symptom, then check the short list.", ""),
    "tip": ("Read this before you rush. It keeps you safe or up to date.", ""),
    "gate": ("Only check a box when you have evidence.", ""),
}


# Keyword rules for lab / prose steps → plain words
STEP_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bbackup\b", re.I), "Make a safety copy first so a mistake does not erase your work."),
    (re.compile(r"\bdocker\s+compose\b", re.I), "Compose is the recipe file that starts and stops your app group together."),
    (re.compile(r"\bdocker\s+network\b|\bmedia_net\b|\bproject network\b", re.I), "A Docker network is a private chat room so containers can find each other by name."),
    (re.compile(r"\bservice name\b|\bDNS\b|resolve and reach", re.I), "Use the container’s name like a phone contact, not “localhost,” unless they truly share one network bubble."),
    (re.compile(r"\bAPI key\b", re.I), "An API key is a password apps use to talk to each other. Keep it private."),
    (re.compile(r"\bindexer\b", re.I), "An indexer is a search source. You only add ones you are allowed to use."),
    (re.compile(r"\bsync\b", re.I), "Sync means copy the settings from one app into another so they match."),
    (re.compile(r"\bcategor(y|ies)\b", re.I), "A category is a label that keeps TV and movies (or other jobs) in separate piles."),
    (re.compile(r"\broot folder\b", re.I), "A root folder is the shelf where finished files should live."),
    (re.compile(r"\bhardlink\b|\binode\b", re.I), "Check that two paths are the same file underneath, not a wasteful second copy."),
    (re.compile(r"\bvolume\b|\bbind mount\b", re.I), "This connects a real folder on your computer into the container so data can stay."),
    (re.compile(r"\bport\b", re.I), "A port is the door number you use in the browser to open the app."),
    (re.compile(r"\bhealth\b|\bhealthcheck\b", re.I), "A health check asks “are you really ready?” not just “did the process start?”"),
    (re.compile(r"\blog\b", re.I), "Logs are the app’s diary. Read the newest lines when something breaks."),
    (re.compile(r"\bpermission\b|\bPUID\b|\bPGID\b|\bownership\b", re.I), "If the app cannot write files, the user numbers (who owns the folder) are probably wrong."),
    (re.compile(r"\bVPN\b|\bGluetun\b|\btunnel\b", re.I), "This path is about safe remote reach or private download traffic — not opening every admin page to the world."),
    (re.compile(r"\bHome Assistant\b|\bentity\b|\bautomation\b", re.I), "Home Assistant watches sensors and runs if-this-then-that rules for your house."),
    (re.compile(r"\bwake word\b|\bSTT\b|\bTTS\b|\bWhisper\b|\bPiper\b", re.I), "Voice is a chain: hear → turn into text → decide → speak back. Test one link at a time."),
    (re.compile(r"\blocalhost\b", re.I), "Localhost means “this same machine/container.” From inside another container it often points at the wrong place."),
    (re.compile(r"\bYAML\b|\bcompose\.ya?ml\b", re.I), "YAML is the indented text file that describes your services. Spaces matter."),
    (re.compile(r"\brecreate\b|\bdestroy\b|\bup -d\b", re.I), "Tear it down and bring it back to prove your data and settings really survive."),
    (re.compile(r"\bquality profile\b|\bcustom format\b|\bTRaSH\b", re.I), "These rules grade releases so your apps pick the quality you actually want."),
    (re.compile(r"\bSeerr\b|\bOverseerr\b|\bJellyseerr\b|\brequest\b", re.I), "The request app is the friendly front desk. Family uses it instead of the admin tools."),
]


def plain_for_section(h2: str, kind: str) -> tuple[str, str]:
    key = h2.lower().strip()
    if key in SECTION_PLAIN:
        return SECTION_PLAIN[key]
    for k, v in SECTION_PLAIN.items():
        if k in key or key in k:
            return v
    return KIND_PLAIN.get(kind, (
        "Read this block, then try the next action. If you feel stuck, tap What this means.",
        "",
    ))


def plain_for_step(text: str) -> str:
    for pat, mean in STEP_RULES:
        if pat.search(text):
            return mean
    # Generic fallback — still helpful, never says "6th grade"
    clean = re.sub(r"`[^`]+`", "that command", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    if len(clean) > 140:
        clean = clean[:137] + "…"
    return f"Do this carefully, then check that it worked before moving on. ({clean})"


def plain_for_paragraph(text: str) -> str:
    t = text.strip()
    if not t:
        return ""
    for pat, mean in STEP_RULES:
        if pat.search(t):
            return mean
    # Soften dense first sentence
    first = re.split(r"(?<=[.!?])\s+", t)[0]
    first = re.sub(r"`[^`]+`", "this setting", first)
    if len(first) > 160:
        first = first[:157] + "…"
    return f"Big idea: {first}"


def extract_numbered_steps(md: str) -> list[str] | None:
    """Return numbered steps if the body is primarily an ordered list."""
    steps = []
    for line in md.splitlines():
        m = re.match(r"^(\d+)\.\s+(.+)$", line.strip())
        if m:
            steps.append(m.group(2).strip())
    # Prefer step cards when we have a real lab list
    if len(steps) >= 3:
        return steps
    return None


def extract_h3_blocks(md: str) -> list[tuple[str, str]] | None:
    """Split ### subsections for break/fix style content."""
    if "### " not in md:
        return None
    parts = re.split(r"^###\s+(.+)$", md, flags=re.M)
    # parts[0]=preamble, then title, body, title, body...
    if len(parts) < 3:
        return None
    blocks = []
    preamble = parts[0].strip()
    if preamble:
        blocks.append(("", preamble))
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        blocks.append((title, body))
    return blocks


def kind_class(kind: str) -> str:
    return {
        "lab": "cr-box cr-box-lab",
        "break": "cr-box cr-box-break",
        "quiz": "cr-box cr-box-quiz",
        "diagram": "cr-box cr-box-diagram",
        "vocab": "cr-box cr-box-vocab",
        "trouble": "cr-box cr-box-trouble",
        "tip": "cr-callout tip",
        "gate": "cr-check",
        "box": "cr-box",
    }.get(kind, "cr-box")


def kind_badge(kind: str) -> str:
    labels = {
        "lab": ("lab", "Hands-on"),
        "break": ("break", "Break / fix"),
        "quiz": ("quiz", "Check yourself"),
        "diagram": ("map", "Map"),
        "vocab": ("words", "Words"),
        "trouble": ("fix", "Fix chart"),
        "tip": ("tip", "Tip"),
        "gate": ("gate", "Pass gate"),
        "box": ("learn", "Learn"),
    }
    cls, label = labels.get(kind, ("learn", "Learn"))
    return f'<span class="cr-chip cr-chip-{cls}">{label}</span>'
