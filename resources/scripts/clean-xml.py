import os

# Function to process a single file
def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Find the index of the line containing <PolymerNanocomposite>
        start_index = next((i for i, line in enumerate(lines) if '<PolymerNanocomposite>' in line), None)

        # If the tag is found, keep lines from that point onward
        if start_index is not None:
            lines = lines[start_index:]
        else:
            print(f"Warning: <PolymerNanocomposite> tag not found in {file_path}")

        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)

        # print(f"Processed: {file_path}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

# Function to iterate through all files in the given directory
def process_directory(directory_path):
    if not os.path.isdir(directory_path):
        print(f"Error: The provided path is not a directory: {directory_path}")
        return

    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            process_file(file_path)

# Example usage
directory_path = "../datasets/nanomine/"
process_directory(directory_path)
