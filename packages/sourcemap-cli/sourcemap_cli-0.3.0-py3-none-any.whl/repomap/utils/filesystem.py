# ABOUTME: File system utilities - handling file discovery, git operations, and path utilities
"""File system utilities for repomap."""

import os
import subprocess
import time
from pathlib import Path
from typing import List, Set, Optional


# Important files list from aider.special
ROOT_IMPORTANT_FILES = [
    # Version Control
    ".gitignore",
    ".gitattributes",
    # Documentation
    "README",
    "README.md",
    "README.txt",
    "README.rst",
    "CONTRIBUTING",
    "CONTRIBUTING.md",
    "CONTRIBUTING.txt",
    "CONTRIBUTING.rst",
    "LICENSE",
    "LICENSE.md",
    "LICENSE.txt",
    "CHANGELOG",
    "CHANGELOG.md",
    "CHANGELOG.txt",
    "CHANGELOG.rst",
    "SECURITY",
    "SECURITY.md",
    "SECURITY.txt",
    "CODEOWNERS",
    # Package Management and Dependencies
    "requirements.txt",
    "Pipfile",
    "Pipfile.lock",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "npm-shrinkwrap.json",
    "Gemfile",
    "Gemfile.lock",
    "composer.json",
    "composer.lock",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "build.sbt",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "Cargo.lock",
    "mix.exs",
    "mix.lock",
    "pubspec.yaml",
    "pubspec.lock",
    "CMakeLists.txt",
    # CI/CD
    ".travis.yml",
    ".circleci/config.yml",
    ".github/workflows",
    ".gitlab-ci.yml",
    "Jenkinsfile",
    "azure-pipelines.yml",
    "appveyor.yml",
    ".drone.yml",
    "Makefile",
    # Config files
    ".editorconfig",
    ".eslintrc",
    ".eslintrc.js",
    ".eslintrc.json",
    ".prettierrc",
    ".prettierrc.js",
    ".prettierrc.json",
    ".stylelintrc",
    ".stylelintrc.js",
    ".stylelintrc.json",
    ".babelrc",
    ".babelrc.js",
    ".babelrc.json",
    "babel.config.js",
    "tsconfig.json",
    "jsconfig.json",
    ".nvmrc",
    ".rvmrc",
    ".ruby-version",
    ".python-version",
    ".tool-versions",
    ".env.example",
    ".env.sample",
    # Linting
    ".pylintrc",
    ".flake8",
    ".rubocop.yml",
    ".scalafmt.conf",
    ".dockerignore",
    ".gitpod.yml",
    "sonar-project.properties",
    "renovate.json",
    "dependabot.yml",
    ".pre-commit-config.yaml",
    "mypy.ini",
    "tox.ini",
    ".yamllint",
    "pyrightconfig.json",
    # Build and Compilation
    "webpack.config.js",
    "rollup.config.js",
    "parcel.config.js",
    "gulpfile.js",
    "Gruntfile.js",
    "build.xml",
    "build.boot",
    "project.json",
    "build.cake",
    "MANIFEST.in",
    # Testing
    "pytest.ini",
    "phpunit.xml",
    "karma.conf.js",
    "jest.config.js",
]

NORMALIZED_ROOT_IMPORTANT_FILES = set(
    os.path.normpath(path) for path in ROOT_IMPORTANT_FILES)


# Common source code extensions
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.cc', '.cxx',
    '.h', '.hpp', '.cs', '.rb', '.go', '.rs', '.php', '.swift', '.kt', '.scala',
    '.r', '.m', '.mm', '.pl', '.pm', '.lua', '.dart', '.ex', '.exs', '.clj',
    '.cljs', '.elm', '.ml', '.mli', '.fs', '.fsi', '.fsx', '.hs', '.lhs',
    '.jl', '.nim', '.cr', '.d', '.pas', '.pp', '.inc', '.asm', '.s',
    '.sh', '.bash', '.zsh', '.fish', '.ps1', '.psm1', '.psd1', '.bat', '.cmd',
    '.yaml', '.yml', '.json', '.xml', '.toml', '.ini', '.cfg', '.conf',
    '.html', '.htm', '.css', '.scss', '.sass', '.less', '.vue', '.svelte'
}

# Directories to skip
SKIP_DIRS = {
    '.git', '.svn', '.hg', '.bzr', '_darcs', '.fossil',
    'node_modules', 'venv', 'env', '.env', 'virtualenv',
    '__pycache__', '.pytest_cache', '.mypy_cache',
    'build', 'dist', 'target', 'out', 'bin', 'obj',
    '.idea', '.vscode', '.vs', '.eclipse', '.settings',
    'coverage', 'htmlcov', '.coverage', '.nyc_output',
    '.next', '.nuxt', '.cache', '.parcel-cache',
    'vendor', 'packages', 'bower_components',
    '.terraform', '.serverless', '.netlify'
}


def is_important(file_path: str) -> bool:
    """Check if a file is commonly important in codebases."""
    file_name = os.path.basename(file_path)
    dir_name = os.path.normpath(os.path.dirname(file_path))
    normalized_path = os.path.normpath(file_path)

    # Check for GitHub Actions workflow files
    if dir_name == os.path.normpath(".github/workflows") and file_name.endswith(".yml"):
        return True

    return normalized_path in NORMALIZED_ROOT_IMPORTANT_FILES


def filter_important_files(file_paths: List[str]) -> List[str]:
    """
    Filter a list of file paths to return only those that are commonly important in codebases.

    :param file_paths: List of file paths to check
    :return: List of file paths that match important file patterns
    """
    return list(filter(is_important, file_paths))


def get_gitignored_files(root_dir: str) -> Set[str]:
    """Get a set of files that are gitignored."""
    try:
        # First check if it's a git repo
        subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=root_dir,
            capture_output=True,
            check=True
        )

        # Get ignored files
        ignored_result = subprocess.run(
            ['git', 'ls-files', '--others', '--ignored', '--exclude-standard'],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=True
        )

        ignored_files = set()
        for line in ignored_result.stdout.strip().split('\n'):
            if line:
                # Convert to absolute path with proper separators
                abs_path = os.path.abspath(os.path.join(
                    root_dir, line.replace('/', os.sep)))
                ignored_files.add(abs_path)

        return ignored_files
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Git not available or not a git repo
        return set()


def get_staged_files(root_dir: str) -> List[str]:
    """Get files with staged changes in git."""
    try:
        # Get staged files
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=True
        )

        staged_files = []
        for line in result.stdout.strip().split('\n'):
            if line:
                # Convert to absolute path
                abs_path = os.path.abspath(os.path.join(root_dir, line))
                if os.path.exists(abs_path):
                    staged_files.append(abs_path)

        return staged_files
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def get_recently_modified_files(directory: str, days: int) -> List[str]:
    """Get files modified in the last N days."""
    cutoff_time = time.time() - (days * 24 * 60 * 60)
    recent_files = []

    for root, dirs, files in os.walk(directory):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            filepath = os.path.join(root, file)
            try:
                mtime = os.path.getmtime(filepath)
                if mtime > cutoff_time:
                    recent_files.append(filepath)
            except OSError:
                continue

    return recent_files


def find_src_files(directory: str, respect_gitignore: bool = True) -> List[str]:
    """Find source code files in a directory."""
    if not os.path.isdir(directory):
        return [directory]

    # Get gitignored files if needed
    gitignored = set()
    if respect_gitignore:
        gitignored = get_gitignored_files(directory)

    src_files = []
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories and common non-source directories
        dirs[:] = [d for d in dirs if not d.startswith(
            '.') and d not in SKIP_DIRS]

        for file in files:
            # Skip hidden files
            if file.startswith('.'):
                continue

            # Check if it's a source code file
            ext = os.path.splitext(file)[1].lower()
            filepath = os.path.join(root, file)

            # Skip gitignored files if requested
            if respect_gitignore and os.path.abspath(filepath) in gitignored:
                continue

            if ext in CODE_EXTENSIONS:
                src_files.append(filepath)
            # Also include files with no extension that might be scripts
            elif not ext and file.lower() in ['makefile', 'dockerfile', 'rakefile', 'gemfile', 'pipfile', 'procfile']:
                src_files.append(filepath)

    return src_files