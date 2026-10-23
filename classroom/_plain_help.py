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
    "what a virtual machine is": (
        "A virtual machine is a full computer made of software. It runs inside your real computer and gets its own fake hardware.",
        "The guest OS does not know it is sharing your laptop. Treat it like a second PC you can delete.",
    ),
    "why you want one": (
        "VMs let you practice and break things without wrecking the computer you use every day.",
        "Safe practice, other operating systems, and isolation are the three big wins.",
    ),
    "hypervisors: type 2 vs type 1": (
        "The hypervisor is the app (or OS) that creates VMs. Type 2 sits on your normal OS. Type 1 replaces it on dedicated hardware.",
        "Same goal, make guests. Different place in the stack and different power.",
    ),
    "path a: type 2 on your daily computer (virtualbox)": (
        "This path installs VirtualBox on the computer you already use. Good when you have no spare PC yet.",
        "Finish a working guest and snapshots here, then plan a Proxmox box for later classes.",
    ),
    "path b: type 1 on spare hardware (proxmox ve)": (
        "This path installs Proxmox on a machine you can dedicate. That is the Academy’s default for later labs.",
        "Back up the disk first. Prefer wired Ethernet for the host.",
    ),
    "vm vs lxc vs docker": (
        "A VM has its own kernel. An LXC shares the host kernel. Docker packages apps and is a different layer again.",
        "This course puts Docker inside a Linux VM so each layer stays understandable.",
    ),
    "isolation vs convenience (both paths)": (
        "Every sharing feature makes the sandbox thinner. Turn them on only when you need them.",
        "Bridged LAN, clipboard, and shared folders are convenience doors, not free upgrades.",
    ),
    "firmware: turn on hardware virtualization": (
        "Your CPU has a switch for virtualization. Turn it on in BIOS/UEFI or 64-bit guests may fail.",
        "Look for VT-x / VMX (Intel) or AMD-V / SVM (AMD).",
    ),
    "safety boundary": (
        "These rules keep powerful tools from becoming accidents. Read them before you connect SSH or agents.",
        "Least privilege first. Approval before mutation. No public admin UI.",
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
    "learning objective": (
        "This is the finish line for the class: a task you should be able to do, not a vague 'understand.'",
        "If you cannot restate it as something you can perform, you are not ready for the gate.",
    ),
    "why this matters": (
        "This gives you a reason to care before the theory. Context first, then details.",
        "",
    ),
    "prior-knowledge check": (
        "Warm up your brain. Wrong answers are useful: they show what to review.",
        "Do not skip ahead. Activation makes the lesson stick.",
    ),
    "instruction": (
        "This is the teaching core. One major concept (or a tight group). Read carefully.",
        "Use What this means under dense blocks.",
    ),
    "worked example": (
        "I do: watch the bad → better reasoning. Steal the thinking, not just the answer.",
        "",
    ),
    "guided practice": (
        "We do: try with hints. Compare your reasoning to the lesson.",
        "",
    ),
    "independent practice": (
        "You do: close the hints. Struggle is part of learning.",
        "",
    ),
    "feynman teach-back": (
        "If you cannot explain it simply, you do not own it yet. This section is required for mastery.",
        "Weak spots are gold: restudy that part and rewrite.",
    ),
    "retrieval check": (
        "Write from memory first. Retrieval beats rereading.",
        "Target about 80% before the practical gate.",
    ),
    "feedback / common mistakes": (
        "These are the traps other students fall into. Check yourself against the list.",
        "",
    ),
    "practical mastery gate": (
        "Pass only with evidence. Feynman + practice + checkboxes unlock the next class.",
        "If you fail: feedback → review → new practice → reassess.",
    ),
    "reflection": (
        "Name what you learned, where you struggled, and how it connects backward and forward.",
        "",
    ),
    "spiral hook": (
        "This skill will return later. Knowing the hook helps you notice it when it does.",
        "",
    ),
    "break / fix": (
        "Break one thing on purpose, watch the failure, then repair it.",
        "Change only one variable at a time.",
    )
}


KIND_PLAIN = {
    "feynman": ("Explain it simply. If you cannot, restudy and retry.", "Required for unlock."),
    "objective": ("This is what done looks like for the class.", ""),
    "why": ("Care first, then theory.", ""),
    "prior": ("Activate old knowledge before new.", ""),
    "learn": ("Core teaching. One concept at a time.", ""),
    "example": ("Study the reasoning in the worked example.", ""),
    "practice": ("Hints first, then no hints.", ""),
    "reflect": ("Metacognition: learn, struggle, connect.", ""),
    "spiral": ("This idea comes back later on purpose.", ""),
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
    (re.compile(r"\bVirtualBox\b|\bExtension Pack\b", re.I), "VirtualBox is a free Type 2 hypervisor, an app on your normal OS that creates guest computers."),
    (re.compile(r"\bProxmox\b", re.I), "Proxmox is a Type 1 hypervisor you install on dedicated hardware and manage in a web browser."),
    (re.compile(r"\bType\s*[12]\b|\bhypervisor\b", re.I), "A hypervisor creates and runs virtual machines. Type 2 sits on your OS; Type 1 sits on the hardware."),
    (re.compile(r"\bVT-x\b|\bAMD-V\b|\bSVM\b|\bVMX\b|\bfirmware\b.*virtual", re.I), "This is the BIOS/UEFI switch that lets your CPU run virtual machines well. Turn it on, save, reboot."),
    (re.compile(r"\bsnapshot\b", re.I), "A snapshot is a restore point. Take one before a risky change so you can roll back fast."),
    (re.compile(r"\bclone\b", re.I), "A clone is a full copy of a VM. Break the copy; keep the original clean."),
    (re.compile(r"\bNAT\b", re.I), "NAT lets the guest use the host’s internet path. The guest is usually not a full peer on your home LAN."),
    (re.compile(r"\bbridged?\b", re.I), "Bridged networking puts the guest on the real LAN with its own address, handy and less isolated."),
    (re.compile(r"\bISO\b", re.I), "An ISO is the install disc as a file. Attach it to the VM like inserting an installer DVD."),
    (re.compile(r"\bhost key\b|Right Ctrl", re.I), "The host key releases mouse and keyboard from the guest window back to your real desktop."),
    (re.compile(r"\bLXC\b|\bcontainer template\b", re.I), "LXC is a lightweight Linux system that shares the host kernel, fast to start, less separate than a VM."),
    (re.compile(r"\bvmbr0\b", re.I), "vmbr0 is Proxmox’s usual virtual switch. Guests plug into it to reach the network."),
    (re.compile(r"\bn8n\b", re.I), "n8n is a self-hosted automation app. You connect nodes into a workflow that moves JSON items."),
    (re.compile(r"\bworkflow\b", re.I), "A workflow is the whole automation graph, triggers, nodes, and how data flows between them."),
    (re.compile(r"\bwebhook\b", re.I), "A webhook is a secret URL another service can POST to. Treat it like a password."),
    (re.compile(r"\bhuman-in-the-loop\b|\bneeds_approval\b|\bapproval\b", re.I), "Pause for a human yes/no before the automation changes anything important."),
    (re.compile(r"\bAI [Aa]gent\b|\bKeep Agent\b", re.I), "An agent is a model plus tools. It can choose checks, but mutating tools stay behind approval."),
    (re.compile(r"\bAI CLI\b|\bClaude Code\b|\bgemini cli\b|\bheadless\b", re.I), "An AI CLI is a terminal AI tool. n8n can SSH in and run it headless, then read the text it prints."),
    (re.compile(r"\bsession[- ]?id\b|\bUUID\b", re.I), "A session id lets you resume the same AI conversation later, like continuing a chat instead of starting over."),
    (re.compile(r"\borchestrator\b", re.I), "n8n starts and routes the work; the AI CLI (or other tools) do the heavy thinking on a jump host."),
    (re.compile(r"\bIPv4\b|\bIP address\b|\bsubnet mask\b|\bnetmask\b", re.I), "An IP address is how devices find each other on a network. The mask tells which part is the ‘street’ and which part is the ‘house number.’"),
    (re.compile(r"\bdefault gateway\b|\bdefault router\b", re.I), "The gateway is your router’s address on the LAN, the courier when the destination is not on your street."),
    (re.compile(r"\bDHCP\b", re.I), "DHCP is how most home devices get an IP automatically from the router."),
    (re.compile(r"\bbroadcast\b", re.I), "The broadcast address talks to every host on that subnet. Do not assign it to a normal device."),
    (re.compile(r"\bclassful\b|\bClass [ABCDE]\b", re.I), "Old IPv4 classes A–C each had a default mask size. Learn the chart for exams; real labs use classless masks (CIDR)."),
    (re.compile(r"\bclassless\b|\bCIDR\b", re.I), "Classless means you choose the mask that fits, you are not stuck with the old Class A/B/C default."),
    (re.compile(r"\bloopback\b|\b127\.0\.0\.1\b", re.I), "Loopback talks only to this computer. Ping 127.0.0.1 to check the local IP stack."),
    (re.compile(r"\bIANA\b", re.I), "IANA sits at the top of public IP number allocation. Regions and ISPs get slices under that system."),
    (re.compile(r"\bmulticast\b", re.I), "Multicast (Class D) sends to a group of listeners. Do not use it as a normal host address."),
    (re.compile(r"\bping\b", re.I), "Ping asks “are you reachable?” with a small echo packet. First tool when something seems offline."),
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
    (re.compile(r"\bVPN\b|\bGluetun\b|\btunnel\b", re.I), "This path is about safe remote reach or private download traffic: not opening every admin page to the world."),
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
    # Prefer the bold step title when present
    m = re.match(r"\*\*([^*]+)\*\*", text.strip())
    if m:
        title = m.group(1).strip().rstrip(".")
        return f"Do this step fully, then check that it worked before the next one. Focus: {title}."
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


def extract_numbered_steps(md: str, *, min_steps: int = 1) -> list[str] | None:
    """Return numbered steps, including continuation lines under each item."""
    lines = md.splitlines()
    steps: list[str] = []
    i = 0
    while i < len(lines):
        m = re.match(r"^(\d+)\.\s+(.*)$", lines[i])
        if not m:
            i += 1
            continue
        chunk = [m.group(2)]
        i += 1
        in_fence = False
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                chunk.append(line)
                i += 1
                continue
            if not in_fence:
                if re.match(r"^\d+\.\s+", line):
                    break
                # Only ATX ##+ headings end a step. Do not treat bash `# comments` as headings.
                if re.match(r"^#{2,6}\s+\S", line):
                    break
            chunk.append(line)
            i += 1
        text = "\n".join(chunk).strip()
        if text:
            steps.append(text)
    if len(steps) >= min_steps:
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
        "feynman": "cr-box cr-box-feynman",
        "objective": "cr-box cr-box-objective",
        "why": "cr-box cr-box-why",
        "prior": "cr-box cr-box-prior",
        "learn": "cr-box cr-box-learn",
        "example": "cr-box cr-box-example",
        "practice": "cr-box cr-box-practice",
        "reflect": "cr-box cr-box-reflect",
        "spiral": "cr-box cr-box-spiral",
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
        "feynman": ("feynman", "Teach it back"),
        "objective": ("goal", "Objective"),
        "why": ("why", "Why it matters"),
        "prior": ("prior", "Prior check"),
        "learn": ("learn", "Instruction"),
        "example": ("example", "I do"),
        "practice": ("practice", "Practice"),
        "reflect": ("reflect", "Reflect"),
        "spiral": ("spiral", "Spiral"),
        "box": ("learn", "Learn"),
    }
    cls, label = labels.get(kind, ("learn", "Learn"))
    return f'<span class="cr-chip cr-chip-{cls}">{label}</span>'
