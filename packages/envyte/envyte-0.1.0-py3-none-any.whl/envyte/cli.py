from json import loads, dumps
from pathlib import Path
from sys import argv, executable, exit
from subprocess import run as subprocessRun

from .core import autoLoadEnvironmentVariables



HISTORY_PATH = Path.home() / ".envyte.json"





def loadHistory():
    
    if HISTORY_PATH.exists():
        try:
            return loads(HISTORY_PATH.read_text())
        except Exception:
            return {}
    return {}


def saveHistory(history):
    
    try:
        HISTORY_PATH.write_text(dumps(history, indent = 2))
    except Exception as error:
        print(f"lazy-env: Warning - could not save history: {error}")


def saveLastRun(file_path: Path):
    
    history = loadHistory()
    project_path = str(Path.cwd().resolve())
    history[project_path] = str(file_path.resolve())
    saveHistory(history)



def getLastRun():
    
    history = loadHistory()
    project_path = str(Path.cwd().resolve())
    saved_file = history.get(project_path)
    if saved_file:
        saved_path = Path(saved_file)
        if saved_path.exists():
            return saved_path
    return None



def run():
    
    # Case 1: When the command is specified
    if len(argv) > 1:
        target = Path(argv[1])
        
        if target.exists() and target.suffix == '.py':
            saveLastRun(target)
            autoLoadEnvironmentVariables()
            subprocessRun([executable, str(target)] + argv[2:])
        
        else:
            autoLoadEnvironmentVariables()
            subprocessRun(argv[1:])
        
        return

    # Case 2: No command → detect what to run
    # discover python files, ignoring packaging scripts like setup.py
    python_files = [p for p in Path.cwd().glob("*.py") if p.name.lower() != "setup.py"]

    if len(python_files) == 1:
        found_script = python_files[0]
    elif len(python_files) > 1:
        found_script = getLastRun()
        if not found_script:
            candidates = ["main.py", "app.py", "server.py"]
            found_script = next((Path(c) for c in candidates if Path(c).exists()), None)
    else:
        found_script = None

    if not found_script:
        print("Envyte: No script specified and no last/known entrypoint found.")
        print("Usage: envyte [command] or envyte python your_script.py")
        exit(1)

    saveLastRun(found_script)
    autoLoadEnvironmentVariables()
    subprocessRun([executable, str(found_script)])
