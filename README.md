# Download Manager

A python download manager for Windows.


# Features

- Asynchronous downloads using aioHTTP
- Download Manager download controls: Start/Resume/Pause/Delete
- Single File Parallel Download
    - Using multiple connections to download one file faster

- Test Suite with > 100 Tests

- Stateless GUI to add and control downloads
    - GUI allows adding direct download links and setting the output file name
    - GUI shows progress of download including, progress, speed and more


# Usage

### App

1. Install python and git on Windows.
2. Clone the repository in git bash with `git clone https://github.com/Evoiis/Download-Manager.git`
3. Open the repo folder with git bash and create a virtual environment: `python -m venv venv`
4. Then activate the virtual environment with: `. venv/Scripts/activate`
5. Install dependencies with: `pip install -r requirements`
6. Run the program with: `python main.py`
7. Copy-Paste direct download links into Download URL input and press Add Download!

### Tests

Install test dependencies with `pip install -r requirements_test.txt`
Run `pytest` from repo root.

Use `-k <test or test_file name>` option to choose a specific test or test_file to run
Use `--log-cli-level=INFO` option to mute debug log messages


## Possible Extensions:
- Auto-shutdown/Keep-on Computer Feature
- Download Speed limiter
- Save metadata to file: Persist preferences and download_metadata between restarts
- Browser extension to grab direct download links from websites when browsing

- Separate ERROR from state
    - State should explain what the manager is doing with a certain download task
    - Errors should be kept separate
        - Especially now that errors can continue or pause a download depending on parameters...
