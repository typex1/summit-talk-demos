"""A2A server: a Strands weather-specialist agent exposed over the A2A protocol.

Run:  python weather_agent_server.py   (serves on http://127.0.0.1:9000)
Any A2A client can now discover it via its Agent Card and send it tasks.
"""
from strands import Agent, tool
from strands.models import BedrockModel
from strands.multiagent.a2a import A2AServer


@tool
def get_weather(city: str) -> dict:
    """Get current weather for a city."""
    fake_db = {
        "berlin": {"temp_c": 22, "condition": "sunny"},
        "leipzig": {"temp_c": 21, "condition": "cloudy"},
        "nuremberg": {"temp_c": 17, "condition": "rain"},
        "munich": {"temp_c": 18, "condition": "rain"},
    }
    return fake_db.get(city.lower(), {"temp_c": 20, "condition": "unknown"})


weather_agent = Agent(
    name="Weather Specialist",
    description="Answers weather questions for cities on cycling routes.",
    model=BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                       region_name="us-west-2"),
    system_prompt="You are a weather specialist. Answer concisely.",
    tools=[get_weather],
    callback_handler=None,
)

server = A2AServer(agent=weather_agent, host="127.0.0.1", port=9000)

if __name__ == "__main__":
    server.serve()
