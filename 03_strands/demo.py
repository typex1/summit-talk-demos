# %% [markdown]
# # Demo 3 — Strands Agents: The Framework Does the Loop
#
# Demo 2's ReAct loop was ~40 lines of hand-written orchestration.
# **Strands Agents** (AWS open source) reduces it to: *model + tools + prompt*.
#
# - `@tool` decorator turns any Python function into a tool
#   (schema auto-generated from the signature + docstring)
# - The agent loop, retries, streaming, and tracing come for free

# %%
from strands import Agent, tool
from strands.models import BedrockModel

# %% [markdown]
# ## Same travel toolbox as Demo 2 — but now just decorated functions

# %%
@tool
def list_cities_on_route(route: str) -> dict:
    """List the major cities along a cycling route, in order.

    Args:
        route: Route name, e.g. 'berlin-munich'
    """
    routes = {"berlin-munich": ["Berlin", "Leipzig", "Nuremberg", "Munich"]}
    return {"cities": routes.get(route.lower(), [])}


@tool
def get_weather(city: str) -> dict:
    """Get current weather for a city.

    Args:
        city: City name
    """
    fake_db = {
        "berlin": {"temp_c": 22, "condition": "sunny"},
        "leipzig": {"temp_c": 21, "condition": "cloudy"},
        "nuremberg": {"temp_c": 17, "condition": "rain"},
        "munich": {"temp_c": 18, "condition": "rain"},
    }
    return fake_db.get(city.lower(), {"temp_c": 20, "condition": "unknown"})

# %% [markdown]
# ## Assemble the agent — this is the whole thing

# %%
model = BedrockModel(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    region_name="us-west-2",
)

agent = Agent(
    model=model,
    system_prompt="You are a cycling trip assistant. Be concise.",
    tools=[list_cities_on_route, get_weather],
)

# %% [markdown]
# ## Run it — same question as Demo 2

# %%
result = agent(
    "I'm cycling the berlin-munich route. Which cities on the route "
    "will I need rain gear in, based on current weather?"
)

# %% [markdown]
# ## Inspect what happened: the tool-call trace

# %%
for msg in agent.messages:
    for block in msg["content"]:
        if "toolUse" in block:
            tu = block["toolUse"]
            print(f"→ {tu['name']}({tu['input']})")

# %% [markdown]
# ## Takeaways
#
# - The hand-written loop from Demo 2 became **zero lines** — Strands owns it
# - Tools are plain Python functions; the docstring *is* the API contract
# - Full message history stays inspectable (`agent.messages`) — no black box
# - Next: a different philosophy — **CrewAI**, where multiple specialized
#   agents collaborate on a task
