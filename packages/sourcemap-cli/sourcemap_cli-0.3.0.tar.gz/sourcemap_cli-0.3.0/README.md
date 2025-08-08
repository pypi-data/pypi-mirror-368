# RepoMap

A tool for generating intelligent repository maps showing code structure and relationships.

RepoMap analyzes your codebase to create a compact, context-aware map that highlights the most relevant parts of your code. It uses tree-sitter for parsing, PageRank for ranking importance, and intelligent filtering to create useful repository maps.

This is a standalone version extracted from the [aider](https://github.com/paul-gauthier/aider) project.

## Features

- **Smart code analysis**: Uses tree-sitter to parse code and understand symbols
- **Intelligent ranking**: Employs PageRank algorithm to identify important code sections
- **Language support**: Supports many programming languages through tree-sitter
- **Caching**: Fast incremental updates with intelligent caching
- **Customizable**: Configurable token limits and context windows

## Installation

### Using uv (recommended)

```bash
# Install as a standalone tool (creates isolated environment)
uv tool install repomap
```

For development or building from source:

```bash
# Build the package
uv build

# Install the built wheel
uv pip install dist/repomap-*.whl

# Or for development (editable install)
uv pip install -e .
uv pip install -e ".[dev]"  # with dev dependencies
```

### Using pip

```bash
# Install from PyPI
pip install repomap

# Or install from source
pip install .

# Development install
pip install -e .[dev]
```

## Usage

By default, running `repomap` with no arguments launches the interactive TUI. Supplying
arguments invokes the classic CLI.

### CLI Examples

Generate a repository map for specific files:

```bash
repomap file1.py file2.js directory/
```

### Options

- `--tokens, -t`: Maximum tokens for the map (default: 8192)
- `--verbose, -v`: Enable verbose output
- `--root, -r`: Root directory for the repository (default: current directory)
- `--refresh`: Cache refresh strategy (auto/always/files/manual, default: auto)
- `--max-context-window`: Maximum context window size
- `--output, -o`: Output file path (default: stdout)
- `--format, -f`: Output format - `text` or `json` (default: text)
- `--all-files`: Include all files regardless of ranking (ignores token limit)
- `--list-files`: Just list all files found, no analysis
- `--no-gitignore`: Include files that are gitignored
- `--git-staged`: Only include files with staged changes in git
- `--recent DAYS`: Only include files modified in the last N days

### Examples

Analyze Python files in a project:

```bash
repomap src/*.py --tokens 2048
```

Generate a map for an entire directory:

```bash
repomap . --verbose
```

Analyze multiple specific files:

```bash
repomap main.py utils.py tests/ --root /path/to/project
```

Save output to a file:

```bash
repomap src/ --output repomap.txt
```

Generate JSON output:

```bash
repomap src/ --format json --output repomap.json
```

Pipe JSON output to other tools:

```bash
repomap src/*.py --format json | jq '.files | keys'
```

List all source files in a directory:

```bash
repomap src/ --list-files
```

Include ALL files in the analysis (ignore token limit):

```bash
repomap src/ --all-files --output full-analysis.txt
```

Analyze only staged files (great for pre-commit):

```bash
repomap --git-staged
```

Analyze files modified in the last 7 days:

```bash
repomap --recent 7
```

Include gitignored files in the analysis:

```bash
repomap src/ --no-gitignore
```

Combine filters - staged files from the last 3 days:

```bash
repomap --git-staged --recent 3
```

### Python Library

Use RepoMap as a library to generate text or JSON maps programmatically:

```python
from repomap import generate_map, MapOptions

files = ["."]  # files or directories
opts = MapOptions(tokens=2048, root=".")

# Text output
text_map = generate_map(files, options=opts, format="text")

# JSON output (as Python dict)
json_map = generate_map(files, options=opts, format="json")
```

### Interactive TUI

A Rich/Textual-based TUI is included. After installing the package:

```bash
repomap-tui
# or just run with no args
repomap
```

Controls: G (Generate), S (Save), Q (Quit). Edit Root/Tokens/Format fields in the top bar, then press Generate. The main pane is scrollable.
The TUI uses Textual (built on Rich), so it works cross‑platform without curses.

### Prompts Mode (fallback)

If your terminal cannot run the TUI, `repomap` falls back to a simple prompts mode (Typer).
You’ll be asked for the root directory, token budget, and output format; the result prints
to the terminal. You can always use the full CLI via `repomap map ...`.

## How it Works

RepoMap generates a ranked map of your codebase by:

1. **Parsing code files** using tree-sitter to identify symbols and references
2. **Building a graph** of symbol definitions and references
3. **Ranking code sections** using PageRank based on reference patterns
4. **Filtering results** to fit within token limits while preserving important context
5. **Formatting output** as a concise, readable map

The tool prioritizes:
- Files with many incoming references
- Important symbols (classes, functions) that are frequently used
- Key configuration and documentation files
- Recently modified files when using cache

### Why some files might not appear

By default, SourceMap CLI shows only the most "important" files based on:
- **Token limit** (default 8192) - Only includes files that fit within this limit
- **PageRank score** - Files with more references from other files rank higher
- **File types** - Only source code files are analyzed (configurable extensions)

To see all files:
- Use `--all-files` to ignore token limits and include everything
- Use `--list-files` to see what files are being found
- Increase `--tokens` to include more files in the analysis

## Supported Languages

RepoMap supports all languages that have tree-sitter parsers and tag queries, including:

- Python
- JavaScript/TypeScript  
- Java
- C/C++
- Go
- Rust
- Ruby
- And many more...

Run `repomap --supported-languages` to see the full list.

## Output Formats

### Text Format (default)

The text output is a human-readable map showing:
- File paths
- Important symbols and their locations
- Contextual code snippets
- `⋮` symbols indicating condensed sections

Example:

```
src/main.py:
│class Application:
│    def __init__(self):
│        self.config = Config()
│    
│    def run(self):
│        ...

src/config.py:
│class Config:
│    def load(self):
│        ...
```

### JSON Format

The JSON output provides structured data about the codebase:

```json
{
  "files": {
    "src/main.py": {
      "symbols": [
        {
          "name": "Application",
          "kind": "def",
          "line": 5
        },
        {
          "name": "__init__",
          "kind": "def", 
          "line": 7
        }
      ]
    }
  },
  "summary": {
    "total_files": 10,
    "tokens": 1024,
    "root": "/path/to/project"
  }
}
```

This format is useful for:
- Integration with other tools
- Generating documentation
- Code analysis pipelines
- Custom visualizations

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

This tool is based on the repository map functionality from [aider](https://github.com/paul-gauthier/aider), an AI pair programming tool.
