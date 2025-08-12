# Envyte

Tiny helper to auto-load environment variables from .env files and run your commands or Python scripts with those variables available. It also exposes a small Python API for reading env values safely.

## Features

- Auto-loads .env files from the current working directory before running your command/script
- Simple CLI wrapper: run any command or directly run a Python file
- Remembers the last Python script you ran in each project
- Small Python helpers: get, getBool, getInt, getString

## Installation

Install from PyPI (recommended):

```powershell
pip install envyte
```

This installs Envyte and its dependency `python-dotenv`.

If you’re developing locally from this repository:

```powershell
# from the repo root
python -m pip install -e .
python -m pip install python-dotenv
```

## How it works (at a glance)

- Envyte looks for .env files in your current working directory (where you invoke the CLI) and loads them before executing your command.
- Files are loaded in this sequence: .env.local, then .env.dev, then .env.prod, then .env. Because variables loaded later override earlier ones, keys in .env win if duplicated.
- When you call Envyte as a CLI without arguments, it tries to detect a Python entry file to run (see CLI section).
- Envyte stores a per-project “last run” Python script at the path below so it can auto-run the same file next time:
  - Windows example: `C:\\Users\\Contemelia\\.envyte.json`

Note: Environment files are resolved in the current working directory only.

## CLI usage

Basic form:

```powershell
envyte [command and args]
```

Examples:

```powershell
# Run a Python script explicitly
envyte python .\main.py --port 8080

# Run any arbitrary command (env is loaded first)
envyte uvicorn app:app --reload

# With no arguments: auto-detect a Python entry file
# - If exactly one *.py file exists in CWD, run it
# - If multiple, Envyte tries last run from C:\Users\Contemelia\.envyte.json
# - Otherwise it looks for main.py, app.py, server.py in that order
envyte
```

Alternative invocation (if you prefer module syntax):

```powershell
python -m envyte [command and args]
```

What gets loaded:

- In your project folder, create any of these files: `.env`, `.env.prod`, `.env.dev`, `.env.local`.
- Define variables in standard KEY=VALUE lines.

Example `.env`:

```ini
PORT=8000
DEBUG=true
SECRET_KEY=dev-secret
```

Example `.env.local`:

```ini
DEBUG=false
SECRET_KEY=local-override
```

Then run your script with Envyte so your app gets those values:

```powershell
envyte python .\main.py
```

### Last-run history

Envyte writes and reads a simple JSON file to remember the last Python script used per project (directory):

- Windows example path: `C:\\Users\\Contemelia\\.envyte.json`

This lets `envyte` (with no args) re-run the same entrypoint next time in the same folder.

## Python API usage

Importing `envyte` will automatically load environment variables from .env files in your current working directory.

```python
from envyte import get, getBool, getInt, getString

# .env is already auto-loaded on import

host = get("HOST", "127.0.0.1")
port = getInt("PORT", 8000)
debug = getBool("DEBUG", False)
secret = getString("SECRET_KEY", "")

print(host, port, debug, secret)
```

Available helpers:

- `get(key, default=None) -> Any`
- `getBool(key, default=False) -> bool` (truthy strings: "1", "true", "yes", "y", "on")
- `getInt(key, default=0) -> int` (safe fallback to default on parse errors)
- `getString(key, default="") -> str`

If you need manual control, you can import and call the loader directly before reading values:

```python
from envyte.core import autoLoadEnvironmentVariables
from envyte import get

autoLoadEnvironmentVariables()
token = get("API_TOKEN")
```

## Environment file priority

Load order in the current implementation (last wins on duplicates):

1) .env.local
2) .env.dev
3) .env.prod
4) .env (highest precedence because it loads last)

Note: The docstring in `envyte/core.py` references an intended priority of `.env.local > .env.dev > .env.prod > .env` (where earlier files would win). Given the loader uses `override=True` and the order above, variables in `.env` currently override the others. Adjust the load order if you prefer different precedence.

## Tips and troubleshooting

- Envyte loads from the current working directory. Run the CLI from your project folder where your .env files live.
- If `envyte` (no args) says it cannot find an entrypoint, specify your script explicitly: `envyte python .\main.py`.
- Ensure `python-dotenv` is installed in the same environment as your app.

## License

See `LICENSE` in this repository.
