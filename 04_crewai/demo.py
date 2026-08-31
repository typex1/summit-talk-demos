# %% [markdown]
# # Demo 4 — CrewAI: Multiple Specialized Agents Collaborate
#
# Strands (Demo 3) = **one** agent with tools.
# **CrewAI** = a *crew* of role-based agents that hand work to each other.
#
# Here: a two-agent content pipeline on Bedrock —
# a **Route Analyst** researches (with a tool), then a **Travel Writer**
# turns the analysis into a rider briefing. Sequential handoff.

# %%
import os
os.environ["OTEL_SDK_DISABLED"] = "true"  # keep demo output clean
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["CREWAI_TRACING_ENABLED"] = "false"  # prevent interactive tracing prompt on a TTY

from crewai import Agent, Crew, Process, Task, LLM
from crewai.tools import tool

llm = LLM(model="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
          temperature=0.3)

# %% [markdown]
# ## A tool for the analyst agent

# %%
@tool("get_weather")
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    fake_db = {
        "berlin": {"temp_c": 22, "condition": "sunny"},
        "leipzig": {"temp_c": 21, "condition": "cloudy"},
        "nuremberg": {"temp_c": 17, "condition": "rain"},
        "munich": {"temp_c": 18, "condition": "rain"},
    }
    return str(fake_db.get(city.lower(), {"temp_c": 20, "condition": "unknown"}))

# %% [markdown]
# ## Define the crew: two agents, two tasks

# %%
analyst = Agent(
    role="Cycling Route Analyst",
    goal="Assess weather conditions along cycling routes",
    backstory="A meticulous route planner for long-distance cyclists.",
    tools=[get_weather],
    llm=llm,
    verbose=True,
)

writer = Agent(
    role="Travel Writer",
    goal="Write short, vivid rider briefings",
    backstory="A cycling journalist who values brevity.",
    llm=llm,
    verbose=True,
)

analyze = Task(
    description=(
        "Check current weather in Berlin, Leipzig, Nuremberg and Munich "
        "(the berlin-munich cycling route). Identify where rain gear is needed."
    ),
    expected_output="A bullet list of cities with conditions and a rain-gear verdict.",
    agent=analyst,
)

brief = Task(
    description="Turn the analysis into a 3-sentence rider briefing.",
    expected_output="A 3-sentence briefing a cyclist reads before departure.",
    agent=writer,
    context=[analyze],
)

crew = Crew(agents=[analyst, writer], tasks=[analyze, brief],
            process=Process.sequential, verbose=True)

# %% [markdown]
# ## Run the crew

# %%
result = crew.kickoff()

# %%
print(result)

# %% [markdown]
# ## Takeaways
#
# - CrewAI thinks in **roles, goals, tasks** — orchestration by declaration
# - `context=[analyze]` wires task outputs together: agent-to-agent handoff
#   *inside one process*
# - Strands vs CrewAI isn't either/or: single capable agent vs. a
#   division-of-labor pipeline
# - Next question: what if the tools live *outside* your process?
#   That's **MCP** →
