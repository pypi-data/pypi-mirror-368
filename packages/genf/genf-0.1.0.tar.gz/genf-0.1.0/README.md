# genf
A Python script to automatically extract file names and contents from a specified directory. Outputs results to a text file named after the folder. Excludes folders like node_modules and files like package-lock.json to focus on relevant files. Ideal for quickly gathering file context for AI or code analysis.

## Installation
```bash
pip install genf
```

## Usage
Run in any directory:
```bash
genf
```
Output will be saved to a file named after the current folder (e.g., folder_name.txt).

## Features
- Extracts file names and contents from a directory.
- Excludes irrelevant folders (node_modules, venv, etc.) and files (package-lock.json, etc.).
- Saves output to a text file named after the folder.
    
## Author
- **marhaendev**
- Email: marhaendev@gmail.com
- Websites: marhaendev.com | hasanaskari.com
    
## License
MIT License