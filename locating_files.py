from letta import create_client, EmbeddingConfig, LLMConfig, ChatMemory
import json

client = create_client()

client.set_default_embedding_config(
    EmbeddingConfig.default_config(model_name="letta")
)
client.set_default_llm_config(LLMConfig.default_config(model_name="letta"))

# Reset agent
# client.delete_agent(client.get_agent_id("querying"))

agent_name = "queryingg"

class FileSearch:
    def extract_summaries(self, tablePath: str):
        """
        Extracts file summaries and their paths from a JSON data table.

        Args:
            tablePath (str): The path to the JSON file containing summaries and paths.

        Returns:
            tuple: A tuple containing a list of summaries and a list of corresponding paths.
        """
        summaries = []
        paths = []

        def traverse_json(data, current_path=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    new_path = f"{current_path}/{key}" if current_path else key
                    if key == "path" and isinstance(value, str):
                        yield (None, value)
                    elif key == "summary" and isinstance(value, str):
                        yield (value, current_path)
                    elif isinstance(value, (dict, list)):
                        yield from traverse_json(value, new_path)
            elif isinstance(data, list):
                for item in data:
                    yield from traverse_json(item, current_path)

        with open(tablePath, "r") as f:
            data = json.load(f)
            for summary, path in traverse_json(data):
                if summary and path:
                    summaries.append(summary)
                    paths.append(path)

        return summaries, paths

file_search_tool = FileSearch()
file_tool = client.create_tool(FileSearch.extract_summaries)

# Create agent
# agent_state = client.create_agent(agent_name)
system_prompt = """
You are a helpful assistant that assists users in finding files based on their summaries.
When responding to queries, ONLY provide the file names and paths, NOT the summaries.
Return the file paths as bullet points, without any additional explanations.
Ensure that you ignore any past queries and only respond based on the most recent user request.
"""
agent_state = client.create_agent(name=agent_name,
    # memory with human/persona blocks
    memory=ChatMemory(
      human="Name: Sarah", 
      persona=system_prompt
    ))
agent_id = client.get_agent_id(agent_name)
agent_state = client.get_agent(agent_id)

# file table
table_name = "dataTable.json"
summaries, paths = file_search_tool.extract_summaries(tablePath=table_name)

# Insert each summary into the archival memory
for summary, path in zip(summaries, paths):
    print(f"Inserting summary for file '{path}' into archival memory...")
    
    # insert summary content
    passage = client.insert_archival_memory(agent_id, summary)
    
    # store file path
    passage[0].metadata_ = {"file_path": path}
    print(f"Inserted file with metadata: {passage[0].metadata_}")

# now allow user to provide description of the file they remember
user_query = "I'm looking for a document related to fruits."
num_files_to_return = 3

# client.update_agent(agent_id, memory={"persona": system_prompt})
# Construct the message with summaries included
summaries_text = "\n".join([f"Summary of {path}: {summary}" for summary, path in zip(summaries, paths)])

response = client.send_message(
    agent_id=agent_id,
    role="user",
    message=f"Search for files that best match the description: '{user_query}'. "
            f"Here are the summaries of all files stored in the archival memory:\n\n{summaries_text}\n\n"
            f"Return the top {num_files_to_return} files based on their summaries and relevance to the query. "
            f"Only provide the file names and paths, not the summaries. DO NOT SAY ANYTHING OTHER THAN LIST THE FILES THAT MATCH THE USER's file description. JUST GIVE THE FILES THAT MATCH AS BULLET POINTS, AND GIVE THE FILE PATHS"
)

print(f"Matching Files:\n{response.messages}")
