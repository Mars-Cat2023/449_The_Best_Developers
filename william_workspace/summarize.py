from letta import create_client

client = create_client()

class FileTools:

    def extract_file_content(file_path: str, self) -> str:
        """
        Extracts content from a text-based file.

        Args:
            file_path (str): The path to the file

        Returns:
            str: The extracted content or raises an error if the file is not found
        """
        try:
            with open(file_path, 'r') as file:
                content = file.read()

            print(f"Extracted content from {file_path}: {content}...")
            return content

        except FileNotFoundError:
            print(f"Error: File {file_path} does not exist.")
            return None
        except Exception as e:
            print(f"An error occurred while reading the file: {str(e)}")
            return None

file_tools = FileTools()

file_extraction_tool = client.create_tool(FileTools.extract_file_content)

# Comment this line out before running the program for the first time
# Included to update the agent with new function when testing
client.delete_agent(client.get_agent_id("file_extraction_agent"))

file_extraction_agent_state = client.create_agent(
    name="file_extraction_agent",
    tools=[file_extraction_tool.name]
)

# FILL THIS FIELD BEFORE RUNNING
file_path = ""

response = client.send_message(
    agent_id=file_extraction_agent_state.id,
    role="user",
    message=f"Extract and summarize the content from the following file path: {file_path}"
)

print(f"File Summary:\n{response}")
