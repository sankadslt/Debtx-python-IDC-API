import platform
import json

# configuration file path
CONFIG_FILE_PATH = "filePath.json"

def load_file_paths(file_path):
    """
    Load file paths configuration from a JSON file.
    """
    with open(file_path, 'r') as file:
        return json.load(file)

def get_correct_file_path(description):
    """
    Get the correct file path for the current platform based on the description.
    """
    # Load file paths configuration
    file_paths_config = load_file_paths(CONFIG_FILE_PATH)

    os_type = platform.system()
    for entry in file_paths_config.get("filePaths", []):
        if entry.get("description") == description:
            paths = entry.get("paths", {})
            if os_type == "Windows":
                return paths.get("windows")
            elif os_type == "Linux":
                return paths.get("linux")
            else:
                raise ValueError(f"Unsupported platform: {os_type}")
    raise KeyError(f"Description '{description}' not found in file paths configuration.")

# Main block
if __name__ == "__main__":
    log_file_path = get_correct_file_path("Log file path")
    print(log_file_path)