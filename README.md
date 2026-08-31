# Summit Talk Demos — Using Tools and Agents in Generative AI Applications

Live demos for the breakout session on 2026-09-02, 11:30 AM (45 min).
All notebooks run against Amazon Bedrock in **us-west-2** with
`us.anthropic.claude-haiku-4-5` (fast + cheap — good live-demo latency).

## Narrative arc

| # | Demo | Message | ~Time |
|---|------|---------|-------|
| 1 | `01_function_calling/` | Function calling = structured JSON round-trip. The model *asks*, your code *executes*. | 5 min |
| 2 | `02_react_pattern/` | ReAct = function calling in a loop. Watch Thought → Action → Observation live. | 6 min |
| 3 | `03_strands/` | Frameworks own the loop. Strands: `@tool` + model + prompt = agent. | 5 min |
| 4 | `04_crewai/` | CrewAI: role-based multi-agent collaboration (analyst → writer handoff). | 6 min |
| 5 | `05_mcp/` | MCP: tools behind a protocol. Agent discovers tools it never imported. | 5 min |
| 6 | `06_a2a/` | A2A: agents behind a protocol. Discovery via Agent Card, delegation via tasks. | 7 min |
| — | (option) AgentCore | "And AWS runs it for you" — Runtime/Gateway, if time allows. | 5 min |

Running thread: the same question ("rain gear on the berlin-munich cycling
route?") solved at every abstraction level, so the audience compares
approaches, not problems.

## Setup

```bash
cd ~/environment/summit-talk-demos
python3.11 -m venv .venv
.venv/bin/pip install boto3 "strands-agents[a2a]>=1.53.0" crewai jupyter jupytext rich mcp httpx
# AWS credentials with bedrock:InvokeModel in us-west-2 required
```

## Running live

```bash
.venv/bin/jupyter lab        # open the demo.ipynb in each folder, run cell-by-cell
```

**Demo 6 needs the remote agent running first** (separate terminal):

```bash
cd 06_a2a && ../.venv/bin/python weather_agent_server.py
# wait for "Uvicorn running on http://127.0.0.1:9000"
```

Nice live moment: `curl http://127.0.0.1:9000/.well-known/agent-card.json | jq`
before running the notebook.

## Backup

Every `demo.ipynb` is committed **with verified saved outputs** — if the demo
gods are angry, scroll through the executed notebook instead of re-running.
Source of truth is `demo.py` (jupytext percent format); regenerate notebooks with:

```bash
.venv/bin/jupytext --to ipynb NN_folder/demo.py -o NN_folder/demo.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --inplace NN_folder/demo.ipynb
```

## Pitfalls learned while building (keep in mind live)

- **Bedrock Converse:** `toolResult` `json` content must be an *object* —
  wrap lists/scalars as `{"result": ...}` (Demo 2 does this).
- **Strands + MCP:** run the agent *inside* the `with mcp_client:` block and
  pass the tool **list**, never the client itself.
- **CrewAI:** uses LiteLLM — Bedrock model id is `bedrock/us.anthropic...`;
  `OTEL_SDK_DISABLED=true` keeps telemetry noise out of the output.
- **A2A:** `strands-agents[a2a]` extra required; Agent Card lives at
  `/.well-known/agent-card.json`; `message/send` returns artifacts + full
  streaming history.
