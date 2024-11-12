from letta import create_client
from letta import EmbeddingConfig, LLMConfig

import json


client = create_client()

client.set_default_embedding_config(
    EmbeddingConfig.default_config(model_name="letta")
)
client.set_default_llm_config(LLMConfig.default_config(model_name="letta"))

# Comment out during initial run
# Uncomment to reset
client.delete_agent(client.get_agent_id("garbage_agent"))

agent_name = "garbage_agent"

# Uncomment during first run/reset
agent_state = client.create_agent(agent_name)

agent_id = client.get_agent_id(agent_name)
agent_state = client.get_agent(agent_id)

filename = "combinedFileDataTable.json"


def get_all_summaries(dic):
    for key, value in dic.items():
        if key == "summary":
            yield value
        elif isinstance(value, dict):
            yield from get_all_summaries(value)


summaries = []

with open(filename, "r") as f:
    dic = json.load(f)

    for x in get_all_summaries(dic):
        summaries.append(x)


# Getting deletion suggestion
# Edit for number of deletion suggestions
response = client.send_message(
    agent_id=agent_id,
    role="user",
    message=f"Please tell me which three entries in the list {summaries} you would recommend deleting.",
)

print(f"File Summary:\n{response.messages}")
