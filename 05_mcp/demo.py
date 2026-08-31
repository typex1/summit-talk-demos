# %% [markdown]
# # Demo 5 — MCP: Tools as a Protocol, Not a Function Call
#
# So far every tool lived **inside** the agent's process.
# **Model Context Protocol (MCP)** moves tools behind a standard interface:
#
# - A tool server can be written once and used by *any* MCP client
#   (Strands, Claude Desktop, Cursor, your IDE...)
# - Transports: **stdio** (local subprocess) or **streamable HTTP** (remote)
#
# `weather_server.py` in this folder is a ~30-line MCP server exposing the
# same weather toolbox. The agent below has **no tool code at all** —
# it discovers the tools over the protocol.

# %%
import sys
from pathlib import Path

from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

SERVER = str((Path(__file__).parent if "__file__" in globals()
              else Path.cwd()) / "weather_server.py")
print(open(SERVER).read()[:800])  # show the audience the server code

# %% [markdown]
# ## Connect to the MCP server (it launches as a subprocess)

# %%
weather_mcp = MCPClient(lambda: stdio_client(
    StdioServerParameters(command=sys.executable, args=[SERVER])
))

model = BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                     region_name="us-west-2")

# %% [markdown]
# ## Discover tools over the protocol, then run the agent
#
# Note: the MCP connection is a context manager — connection lifetime
# = tool lifetime, so the agent runs *inside* the `with` block.

# %%
with weather_mcp:
    tools = weather_mcp.list_tools_sync()
    print("Tools discovered via MCP:", [t.tool_name for t in tools])

    agent = Agent(
        model=model,
        system_prompt="You are a cycling trip assistant. Be concise.",
        tools=tools,
    )
    result = agent(
        "I'm cycling the berlin-munich route. Which cities on the route "
        "will I need rain gear in, based on current weather?"
    )

# %% [markdown]
# ## Takeaways
#
# - The agent gained tools **without importing any tool code** — pure protocol
# - Same server would plug into Claude Desktop, Cursor, or a CrewAI agent
# - stdio for local, streamable HTTP for remote (e.g. the managed
#   **AWS Knowledge MCP server**: `https://knowledge-mcp.global.api.aws`)
# - MCP standardizes **agent → tool**. What about **agent → agent**?
#   That's **A2A** →
