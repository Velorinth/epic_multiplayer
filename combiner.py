import os

def combine_files(start_dir, output_file):
    """
    Finds all .yml and .py files in a directory, and writes their path and content
    to a single output file.

    Args:
        start_dir (str): The directory to search for files (e.g., 'client').
        output_file (str): The name of the file to save the combined content.
    """
    # Check if the starting directory exists.
    if not os.path.isdir(start_dir):
        print(f"Error: Directory '{start_dir}' not found.")
        return

    try:
        # Open the output file in write mode, which will overwrite it if it exists.
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # os.walk recursively goes through the directory tree.
            for dirpath, _, filenames in os.walk(start_dir):
                for filename in filenames:
                    # Check if the file has the desired extension.
                    if filename.endswith(('.yml', '.py')):
                        # Construct the full path to the file.
                        file_path = os.path.join(dirpath, filename)
                        
                        try:
                            # Open and read the content of the current file.
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                                content = infile.read()
                            
                            # Write the file path to the output file.
                            outfile.write(f"{file_path}\n")
                            
                            # Write the content of the file to the output file.
                            outfile.write(f"{content}\n")
                            
                            # Add a separator for clarity, though the prompt didn't require it.
                            # You can remove this line if you want the exact format.
                            outfile.write("-" * 20 + "\n")

                        except Exception as e:
                            print(f"Error reading file {file_path}: {e}")
                            
        print(f"Successfully combined files into '{output_file}'.")

    except IOError as e:
        print(f"Error writing to output file {output_file}: {e}")

# --- Main execution ---
if __name__ == "__main__":
    # Define the directory to search and the output filename.
    # This script assumes a 'client' directory exists in the same location
    # where the script is run.
    search_directory = 'client'
    output_filename = 'filesall.txt'
    
    # Create a dummy 'client' directory and some files for testing purposes
    # if it doesn't exist.
    if not os.path.exists(search_directory):
        print(f"Creating dummy '{search_directory}' directory for demonstration.")
        os.makedirs(os.path.join(search_directory, 'subdir'))
        with open(os.path.join(search_directory, 'main.py'), 'w') as f:
            f.write('print("Hello from main.py")')
        with open(os.path.join(search_directory, 'config.yml'), 'w') as f:
            f.write('setting: value\n')
        with open(os.path.join(search_directory, 'subdir', 'utils.py'), 'w') as f:
            f.write('def helper():\n    return "helper function"')

    combine_files(search_directory, output_filename)
