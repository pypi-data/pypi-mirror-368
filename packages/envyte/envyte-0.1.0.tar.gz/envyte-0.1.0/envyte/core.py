from pathlib import Path
from dotenv import load_dotenv





def autoLoadEnvironmentVariables():
    """
    Automatically load environment variables from .env files in priority order.
    Priority: .env.local > .env.dev > .env.prod > .env
    """
    
    search_directory = Path.cwd()
    env_files = [".env.local", ".env.dev", ".env.prod", ".env"]
    loaded_files = []
    
    for env_file in env_files:
        file_path = search_directory / env_file
        if file_path.exists():
            load_dotenv(dotenv_path = file_path, override = True)
            loaded_files.append(str(file_path))

    return loaded_files