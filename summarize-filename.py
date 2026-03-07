#!/usr/bin/env python3
"""
Summarize file contents and rename files using a local LLM (Ollama).
"""

import os
import sys
import argparse
import requests
from pathlib import Path


def summarize_with_ollama(content: str, model: str = "llama3.2", host: str = "http://localhost:11434") -> str:
    """
    Summarize content using Ollama local LLM.
    Returns a short filename-friendly summary.
    """
    prompt = f"""Summarize the following content into a short filename (3-5 words, snake_case, no extensions). 
Return ONLY the filename, nothing else.

Content:
{content[:3000]}  # Limit content to avoid token issues
"""
    
    try:
        response = requests.post(
            f"{host}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3}
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip().strip('"')
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to Ollama at {host}")
        print("Make sure Ollama is running: ollama serve")
        sys.exit(1)
    except Exception as e:
        print(f"LLM error: {e}")
        return None


def sanitize_filename(name: str) -> str:
    """Convert text to a safe filename format."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|？*'
    for char in invalid_chars:
        name = name.replace(char, "_")
    # Convert to lowercase and replace spaces with underscores
    name = name.lower().replace(" ", "_")
    # Remove multiple underscores
    while "__" in name:
        name = name.replace("__", "_")
    # Trim to reasonable length
    return name[:50]


def process_file(filepath: Path, model: str, host: str, dry_run: bool = True) -> None:
    """Process a single file: summarize and rename."""
    print(f"\nProcessing: {filepath.name}")
    
    try:
        content = filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = filepath.read_text(encoding="latin-1")
    except Exception as e:
        print(f"  Error reading file: {e}")
        return
    
    # Get summary from LLM
    summary = summarize_with_ollama(content, model, host)
    if not summary:
        print("  Failed to get summary from LLM")
        return
    
    # Sanitize the summary for use as filename
    new_name = sanitize_filename(summary)
    
    # Preserve original extension
    extension = filepath.suffix
    new_filename = f"{new_name}{extension}"
    new_path = filepath.parent / new_filename
    
    if new_path == filepath:
        print(f"  Name unchanged: {new_filename}")
        return
    
    if dry_run:
        print(f"  Would rename: {filepath.name} → {new_filename}")
    else:
        # Handle existing file conflict
        if new_path.exists():
            print(f"  Conflict: {new_filename} already exists")
            counter = 1
            while new_path.exists():
                new_filename = f"{new_name}_{counter}{extension}"
                new_path = filepath.parent / new_filename
                counter += 1
            print(f"  Using: {new_filename}")
        
        filepath.rename(new_path)
        print(f"  Renamed: {filepath.name} → {new_filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Summarize file contents and rename using local LLM (Ollama)"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="File or directory to process (default: current directory)"
    )
    parser.add_argument(
        "--model", "-m",
        default="llama3.2",
        help="Ollama model to use (default: llama3.2)"
    )
    parser.add_argument(
        "--host", "-H",
        default="http://localhost:11434",
        help="Ollama host URL (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--extensions", "-e",
        nargs="+",
        default=[".txt", ".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml"],
        help="File extensions to process"
    )
    parser.add_argument(
        "--execute", "-x",
        action="store_true",
        help="Actually rename files (default: dry-run)"
    )
    
    args = parser.parse_args()
    
    target = Path(args.path).resolve()
    
    if not target.exists():
        print(f"Error: Path does not exist: {target}")
        sys.exit(1)
    
    # Collect files to process
    if target.is_file():
        files = [target]
    else:
        files = []
        for ext in args.extensions:
            files.extend(target.glob(f"**/*{ext}"))
    
    if not files:
        print(f"No files found to process in: {target}")
        sys.exit(0)
    
    print(f"Found {len(files)} file(s) to process")
    print(f"Model: {args.model}")
    print(f"Host: {args.host}")
    print(f"Dry run: {not args.execute}")
    print("-" * 50)
    
    for filepath in files:
        process_file(filepath, args.model, args.host, dry_run=not args.execute)
    
    print("\nDone!")


if __name__ == "__main__":
    main()
