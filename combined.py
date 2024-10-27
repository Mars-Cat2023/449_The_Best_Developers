import os
import json
from datetime import datetime
from letta import create_client

client = create_client()

class FileTools:
    def extract_file_content(self, file_path: str) -> str:
        """
        Extracts content from a text-based file.

        Args:
            file_path (str): The path to the file

        Returns:
            str: The extracted content or None if the file is not found or an error occurs
        """
        try:
            with open(file_path, 'r', encoding='ISO-8859-1') as file:
                content = file.read()
            print(f"Extracted content from {file_path}: {content[:100]}...")
            return content
        except FileNotFoundError:
            print(f"Error: File {file_path} does not exist.")
            return None
        except Exception as e:
            print(f"An error occurred while reading the file: {str(e)}")
            return None

file_tools = FileTools()


def create_file_entry(file_path):
    file_data = {
        "type": "file",
        "path": file_path,
        "creation_timestamp": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
        "summary": file_tools.extract_file_content(file_path)
    }
    return file_data

def create_folder_entry(folder_path):
    folder_data = {
        "type": "folder",
        "path": folder_path,
        "children": {}
    }
    return folder_data

def build_file_system(directory):
    file_system = {}
    for root, folders, files in os.walk(directory):
        current_folder = create_folder_entry(root)
        
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_entry = create_file_entry(file_path)
            current_folder["children"][file_name] = file_entry
        
        for folder_name in folders:
            folder_path = os.path.join(root, folder_name)
            folder_entry = create_folder_entry(folder_path)
            current_folder["children"][folder_name] = folder_entry

        file_system[root] = current_folder

    return file_system

if __name__ == "__main__":
    directory = "TestDirectory2"

    file_system_data = build_file_system(directory)

    with open("combinedFileDataTable.json", "w") as file_system_output:
        json.dump(file_system_data, file_system_output, indent=4)
    
    print("File system data with summaries and timestamps saved to 'combinedFileDataTable.json'")

