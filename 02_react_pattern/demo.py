# %% [markdown]
# # Demo 2 — The ReAct Pattern: Reason + Act in a Loop
#
# Demo 1 was one round-trip. Real problems need **several** tool calls,
# where each step depends on the last result.
#
# **ReAct** = the model alternates:
# - **Thought** — reason about what to do next
# - **Action** — call a tool
# - **Observation** — read the result
#
# ...until it can answer. We implement the whole loop in ~40 lines,
# and print every step so you can watch the agent "think".

# %%
import json
import boto3
from rich.console import Console
from rich.panel import Panel

console = Console()
bedrock = boto3.client("bedrock-runtime", region_name="us-west-2")
MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# %% [markdown]
# ## Tools: a tiny travel toolbox
#
# The question we'll ask needs *chained* lookups — the model must find
# cities first, then check each one's weather. One tool call can't do it.

# %%
def list_cities_on_route(route: str) -> list:
    routes = {
        "berlin-munich": ["Berlin", "Leipzig", "Nuremberg", "Munich"],
    }
    return routes.get(route.lower(), [])


def get_weather(city: str) -> dict:
    fake_db = {
        "berlin": {"temp_c": 22, "condition": "sunny"},
        "leipzig": {"temp_c": 21, "condition": "cloudy"},
        "nuremberg": {"temp_c": 17, "condition": "rain"},
        "munich": {"temp_c": 18, "condition": "rain"},
    }
    return fake_db.get(city.lower(), {"temp_c": 20, "condition": "unknown"})


TOOL_FUNCTIONS = {"list_cities_on_route": list_cities_on_route, "get_weather": get_weather}

tool_config = {
    "tools": [
        {
            "toolSpec": {
                "name": "list_cities_on_route",
                "description": "List the major cities along a cycling route, in order",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {"route": {"type": "string", "description": "e.g. 'berlin-munich'"}},
                        "required": ["route"],
                    }
                },
            }
        },
        {
            "toolSpec": {
                "name": "get_weather",
                "description": "Get current weather for a city",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {"city": {"type": "string"}},
                        "required": ["city"],
                    }
                },
            }
        },
    ]
}

# %% [markdown]
# ## The ReAct loop
#
# This is the entire "agent runtime". Every framework you'll see today
# ships a fancier version of this `while` loop.

# %%
def run_agent(user_question: str, max_turns: int = 10) -> str:
    messages = [{"role": "user", "content": [{"text": user_question}]}]

    for turn in range(1, max_turns + 1):
        response = bedrock.converse(
            modelId=MODEL_ID,
            messages=messages,
            toolConfig=tool_config,
            system=[{"text": "Think step by step. Briefly state your reasoning before each tool call."}],
        )
        msg = response["output"]["message"]
        messages.append(msg)

        # Show the model's THOUGHT (any text blocks)
        for block in msg["content"]:
            if "text" in block and block["text"].strip():
                console.print(Panel(block["text"], title=f"Thought (turn {turn})", border_style="cyan"))

        if response["stopReason"] != "tool_use":
            return next(b["text"] for b in msg["content"] if "text" in b)

        # Execute every requested ACTION, collect OBSERVATIONS
        tool_results = []
        for block in msg["content"]:
            if "toolUse" not in block:
                continue
            tu = block["toolUse"]
            console.print(Panel(f"{tu['name']}({json.dumps(tu['input'])})",
                                title=f"Action (turn {turn})", border_style="yellow"))
            result = TOOL_FUNCTIONS[tu["name"]](**tu["input"])
            console.print(Panel(json.dumps(result), title=f"Observation (turn {turn})", border_style="green"))
            # Bedrock quirk: toolResult json content must be an OBJECT, not a list
            payload = result if isinstance(result, dict) else {"result": result}
            tool_results.append(
                {"toolResult": {"toolUseId": tu["toolUseId"], "content": [{"json": payload}]}}
            )
        messages.append({"role": "user", "content": tool_results})

    return "(max turns reached)"

# %% [markdown]
# ## Watch it think

# %%
answer = run_agent(
    "I'm cycling the berlin-munich route. Which cities on the route "
    "will I need rain gear in, based on current weather?"
)
console.print(Panel(answer, title="Final Answer", border_style="bold magenta"))

# %% [markdown]
# ## Takeaways
#
# - ReAct = function calling **in a loop** with visible reasoning
# - The model chained tools on its own: route → cities → weather per city
# - ~40 lines of orchestration... which we wrote by hand.
#   Frameworks like **Strands** and **CrewAI** give you this loop,
#   plus retries, tracing, memory, and MCP — that's the next demo.
