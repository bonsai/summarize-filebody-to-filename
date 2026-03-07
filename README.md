# Summarize Filebody to Filename

A Python script that summarizes file contents using a local LLM (Ollama) and renames files based on the summary.

## Requirements

- Python 3.7+
- [Ollama](https://ollama.com) installed and running
- A local LLM model (e.g., `llama3.2`, `mistral`)

## Installation

```bash
# Install Ollama from https://ollama.com
ollama pull llama3.2

# Install Python dependencies
pip install requests
```

## Usage

```bash
# Dry run (see what would happen)
python summarize-filename.py path/to/files

# Actually rename files
python summarize-filename.py path/to/files --execute

# Process a single file
python summarize-filename.py document.txt --execute

# Use different model
python summarize-filename.py . --model mistral --execute
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--model, -m` | Ollama model to use | `llama3.2` |
| `--host, -H` | Ollama host URL | `http://localhost:11434` |
| `--extensions, -e` | File extensions to process | `.txt, .md, .py, .js, .ts, .json, .yaml, .yml` |
| `--execute, -x` | Actually rename files (default: dry-run) | `false` |

## Example

```bash
# Summarize all markdown files in current directory
python summarize-filename.py . --extensions .md

# Rename a specific Python file
python summarize-filename.py my_script.py --execute --model mistral
```
