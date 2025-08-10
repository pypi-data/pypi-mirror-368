# File Organizer

A Python script to automatically organize files in a specified folder into categorized subfolders based on file types.

## Features

- Automatically moves files into folders like **Documents**, **Images**, **Videos**, **Audio**, **Archives**, **Apps**, and **Others**.
- Supports organizing any folder by providing the path as an argument or via prompt.
- Non-destructive: existing folders and files not matched by categories remain unaffected.
- Easy to use and extend with more file type categories.
- Installable as a Python package with a simple CLI command.

## Setup

Before running the tool, run the setup script once to install dependencies, upgrade pip tools, and configure your environment:

~~~bash
./setup.sh
~~~

This will:
	•	Upgrade pip, setuptools, and wheel.
	•	Install any dependencies listed in requirements.txt (if present).
	•	Add the file-organizer CLI command to your PATH.

## Usage

After setup, you can organize files using the CLI command from anywhere:

~~~bash
file-organizer /path/to/folder
~~~

- Repalce "/path/to/folder" with your destination folder path which you want to organize.
- If no folder path is provided, it defaults to organizing the Downloads folder.

Example:

~~~bash
file-organizer /Users/username/Downloads
~~~

## Requirements

- Python 3.6 or higher

## How it works

- Scans the target folder.
- Detects file types based on extensions.
- Moves files into corresponding folders.
- Creates folders if they don’t exist.

## Notes

- Running the CLI multiple times will not affect already organized files.
- The CLI does not modify files inside existing subfolders.
- Files without known extensions are moved to the **Others** folder.

# Sample Output:
✅ Moved: example.pdf → Documents
✅ Moved: vacation.jpg → Images
✅ Moved: project.zip → Archives
✅ Moved: app.dmg → Apps

📂 Folder '/Users/username/Downloads' organized successfully!

# Screenshot
![Script Output Screenshot](File_Organizer_Screenshot.PNG)