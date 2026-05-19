# DevOps Pipeline Failure Agent
### Cloud Advocate YouTube Demo

An agentic AI that reads a failed CI build log, inspects the source code, diagnoses the root cause, and posts a fix recommendation to Slack — autonomously.

---

## Setup (WSL2 / Linux)

```bash
# 1. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## Run the demo

```bash
# Uses the included sample failed build log
python agent.py

# Or point it at your own log
python agent.py --log /path/to/your/build.log
```

---

## What the agent does

```
Perceive  →  read_build_log        reads the CI failure output
Plan      →  Claude reasons         identifies the failing test + file
Act       →  read_source_file       inspects the actual source code
Observe   →  Claude re-reasons      diagnoses root cause precisely
Report    →  post_slack_summary     posts fix recommendation
```

Three tools. One loop. No hard-coded logic.

---

## Project structure

```
devops-agent/
├── agent.py                   # main agent (the demo)
├── requirements.txt
├── samples/
│   ├── failed_build.log       # sample CI failure log
│   └── gateway.py             # the buggy source file the agent inspects
└── README.md
```

---

## Extending this

- **Real GitHub trigger**: set up a webhook that writes the Actions log to a file and calls `python agent.py --log /tmp/build.log`
- **Real Slack**: replace `post_slack_summary` with an actual `requests.post` to your Slack webhook URL
- **More tools**: add `create_github_pr`, `query_datadog_metrics`, `run_terraform_plan`

---

## For the YouTube video

This demo intentionally uses a sample log so it's reproducible on any machine without GitHub Actions setup. During filming, run it fresh — the agent's reasoning is non-deterministic and produces a natural, unscripted walkthrough every time.
