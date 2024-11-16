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


class GarbageSuggestion:
    def garbage_suggestion_tool(self, tablePath: str):
        """
        Goes through the summaries of all files and determines which may be fit for deletion.

        Args:
            tablePath (str): The path to the JSON data table
        """
        path = ""

        summaries = []
        files = []

        def get_all_summaries(dic, path):

            for key, value in dic.items():
                if key == "summary":
                    yield (value, path)
                elif isinstance(value, dict):
                    path = key
                    yield from get_all_summaries(value, path)

        with open(tableName, "r") as f:
            dic = json.load(f)

            for x in get_all_summaries(dic, path):
                summaries.append(x[0])
                files.append(x[1])

        return (summaries, files)


garbage_tools = GarbageSuggestion()
garbage_tool = client.create_tool(GarbageSuggestion.garbage_suggestion_tool)

# Uncomment during first run/reset
agent_state = client.create_agent(agent_name)

agent_id = client.get_agent_id(agent_name)
agent_state = client.get_agent(agent_id)

# JSON table path
tableName = "combinedFileDataTable.json"

(summaries, files) = garbage_tools.garbage_suggestion_tool(tablePath=tableName)

# Number of deletion suggestions
num = 3

# Getting deletion suggestion
response = client.send_message(
    agent_id=agent_id,
    role="user",
    message=f"Please decide which {num} entries in the list {summaries} you would recommend deleting based on the content of their summaries. Do not tell me. Use the indices from that list and tell me the corresponding file names from the list {files} that I should delete. Only give me {num} files.",
)

print(f"File Summary:\n{response.messages}")
