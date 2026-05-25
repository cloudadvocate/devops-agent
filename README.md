# 🤖 DevOps Pipeline Failure Agent

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![Anthropic](https://img.shields.io/badge/Claude-API-purple?style=flat-square)
![Ollama](https://img.shields.io/badge/Ollama-Local-green?style=flat-square)
![Qwen3](https://img.shields.io/badge/Qwen3-14b-teal?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20WSL2-lightgrey?style=flat-square)
![YouTube](https://img.shields.io/badge/Cloud%20Advocate-YouTube-red?style=flat-square&logo=youtube)

> An agentic AI that automatically reads a failed CI build log, inspects the source code, diagnoses the root cause, and posts a fix recommendation to Slack — all autonomously.
>
> Two versions: **Claude API** (cloud) and **Qwen3 via Ollama** (100% local, zero cost).

---

## 📺 Video Series

| Video | Title | Link |
|---|---|---|
| Part 1 | Agentic AI in DevOps — The Skill Every Cloud Engineer Needs in 2026 | [Watch](https://youtube.com/@CloudAdvocate) |
| Part 2 | Local LLM vs Cloud API for DevOps Agents — Which Should You Use in 2026? | [Watch](https://youtube.com/@CloudAdvocate) |
| Part 3 | Wire Your AI Agent to Real GitHub Actions (coming soon) | 🔜 |

*Cloud Advocate · GK*

---

## 🧠 How It Works

Traditional DevOps automation executes what you tell it to execute.
**Agentic AI reasons, decides, and acts on its own.**

```
Pipeline fails
     ↓
Agent reads the build log              ← Perceive
     ↓
LLM identifies the failing             ← Plan
test and decides which file to inspect
     ↓
Agent reads the source code            ← Act
     ↓
LLM diagnoses root cause              ← Observe
     ↓
Fix recommendation posted to Slack     ← Report
     ↓
Loop repeats until job is done         ← ↻ Agentic loop
```

**The key insight:** The LLM is the manager. The tools are the workers.
The manager never does the work itself — it delegates to the right worker at the right time.

---

## ⚡ Two Agents — Choose Your Setup

| | `agent.py` | `agent_local.py` |
|---|---|---|
| Model | Claude Sonnet (Anthropic) | Qwen3:14b (Ollama) |
| Cost | ~$0.01 per run | $0.00 forever |
| Privacy | Cloud API | 100% local |
| Internet | Required | Not required |
| Setup | API key only | Ollama + GPU |
| Diagnosis | ✅ Correct | ✅ Correct |
| Enterprise safe | Check policy | Always safe |

---

## 🔵 Option 1 — Claude API (agent.py)

### Prerequisites
- Python 3.12+
- WSL2 / Linux / macOS
- Anthropic API key → [console.anthropic.com](https://console.anthropic.com)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/cloudadvocate/devops-agent.git
cd devops-agent

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Run

```bash
python agent.py

# Or use your own CI log
python agent.py --log /path/to/build.log
```

---

## 🟢 Option 2 — Local Qwen3 via Ollama (agent_local.py)

Zero API cost. Zero data leaves your machine.

### Prerequisites
- Python 3.12+
- WSL2 / Linux / macOS
- [Ollama](https://ollama.com) installed on your machine
- GPU recommended (see hardware table below)

### Hardware recommendations

| VRAM | Recommended model | Pull command |
|---|---|---|
| CPU only | qwen3:8b (slow) | `ollama pull qwen3:8b` |
| 8GB | qwen3:8b | `ollama pull qwen3:8b` |
| 12GB | qwen3:14b ← sweet spot | `ollama pull qwen3:14b` |
| 16GB | qwen3:30b-a3b | `ollama pull qwen3:30b-a3b` |
| 24GB | qwen3:32b | `ollama pull qwen3:32b` |

### Setup

```bash
# 1. Install Ollama → https://ollama.com
# 2. Pull the model
ollama pull qwen3:14b

# 3. Start Ollama server (keep this running)
ollama serve

# 4. Clone the repo and set up venv
git clone https://github.com/cloudadvocate/devops-agent.git
cd devops-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### WSL2 users — set Ollama host

Ollama runs on Windows. WSL2 needs to point to it:

```bash
# Find your Windows host IP
ip route | grep default | awk '{print $3}'

# Set the host (replace with your IP)
export OLLAMA_HOST=http://172.24.48.1:11434

# Verify connection
curl http://172.24.48.1:11434/api/tags
```

### Run

```bash
export OLLAMA_HOST=http://YOUR_WINDOWS_IP:11434
python agent_local.py
```

---

## 🎬 Demo Output

### Claude API version

```
════════════════════════════════════════════════════════════
   🤖  DevOps Pipeline Failure Agent
════════════════════════════════════════════════════════════
   Model: claude-sonnet-4-20250514
   Log:   samples/failed_build.log

⟳  Agent thinking... (step 1)
🔧  Calling tool: read_build_log
⟳  Agent thinking... (step 2)
🔧  Calling tool: read_source_file  (file_path='gateway.py')
⟳  Agent thinking... (step 3)
🔧  Calling tool: post_slack_summary

────────────────────────────────────────────────────────────
  📬  Slack #devops-alerts
────────────────────────────────────────────────────────────
  🔴  Build Failure Diagnosed
  Root cause:  Timeout threshold (5s) too low for Stripe API
  Affected file:  gateway.py · Severity: HIGH
  Fix:  Increase DEFAULT_TIMEOUT to 15s
  _Diagnosed by Cloud Advocate DevOps Agent · 14:23:01_
────────────────────────────────────────────────────────────
  Tokens used — input: 2,847  output: 312
════════════════════════════════════════════════════════════
```

### Local Qwen3 version

```
════════════════════════════════════════════════════════════
   🤖  DevOps Agent — Local Edition (Qwen3:14b)
════════════════════════════════════════════════════════════
   Model:  qwen3:14b via Ollama (100% local)
   Cost:   $0.00

⟳  Agent thinking... (step 1)
🔧  Calling tool: read_build_log
⟳  Agent thinking... (step 2)
🔧  Calling tool: read_source_file  (file_path='gateway.py')
⟳  Agent thinking... (step 3)
🔧  Calling tool: post_slack_summary

────────────────────────────────────────────────────────────
  📬  Slack #devops-alerts
────────────────────────────────────────────────────────────
  🔴  Build Failure Diagnosed
  Root cause:  PaymentGateway returns timeout instead of raising
  Affected file:  gateway.py · Severity: HIGH
  Fix:  raise PaymentGatewayTimeout() instead of returning result
  _Diagnosed by Cloud Advocate Local Agent (Qwen3:14b) · 08:40:34_
────────────────────────────────────────────────────────────
  Powered by: qwen3:14b running locally via Ollama
════════════════════════════════════════════════════════════
```

---

## 📁 Project Structure

```
devops-agent/
├── agent.py                   # Cloud agent — Claude API
├── agent_local.py             # Local agent — Qwen3 via Ollama
├── requirements.txt           # Dependencies
├── samples/
│   ├── failed_build.log       # Sample GitHub Actions failure log
│   └── gateway.py             # Buggy source file the agent inspects
└── .github/
    └── workflows/
        └── ci.yml             # Real GitHub Actions trigger (coming soon)
```

---

## 🛠️ The Three Tools

The agent has exactly three tools — think of them as workers it can delegate to:

| Tool | What it does |
|---|---|
| `read_build_log` | Reads the CI failure output — stack traces, error messages, test results |
| `read_source_file` | Reads any source file from the repo to inspect the buggy code |
| `post_slack_summary` | Posts the diagnosis and fix recommendation to Slack |

The LLM (the manager) decides **which** tool to call, **when**, and **in what order**.
You never hardcode that logic — the model reasons its way to it.

---

## 🔍 The Agentic Loop

### Claude API version (agent.py)

```python
while True:
    response = client.messages.create(
        model=MODEL, tools=TOOLS, messages=messages
    )
    if response.stop_reason == "end_turn":
        break
    for block in response.content:
        if block.type == "tool_use":
            result = execute_tool(block.name, block.input)
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": [tool_result]})
```

### Local Ollama version (agent_local.py)

```python
while step < MAX_STEPS:
    response = ollama.chat(
        model=MODEL, messages=messages,
        tools=TOOLS, think=False, options={"temperature": 0.1}
    )
    if not response.message.tool_calls:
        break
    for tool_call in response.message.tool_calls:
        result = execute_tool(tool_call.function.name, tool_call.function.arguments)
        messages.append({"role": "tool", "content": result})
```

**Key difference:** Ollama uses OpenAI-compatible tool format. Claude uses Anthropic format.
The agentic loop logic is identical — only the API client changes.

---

## 🚀 Extending This Agent

### Add a real Slack webhook

```python
import requests

requests.post(
    os.environ["SLACK_WEBHOOK_URL"],
    json={"text": f"*{payload['root_cause']}*\nFile: `{payload['affected_file']}`\n```{payload['code_suggestion']}```"}
)
```

### Add more tools

```python
{"name": "create_github_pr",      "description": "Create a PR with the fix"}
{"name": "query_datadog_metrics",  "description": "Fetch metrics around failure time"}
{"name": "run_terraform_plan",     "description": "Run terraform plan and return diff"}
```

### Wire to GitHub Actions

```yaml
- name: Run AI Diagnosis Agent
  if: failure()
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
  run: |
    pip install -r requirements.txt
    python agent.py --log $GITHUB_STEP_SUMMARY
```

---

## 🔒 Production Guardrails

| Guardrail | Why |
|---|---|
| Dry-run mode | Agent shows what it would do before acting |
| Approval gate | Human approves fix in Slack before PR is raised |
| Scope limits | Agent cannot touch production without explicit flag |
| Audit logging | Every tool call logged with timestamp and reasoning |
| Secret scanning | Never pass API keys through agent context |

---

## 📦 Requirements

```
anthropic>=0.40.0
ollama>=0.4.0
requests>=2.31.0
```

| Version | Cost per run |
|---|---|
| Claude API | ~$0.01–0.02 |
| Qwen3 local | $0.00 |

---

## 🗺️ Roadmap

- [x] Claude API agent (Part 1)
- [x] Local Qwen3 agent via Ollama (Part 2)
- [ ] Real Slack webhook integration
- [ ] GitHub Actions automatic trigger on build failure
- [ ] Self-hosted runner setup guide
- [ ] GitHub PR creation tool
- [ ] Multi-agent pattern — planner + executor + reviewer
- [ ] Datadog / CloudWatch metrics correlation

---

## 👨‍💻 About

Built by **GK** — Cloud Architect and DevSecOps practitioner with 10+ years of enterprise networking and telecom experience.

**Cloud Advocate** is a YouTube channel covering AI on Cloud, DevSecOps, Multi-cloud, FinOps, and Cloud Career guidance with real-world hands-on depth.

📺 [YouTube — Cloud Advocate](https://youtube.com/@CloudAdvocate)
💼 [LinkedIn](https://www.linkedin.com/in/chaitanya-gk/)

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*If this helped you, give the repo a ⭐ and subscribe to [Cloud Advocate](https://youtube.com/@CloudAdvocate) for more hands-on cloud and DevOps content.*
