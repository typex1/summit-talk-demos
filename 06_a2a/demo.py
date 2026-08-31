# %% [markdown]
# # Demo 6 — A2A: Agents Talking to Agents
#
# MCP standardizes **agent → tool**. **A2A (Agent2Agent)** standardizes
# **agent → agent**: independent agents — different frameworks, different
# owners, different machines — discover and delegate to each other over HTTP.
#
# Running in another terminal: `weather_agent_server.py` — a **Strands**
# agent wrapped in `A2AServer`, listening on port 9000. It could just as
# well be CrewAI, LangGraph, or a vendor's black box: the protocol is the contract.
#
# Two core A2A concepts:
# 1. **Agent Card** — a JSON self-description at `/.well-known/agent-card.json`
# 2. **Tasks** — JSON-RPC `message/send` to give the remote agent work

# %%
import json
import httpx

REMOTE = "http://127.0.0.1:9000"

# %% [markdown]
# ## Step 1 — Discovery: fetch the Agent Card

# %%
card = httpx.get(f"{REMOTE}/.well-known/agent-card.json").json()
print(json.dumps(card, indent=2))

# %% [markdown]
# The card advertises the agent's **skills**, transport, and endpoint —
# everything a client agent needs to decide *whether* and *how* to delegate.
#
# ## Step 2 — A local planner agent that delegates over A2A
#
# We give our local agent one tool: `ask_weather_specialist`. Inside, it's
# a JSON-RPC call to the remote agent. The local agent never sees the
# remote agent's tools, model, or framework.

# %%
from strands import Agent, tool
from strands.models import BedrockModel


@tool
def ask_weather_specialist(question: str) -> str:
    """Delegate a weather question to the remote Weather Specialist agent (via A2A).

    Args:
        question: A natural-language weather question.
    """
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "message/send",
        "params": {
            "message": {
                "kind": "message",
                "role": "user",
                "messageId": "m1",
                "parts": [{"kind": "text", "text": question}],
            }
        },
    }
    resp = httpx.post(REMOTE, json=payload, timeout=60).json()
    artifacts = resp["result"]["artifacts"]
    return " ".join(p["text"] for a in artifacts for p in a["parts"] if "text" in p)


planner = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                       region_name="us-west-2"),
    system_prompt=(
        "You are a cycling trip planner. You don't know weather yourself — "
        "delegate weather questions to the specialist. The berlin-munich "
        "route passes Berlin, Leipzig, Nuremberg, Munich."
    ),
    tools=[ask_weather_specialist],
)

# %% [markdown]
# ## Step 3 — Watch the delegation

# %%
result = planner(
    "Which cities on the berlin-munich route need rain gear today? "
    "Check each city with the specialist."
)

# %% [markdown]
# ## Takeaways
#
# - **Discovery** (Agent Card) + **delegation** (tasks) = the whole idea
# - The planner and the specialist are separate processes; swap the
#   specialist for any A2A-compliant agent and nothing here changes
# - MCP: agent→tool. A2A: agent→agent. Together they make agents *composable*
# - And when you want AWS to host, scale, and secure these agents:
#   **Amazon Bedrock AgentCore** (Runtime, Gateway, Identity, Memory)
