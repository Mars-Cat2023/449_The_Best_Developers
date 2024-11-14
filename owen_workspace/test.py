from summarize import FileTools

filetools = FileTools()

file_path = "/Users/owenrejevich/Development/test/test.txt"
summary = filetools.summarize_file_content(file_path)
print(summary)