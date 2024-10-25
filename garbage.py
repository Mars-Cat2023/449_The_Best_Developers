from letta import create_client
import os


client = create_client()

# Uncomment to reset
# Comment out during initial run
client.delete_agent(client.get_agent_id("garbage_agent"))

# create agent to detect garbage
agent_name = "garbage_agent"

# Uncomment during first run/reset
agent_state = client.create_agent(agent_name)

agent_id = client.get_agent_id(agent_name)
agent_state = client.get_agent(agent_id)

# read all files and add to archival memory
directory = "testDirectory/"

for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    try:
        with open(file_path) as file:
            content = file.read()
            # print(content + " #end#")
            passage = client.insert_archival_memory(agent_id, content)
            passage[0].doc_id = file_path
            # print(passage)

    except FileNotFoundError:
        print(f"Error: File {file_path} does not exist.")

    except Exception as e:
        print(f"An error occurred while reading the file: {str(e)}")

# Getting deletion suggestion
response = client.send_message(
    agent_id=agent_id,
    role="user",
    message="Please give me the memory_id of one of the archival memories that you would recommend deleting.",
)

print(f"File Summary:\n{response.messages}")
