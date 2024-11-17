from letta import create_client
import json

client = create_client()

class FileTools:

    def extract_file_content(self, file_path: str) -> str:
        """
        Extracts content from a text-based file, limiting the amount of content returned.

        Args:
            file_path (str): The path to the file

        Returns:
            str: A portion of the extracted content or an error message if the file is not found or unsupported
        """
        import os
        import PyPDF2
        import magic

        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist.")
            return None

        # Use python-magic to detect the file type - not reliant on just the extension
        ftype = magic.from_file(file_path, mime=True)
        content = ""

        try:
            if ftype == "text/plain":
                # Text files
                with open(file_path, 'r') as file:
                    content = file.read()
            elif ftype == "application/pdf":
                # PDF files
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    content = "\n".join(page.extract_text() for page in pdf_reader.pages)
            else:
                print(f"Unsupported file type: {ftype}")
                return None

            # Limit the content to the first 1000 characters (or any number you prefer)
            max_length = 1000
            content_snippet = content[:max_length]
            
            print(f"Extracted content snippet from {file_path}")
            return content_snippet

        except Exception as e:
            print(f"An error occurred while reading the file: {str(e)}")
            return None

    def summarize_file_content(self, file_path: str) -> str:
        """
        Extracts and summarizes the content from a file.

        Args:
            file_path (str): The path to the file

        Returns:
            str: The summary of the file content
        """
        content = self.extract_file_content(file_path)
        if not content:
            return "No content to summarize."

        # Send the content to Letta for summarization
        response = json.loads(str(client.send_message(
            agent_id=client.get_agent_id("file_extraction_agent"),
            role="user",
            message=f"Extract and summarize the content from the following file path: {file_path}. Provide an objective, assured summary without first-person or second-person language."
        )))
        # print(response)
        for i in response["messages"]:
            if i["message_type"] == "function_call":
                if i["function_call"]["name"] == "send_message":
                    s = i["function_call"]["arguments"]
                    print(s)
                    return s.replace('{\n  \"message\": \"', '').replace('\"\n}', '')
        return "File summary unavailable"

# file_tools = FileTools()

# file_extraction_tool = client.create_tool(FileTools.extract_file_content)

# client.delete_agent(client.get_agent_id("file_extraction_agent"))

# file_extraction_agent_state = client.create_agent(
#     name="file_extraction_agent",
#     tools=[file_extraction_tool.name]
# )

# file_path = "/Users/owenrejevich/Development/test/test.txt"

# response = client.send_message(
#     agent_id=file_extraction_agent_state.id,
#     role="user",
#     message=f"Extract and summarize the content from the following file path: {file_path}"
# )

# print(f"File Summary:\n{response}")
