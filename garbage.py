from letta import create_client
from letta import EmbeddingConfig, LLMConfig


def garbage_suggestion_tool(self):
    """
    Goes through the summaries of all files and determines which may be fit for deletion.
    If prompted to recommend files to delete or which files may be garbage, call this function.

    Args:
        tablePath (str): The path to the JSON data table
    """
    import json
    from letta import create_client, EmbeddingConfig, LLMConfig

    background_client = create_client()

    background_client.set_default_embedding_config(
        EmbeddingConfig.default_config(model_name="letta")
    )
    background_client.set_default_llm_config(
        LLMConfig.default_config(model_name="letta")
    )

    # JSON table path
    tableName = "dataTable3.json"
    path = ""

    summaries = []
    files = []

    def get_all_summaries(dic, path):

        for key, value in dic.items():
            if key == "path":
                path = value
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

    if background_client.get_agent_id("background_agent"):
        background_client.delete_agent(
            background_client.get_agent_id("background_agent")
        )

    agentState = background_client.create_agent("background_agent")

    # Number of deletion suggestions
    num = 3

    message = f"Please decide which {num} entries in the list {summaries} you would recommend deleting based on the content of their summaries. Do not tell me. Use the indices from that list and tell me the corresponding file names from the list {files} that I should delete. Only give me {num} files."

    response = background_client.send_message(
        message=message, role="user", agent_id=agentState.id
    )

    response = response.messages[1].function_call.arguments

    return response


client = create_client()

client.set_default_embedding_config(
    EmbeddingConfig.default_config(model_name="letta")
)
client.set_default_llm_config(LLMConfig.default_config(model_name="letta"))

garbage_tool = client.create_tool(garbage_suggestion_tool)

agent_name = "garbage_agent"

try:
    agent_state = client.create_agent(agent_name)
except ValueError:
    agent_id = client.get_agent_id(agent_name)
    client.delete_agent(agent_id)
    agent_state = client.create_agent(agent_name, tools=[garbage_tool.name])
