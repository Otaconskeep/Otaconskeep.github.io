# Class 14 — n8n automation for the homelab

**Build output:** n8n in Docker; RSS digest workflow; guarded Keep Agent; optional n8n→SSH→AI-CLI bridge with a resumable session

## What you will learn

You will install n8n on your lab host, learn how workflows move **items** of JSON between **nodes**, build a safe first automation (RSS → filter → notify), and then build a small AI agent that can **observe** your lab—and only **change** things after a human approval step. You will also learn a second pattern: use n8n as an **orchestrator** that SSHes into a Linux box and runs a headless **AI CLI** (Claude Code, Gemini CLI, or similar) so the heavy context and skills stay on the terminal tool while n8n handles triggers, chat front-ends, and session IDs. You will treat credentials, SSH, and command execution as high-risk tools with explicit guardrails.

## Vocabulary

| Term | Meaning |
|---|---|
| Workflow | One automation graph: triggers + nodes + connections |
| Trigger | What starts a run (manual, schedule, webhook, chat) |
| Node | One step that reads/transforms/sends data or calls a tool |
| Item | One JSON object flowing through the graph (often many items in parallel) |
| Credential | Stored secret/connection (API key, webhook URL, SSH login) |
| Expression | Small template that pulls fields from JSON (`{{ $json.title }}`) |
| Pin data | Freeze test output on a node so later steps can reuse it without re-calling APIs |
| Sub-workflow | A workflow called as a **tool** by an AI agent |
| Structured output | Force the model to return predictable JSON fields for branching |
| Human-in-the-loop | Pause for approve/deny before risky actions |
| AI CLI | Terminal AI tool (Claude Code, Gemini CLI, Codex, …) run headless from scripts/SSH |
| Headless / print mode | Non-interactive one-shot prompt (`-p` / equivalent)—no TTY chat UI |
| Session ID | Stable ID so a later command can **resume** the same AI conversation |
| Orchestrator pattern | n8n triggers/routes/notifies; the AI CLI owns deep context, skills, and multi-step tools |

## Safety boundary

n8n can talk to email, chat, SSH, APIs, and shells. That power cuts both ways.

- Prefer **read-only** checks first (HTTP GET, `docker ps`, status APIs).
- Never paste production API keys into the workbook or public Discord.
- Do **not** give an agent unrestricted root SSH on day one.
- Any command that **creates, deletes, stops, or rewrites** systems must go through **approval**.
- Keep n8n’s admin UI on LAN/VPN only (Class 10 patterns)—not open to the world.
- AI CLI “dangerous” / YOLO flags that skip confirmations are **lab-only** and still need your approval gate in n8n before mutate.
- Put the AI CLI on a **jump host** you control; do not SSH as root into every production box from n8n on day one.

## Lesson

### What n8n is

n8n is an open-source workflow automation platform you can self-host. Visually, you connect nodes. Under the hood, each node receives JSON **items**, does work, and passes items forward. One RSS node that returns 13 articles hands **13 items** to the next node—so a “send message” node may fire 13 times unless you **limit**, **aggregate**, or **batch** deliberately.

Compared with hosted “if this then that” SaaS tools, self-hosted n8n keeps credentials and execution inside **your** boundary—when you install it that way.

```text
Trigger → (optional) fetch/transform → action / notify / agent tools
                ↑
         credentials + JSON items
```

### Where it sits in this Academy

```text
Proxmox / Docker host (Classes 1–4)
  → n8n container
      → Discord/Telegram (notify)
      → HTTP checks (HA, websites)
      → SSH / APIs (Proxmox, NAS)  [guarded]
```

Install n8n **beside** your stacks, not inside every ARR container. Give it a dedicated Compose project and volume for its database.

### Core UI habits

1. **Save often.**
2. **Execute step** while building; use **Pin** on expensive/AI nodes so you do not re-spend tokens.
3. Inspect the connector badges: `1 item` vs `N items` explains “why Discord said hi thirteen times.”
4. Credentials live under a separate library—reuse them; do not hard-code secrets in node fields when a credential type exists.

### Data shaping nodes you will reuse

| Node idea | Why it exists |
|---|---|
| Limit | Cap how many items continue |
| Filter / If / Switch | Branch on fields |
| Edit Fields (Set) | Keep only the columns you want |
| Split Out | Turn one array field into many items |
| Merge | Combine branches (use carefully with unequal item counts) |
| Code (optional) | Last resort—prefer built-ins first |

### AI in n8n (two different powers)

1. **LLM chain / summarize** — transform text (summarize an article).
2. **AI Agent + tools** — model chooses tools (HTTP, workflow-as-tool SSH) based on a system prompt.

Agents need: a chat/LLM credential, a clear **system message** (who they are / what they may do), and tools with honest descriptions. For autonomous schedules, replace chat input with an **Edit Fields** prompt + stable session/chat id for memory.

### Guarded autonomy pattern (Keep Agent)

```text
Schedule → set prompt → Agent (observe tools only)
  → structured JSON { ok: bool, needs_approval: bool, commands: [], message }
  → If needs_approval → notify + wait for approve → re-enter agent with approval
  → If not ok and no approval path → alert only
  → Never auto-run destructive commands without approval
```

### n8n + AI CLI over SSH (orchestrator pattern)

Sometimes the built-in n8n AI Agent is enough. Sometimes you already live in a **terminal AI tool** that has your repos, skills, and local files. You can combine them without inventing a custom HTTP wrapper:

```text
Chat / Schedule / Webhook (n8n)
  → SSH node → Linux host
      → AI CLI headless command (claude / gemini / …)
          → stdout JSON/text back into n8n
  → Notify / If / loop with same session id
```

**Why this is useful**

1. **Context** — `cd` into a project directory before the AI CLI runs so it sees real files, not an empty sandbox.
2. **Subscription economics** — token-heavy research can stay on a CLI plan you already pay for, while n8n handles timing and messaging.
3. **Skills / multi-step tools** — complex “how to talk to UniFi / Proxmox” knowledge can live as markdown/skills next to the CLI; n8n stays a thin trigger.
4. **Sessions** — generate a UUID once, pass `--session-id` (or product equivalent), then later resume with `-r` / resume flag so Slack/Discord can hold a real conversation.

**Where to install the AI CLI**

Anywhere Linux-capable you trust: the same VM as n8n, a Raspberry Pi, or a dedicated Ubuntu jump host beside the lab. Prefer “next to the files and APIs you want it to see,” not “on every router.”

**SSH gotchas**

n8n’s SSH session is often a non-login shell. If `claude --version` works in your interactive terminal but fails from n8n, fix PATH / login profile for that SSH user (workbook the exact error). Test with `hostname` first, then the AI CLI version flag.

**Headless prompt shape (illustrative—check current CLI flags)**

```bash
cd /path/to/project && claude -p "Summarize README.md in five bullets"
```

Resume:

```bash
claude -p "Continue: what should I fix first?" -r --session-id "$SESSION_UUID"
```

Exact flags differ by tool and version—verify against that tool’s current docs. The Academy skill is the **pattern**, not a frozen flag list.

**Chat front-end loop (Slack/Discord/Telegram)**

```text
Inbound message → ensure session UUID exists → SSH AI CLI with -p + session
  → reply to chat
  → ask “done?” → If no → loop with -r same session → If yes → end
```

Keep the UUID in workflow static data or a database node so a phone conversation can span many messages.

**Architecture shift**

```text
n8n  = scheduler, webhooks, human gates, notifications
AI CLI = deep context, skills, parallel sub-agents on the jump host
```

You can still call an in-n8n AI Agent that *decides* to invoke the SSH→CLI tool. Do not abandon Class 14 Path C guardrails when the CLI is powerful.

## Guided lab

**Prereqs:** Class 2 Compose working on a Linux host/VM; Discord or Telegram you control; optional Ollama or an API key you are allowed to use.

### Path A — Install n8n with Compose

1. **Create a dedicated project directory.**

:::linux
```bash
mkdir -p ~/n8n-lab && cd ~/n8n-lab
```
:::

:::windows
```powershell
mkdir $HOME\n8n-lab -Force
cd $HOME\n8n-lab
```
:::

2. **Write a minimal Compose file** (adjust ports if `5678` is taken). Prefer current official n8n image tags from docs—pin an explicit version when you find one you trust:

:::linux
```bash
cat > compose.yaml <<'YAML'
name: n8n-lab
services:
  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - NODE_ENV=production
      - WEBHOOK_URL=http://N8N-HOST:5678/
      - GENERIC_TIMEZONE=America/Los_Angeles
    volumes:
      - ./n8n_data:/home/node/.n8n
YAML
# Replace WEBHOOK_URL host with your lab IP/DNS after first boot.
docker compose config
docker compose pull
docker compose up -d
docker compose ps
docker compose logs --tail=40 n8n
```
:::

:::windows
```powershell
@'
name: n8n-lab
services:
  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - NODE_ENV=production
      - WEBHOOK_URL=http://127.0.0.1:5678/
      - GENERIC_TIMEZONE=America/Los_Angeles
    volumes:
      - ./n8n_data:/home/node/.n8n
'@ | Set-Content -Encoding utf8 compose.yaml
docker compose config
docker compose up -d
docker compose ps
```
:::

3. **Open the UI and finish owner setup.** Browser: `http://N8N-HOST:5678`. Create the owner account. Skip marketing extras. Record the URL in the workbook—**do not** publish port 5678 to the internet.

:::linux
```bash
curl -sI http://127.0.0.1:5678/ | head
```
:::

:::windows
```powershell
curl.exe -sI http://127.0.0.1:5678/
```
:::

4. **Prove persistence:** `docker compose down && docker compose up -d` and confirm you still log in (data volume kept).

### Path B — First workflow: RSS digest → Discord

1. **Create workflow** → add **Manual Trigger** and optional **Schedule** (daily). Connect both into the same next node later if you want.

2. **Add RSS Read** → configure one authorized feed URL you are allowed to use (example: a public security/news RSS). **Execute step**. Note item count on the connector.

3. **Add Limit** between RSS and notify → set `maxItems` to `5`. Execute. Confirm `5 items` leave the node.

4. **Create a Discord webhook credential** (Server Settings → Integrations → Webhooks → copy URL into n8n credential). Never commit the URL.

5. **Add Discord → Send a Message** (or webhook send). Build the text with dragged fields (title, link, date). Execute once. Expect **one Discord message per item**.

6. **Fix the “header repeated N times” lesson:** either keep per-item messages, or add an **Aggregate / Summarize** style step later. For this class, document why 5 messages appeared.

7. **Optional branch — Execute Command** on the n8n host (only if your install allows it; many hardened setups disable host exec). Safer alternative: skip host exec and use **SSH** to a **dedicated test VM**. If you do run a host command for learning, use a harmless read-only check:

```text
ping -c 3 1.1.1.1
```

Pin outputs. Do not chain this into production destructive actions.

8. **Save** as `01-rss-digest`. Toggle **Active** only after a successful manual run.

### Path C — Keep Agent (observe → approve → fix on a toy site)

Build this on the **same Docker host** as a disposable demo site—not on critical Proxmox nodes until you trust your prompts.

1. **Create a toy website container** you are willing to stop/start:

:::linux
```bash
docker rm -f keep-demo-web 2>/dev/null || true
docker run -d --name keep-demo-web -p 8090:80 nginx:stable
docker exec keep-demo-web sh -c 'echo "<h1>Keep demo OK</h1>" > /usr/share/nginx/html/index.html'
curl -sI http://127.0.0.1:8090/ | head
curl -s http://127.0.0.1:8090/ | head
```
:::

2. **New workflow** `02-keep-agent`:
   - Trigger: Manual + Schedule (every 15 minutes while testing; slow it down later).
   - **Edit Fields**: `prompt` = `Check whether http://HOST:8090 is up. Report status only.` and a fixed `chatId` string for memory.
   - **AI Agent** with a small/fast model you control (local Ollama or a paid API you authorize).
   - Tools:
     - **HTTP Request tool** named `website_check` → GET the demo URL; description: “Fetch the demo site to see if it responds.”
     - **Call n8n Workflow** tool pointing at a sub-workflow that only runs **read-only** SSH/docker commands you whitelist in the prompt (start with `docker ps --filter name=keep-demo-web`).

3. **System message (write your own; example intent):**  
   You are a lab junior admin. You may inspect. You must set `needs_approval=true` before any start/stop/rm/kill. Never stop containers named `n8n` or `traefik`. Prefer explaining evidence from tool output.

4. **Require structured output** JSON shaped like:

```json
{
  "website_up": true,
  "needs_approval": false,
  "commands_requested": [],
  "message": "short status for humans"
}
```

5. **Branch with If/Switch:**
   - If `needs_approval` → Telegram/Discord **send-and-wait / approval** (or manual checkpoint) → feed approval back into the agent with the same `chatId`.
   - If `website_up` is false and no approval pending → notify only.
   - If true and healthy → **do not spam** (silent success).

6. **Break the demo on purpose:**

:::linux
```bash
docker stop keep-demo-web
curl -sI --max-time 3 http://127.0.0.1:8090/ || echo EXPECTED_DOWN
```
:::

   Run the agent manually. Confirm it reports down. Approve a **single** `docker start keep-demo-web` if you enabled fix mode. Prove the site returns.

7. **Failure drill:** ask the agent (in a disposable copy) to “fix everything.” Confirm your prompt/approval gates refuse stopping `n8n`. Record the refusal in the workbook.

8. **Deactivate** the schedule when you leave the lab so it does not page you overnight during learning.

### Path D — n8n orchestrates an AI CLI over SSH (optional stretch)

**Goal:** prove the thin bridge: n8n SSH → headless AI CLI → stdout back, then resume the same session. Pick **one** CLI you are licensed to use (Claude Code, Gemini CLI, or another headless-capable tool). Commands below use `claude` as a stand-in—swap the binary and flags to match **current** docs for your tool.

1. **Install the AI CLI on a Linux jump host** (VM from Class 1 is fine). Log in interactively and confirm:

:::linux
```bash
hostname
which claude || which gemini || echo "Install your chosen AI CLI first"
claude --version   # or: gemini --version
```
:::

2. **In n8n, new workflow** `03-ai-cli-bridge`. Add **Manual Trigger** → **SSH** (Execute Command).

3. **Create SSH credential** to the jump host (password or key). Prefer a **dedicated non-root user** with only the rights that CLI needs. **Test connection**.

4. **Smoke test the shell** — Command field:

```bash
hostname
```

Execute step. Confirm `stdout` shows the jump host name.

5. **Smoke test the AI CLI** — Command field (adjust binary):

```bash
claude --version
```

If this fails but interactive SSH works, fix PATH for non-interactive shells (common). Workbook the fix.

6. **First headless prompt** (read-only; no lab mutations):

```bash
claude -p "In one short paragraph, explain what a virtual machine is."
```

Execute. Confirm answer text lands in SSH node stdout. **Pin** that output.

7. **Add project context** — create a tiny folder the CLI can see:

:::linux
```bash
mkdir -p ~/keep-cli-context
printf '%s\n' '# Keep lab note' 'Class 14 AI CLI bridge test.' 'Do not change production systems.' > ~/keep-cli-context/README.md
```
:::

   SSH command:

```bash
cd ~/keep-cli-context && claude -p "Read README.md and quote its second line exactly."
```

   Prove the reply uses **local file** context, not generic chat memory alone.

8. **Session UUID + first turn.** Add a **Code** node before SSH (JavaScript) that outputs one field `sessionId` (UUID v4). Pin it. First SSH command (shape illustrative):

```bash
cd ~/keep-cli-context && claude -p "List the files in this directory in three bullets." --session-id "{{ $json.sessionId }}"
```

   Use n8n expressions to inject `sessionId` from the Code node (drag field into the command). Execute and pin.

9. **Resume the session.** Duplicate the SSH node. Change the prompt to something that only makes sense in context, e.g. `Which of those files should a beginner open first and why?` and add the resume flag for your CLI (often `-r` plus the **same** session id). Execute **without** re-running the first turn. Confirm it remembers.

10. **Optional chat loop (Slack/Discord/Telegram):**  
    Inbound message → reuse or create `sessionId` → SSH headless prompt → reply to chat → **If** user says they are not done → second SSH with resume → else end. Keep messages under your chat app’s size limits.

11. **Hard ban for this path:** do not enable unrestricted “dangerous” CLI modes against production UniFi/Proxmox until Path C approval patterns wrap the mutate step. Record in the workbook: jump host, CLI name/version, session test PASS/FAIL.

12. **Save** `03-ai-cli-bridge`. Leave **Inactive** unless you are watching it.

## Break/fix

1. Remove Limit → watch notify fan-out → restore Limit.

2. Point HTTP tool at a closed port → confirm agent reports down without inventing success.

3. Revoke Discord/Telegram credential → confirm node errors clearly → restore.

4. Disable approval node and attempt an auto-fix path → prove you refuse to run class gate without human-in-the-loop.

5. **AI CLI PATH break:** from n8n SSH run `claude --version` with a stripped `PATH=` (or wrong binary name) → read the error → restore a working login/PATH for that SSH user.

6. **Session break:** resume with a **wrong** session id → confirm the CLI does not invent prior context → retry with the correct id.

## Common mistakes

- Publishing n8n to `0.0.0.0` on a public VPS without Access/VPN.
- Using `localhost` inside a container when you meant another service name.
- Letting agents choose arbitrary shell commands on day one.
- Forgetting item cardinality (N items → N side effects).
- Storing webhook URLs in git.
- Pinning stale data and thinking production changed.
- Expecting interactive TTY Claude/Gemini behavior over n8n SSH (use headless/print mode).
- Putting AI CLI on root@everything instead of a scoped jump user.
- Resuming sessions without persisting the UUID across chat messages.

## Knowledge check

1. What is an n8n **item**, and why does item count matter for Discord nodes?
2. What is the difference between an LLM summarize node and an AI Agent with tools?
3. Why pin data during builds that call paid models?
4. What must be true before an agent may run `docker stop` / `docker rm` in this class?
5. Where should n8n’s UI be reachable from in a Keep-style lab?
6. How do you keep a healthy schedule from spamming chat every 15 minutes?
7. In the orchestrator pattern, what does n8n own vs what the AI CLI owns?
8. Why generate a session UUID before the first headless AI CLI call?
9. What should you test before `claude -p "..."` if SSH `hostname` works but the CLI fails?

## Practical gate

- [ ] n8n UI reachable on the lab network only; owner account created; data survives recreate.
- [ ] Workflow `01-rss-digest` runs manually: RSS → Limit(≤5) → notify with real titles/links.
- [ ] Student can explain why message count matched item count before Limit.
- [ ] Workflow `02-keep-agent` detects demo site down/up from tool evidence.
- [ ] At least one mutating action is gated by human approval (or class documents that fix-mode is disabled and why).
- [ ] No production ARR/HA admin credentials were pasted into chat nodes or course files.
- [ ] Schedule is off or slowed when the student is not actively testing.
- [ ] **Optional Path D:** `03-ai-cli-bridge` shows hostname + CLI version + one headless answer + one **resumed** follow-up with the same session id (or workbook documents “deferred” with reason).

## 2026 correction

n8n UI labels, AI node names, env vars, and AI CLI flags (`-p`, `--session-id`, resume switches) change across releases. Prefer current official n8n Docker docs and your chosen AI CLI reference for exact screens and flags. The durable skills are: item flow, credentials hygiene, least privilege, structured outputs, human approval before mutation, and treating n8n as orchestrator when a terminal AI tool owns deep context.
