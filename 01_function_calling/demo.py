# %% [markdown]
# # Demo 1 — Raw Function Calling with Amazon Bedrock
#
# No frameworks. Just the Bedrock **Converse API** and ~50 lines of Python.
#
# The flow:
# 1. We tell the model which **tools** exist (name + JSON schema)
# 2. The model decides it needs a tool and returns a `toolUse` block
# 3. **We** execute the function and send the result back
# 4. The model writes the final answer
#
# > The model never runs code. It only *asks*. Your code stays in control.

# %%
import json
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-west-2")
MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# %% [markdown]
# ## Step 1 — Define a tool
#
# A tool is just a function... plus a JSON schema description the model can read.

# %%
def get_weather(city: str) -> dict:
    """Our 'real' function. (Canned data so the demo needs no API key.)"""
    fake_db = {
        "berlin": {"temp_c": 22, "condition": "sunny"},
        "munich": {"temp_c": 18, "condition": "rain"},
        "seattle": {"temp_c": 15, "condition": "drizzle"},
    }
    return fake_db.get(city.lower(), {"temp_c": 20, "condition": "unknown"})


tool_config = {
    "tools": [
        {
            "toolSpec": {
                "name": "get_weather",
                "description": "Get current weather for a city",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string", "description": "City name"}
                        },
                        "required": ["city"],
                    }
                },
            }
        }
    ]
}

# %% [markdown]
# ## Step 2 — Ask a question the model can't answer alone

# %%
messages = [
    {"role": "user", "content": [{"text": "Should I take a rain jacket in Munich today?"}]}
]

response = bedrock.converse(modelId=MODEL_ID, messages=messages, toolConfig=tool_config)
output_message = response["output"]["message"]

print("stopReason:", response["stopReason"])
for block in output_message["content"]:
    print(json.dumps(block, indent=2))

# %% [markdown]
# The model returned `toolUse` — it wants us to call `get_weather`.
#
# ## Step 3 — Execute the tool and send the result back

# %%
messages.append(output_message)  # keep the model's turn in history

# find the toolUse block (content may also contain text/reasoning blocks)
tool_use = next(b["toolUse"] for b in output_message["content"] if "toolUse" in b)
print("Model requested:", tool_use["name"], tool_use["input"])

result = get_weather(**tool_use["input"])
print("Local execution result:", result)

messages.append(
    {
        "role": "user",
        "content": [
            {
                "toolResult": {
                    "toolUseId": tool_use["toolUseId"],
                    "content": [{"json": result}],
                }
            }
        ],
    }
)

# %% [markdown]
# ## Step 4 — The model writes the final answer

# %%
response = bedrock.converse(modelId=MODEL_ID, messages=messages, toolConfig=tool_config)

for block in response["output"]["message"]["content"]:
    if "text" in block:
        print(block["text"])

# %% [markdown]
# ## Takeaways
#
# - Function calling = **structured JSON in, structured JSON out**
# - The model *requests*, your code *executes* — clean security boundary
# - This 4-step dance is the atom every agent framework is built from.
#   Next demo: what happens when we put it in a **loop**...
