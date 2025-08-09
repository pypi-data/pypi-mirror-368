import os, subprocess, shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
from types import SimpleNamespace
from noexcept import no
from .pathFinder import userProjectPath
from .errorCodes import ErrorCodes
from .cliUtilities import pushHandler, getProjectDependencies, directoryMapper, addDependenciesToProject

def init(cliArguments: Optional[dict] = None):
    # --- Get author details from helper function ---
    authorName, authorEmail, authorGitHub = getAuthorDetails()

    # --- Prepare paths and names ---
    packagePath = Path.cwd()
    name = packagePath.name
    scriptName = name.replace(".", "")
    pullFirst = bool(getattr(cliArguments, "pull", False)) if cliArguments else False
    preStatus = set()

    if pullFirst:
        if not (packagePath / ".git").exists():
            subprocess.run(["git", "init", str(packagePath)], check=True)
        repoURL = f"https://github.com/{authorGitHub}/{name}.git"
        if not remoteExists(packagePath):
            subprocess.run(["git", "-C", str(packagePath), "remote", "add", "origin", repoURL], check=True)
        try:
            subprocess.run(["git", "-C", str(packagePath), "fetch", "origin"], check=True)
            subprocess.run(["git", "-C", str(packagePath), "checkout", "-b", "main", "origin/main"], check=True)
            subprocess.run(["git", "-C", str(packagePath), "pull", "origin", "main"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error pulling changes: {e}")

        preStatus = getUntrackedFiles(packagePath)

        projectFiles = directoryMapper(packagePath)
        dependencies = getProjectDependencies(projectFiles)

        if dependencies:
            failed: Dict[str, str] = {}
            print(f"Detected dependencies: {', '.join(sorted(dependencies))}")
            if input("Would you like to install these dependencies? (y/N): ").strip().lower() == "y":
                venvPython = packagePath / ".venv" / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
                if venvPython.exists():
                    for dep in dependencies:
                        try:
                            subprocess.run([str(venvPython), "-m", "pip", "install", dep], check=True)
                        except subprocess.CalledProcessError as e:
                            failed[dep] = str(e)
                            no(ErrorCodes.PACKAGE_INSTALL_FAILED, f"Failed to install {dep}: {e}", soften=True)
                    if failed:
                        print("Some dependencies failed to install:")
                        for dep, error in failed.items():
                            print(f" - {dep}: {error}\n\n")
                else:
                    print("Virtual environment not found. Please create it first.")

            addDependenciesToProject(dependencies, packagePath)

    # --- Create target and src directories ---
    mainDirectory = packagePath / "src" / scriptName
    try:
        mainDirectory.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print(f"Directory {mainDirectory} already exists.")

    # Create .pckgr directory if it doesn't exist
    pckgrDir = packagePath / ".pckgr"
    if not pckgrDir.exists():
        pckgrDir.mkdir(exist_ok=True)

    # Create .pckgr/settings.json and .pckgr/patches if they don't exist
    configPath = pckgrDir / "settings.json"
    if not configPath.exists():
        configPath.write_text('{}', encoding='utf-8')
    patchesDir = pckgrDir / "patches"
    if not patchesDir.exists():
        patchesDir.mkdir(exist_ok=True)

    # --- File templates ---
    currentYear = datetime.now().year

    file_templates = {
        ".gitignore": """.venv/
.pckgr/
OLD*
__pycache__/
tests/
.vscode/
build/
dist/
*.egg-info/
*.patch
*.txt""",
        "AGENTS.md": f"# ./{name}/AGENTS.md",
        "CHANGELOG.md": f"# ./{name}/CHANGELOG.md",
        "LICENSE": f"""MIT License

Copyright (c) {currentYear} {authorName}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell    
copies of the Software, and to permit persons to whom the Software is        
furnished to do so, subject to the following conditions:                     

The above copyright notice and this permission notice shall be included in   
all copies or substantial portions of the Software.                          

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER      
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.""",
        "pyproject.toml": f"""[build-system]
requires = [
    "setuptools>=61.0",
    "wheel",
]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.0.1"
description = ""
authors = [
    {{ name = "{authorName}", email = "{authorEmail}" }}
]
readme = "README.md"
license = {{ file = "LICENSE" }}
requires-python = ">=3.8"
dependencies = []

[project.scripts]
{scriptName} = "{scriptName}.cli:main"
""",
        "README.md": f"# {name}\n\nSee [pyproject.toml](./pyproject.toml) for details.",
        "setup.py": f"""\
from setuptools import setup, find_packages

setup(
    name="{name}",
    version="0.0.1",
    description="",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="{authorName}",
    author_email="{authorEmail}",
    license="MIT",
    python_requires=">=3.8",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
    include_package_data=True,
    install_requires=[],
    entry_points={{
        "console_scripts": [
            "{scriptName}={scriptName}.cli:main"
        ],
    }},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)""",
    }

    # --- Create all root files if missing ---
    for fname, content in file_templates.items():
        fpath = packagePath / fname
        if not fpath.exists():
            fpath.write_text(content, encoding="utf-8")

    # --- src package basic files ---
    (mainDirectory / "__init__.py").write_text(f"# ./{scriptName}/__init__.py\n", encoding="utf-8")
    (mainDirectory / "__main__.py").write_text(f"# ./{scriptName}/__main__.py\n", encoding="utf-8")

    # --- cli.py with dict-driven parser ---
    (mainDirectory / "cli.py").write_text(f'''import argparse
from pathlib import Path

def build_parser(cli_templates):
    parser = argparse.ArgumentParser(prog="test")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for tmpl in cli_templates:
        cmd = tmpl["command"]
        desc = tmpl.get("description", None)
        func = tmpl.get("func", None)
        args = tmpl.get("args", [])
        sub = subparsers.add_parser(cmd, help=desc)
        for arg in args:
            flags = arg.get("flags", [])
            kwargs = {{k: v for k, v in arg.items() if k not in ("name", "flags")}}
            if flags:
                sub.add_argument(*flags, dest=arg["name"], **kwargs)
            else:
                sub.add_argument(arg["name"], **kwargs)
        if func:
            sub.set_defaults(func=func)
    return parser

def helpHandler(args):
    parser = args._parser
    if args.command:
        actions = [a for a in parser._actions if isinstance(a, argparse._SubParsersAction)]
        if actions:
            subparser = actions[0].choices.get(args.command)
            if subparser:
                subparser.print_help()
            else:
                parser.print_help()
        else:
            parser.print_help()
    else:
        parser.print_help()

cli_templates = [
    {{
        "command": "help",
        "description": "Show help for a command.",
        "func": helpHandler,
        "args": [
            {{
                "name": "command",
                "flags": ["-c", "--command"],
                "nargs": "?",
                "help": "Show help for this command."
            }}
        ]
    }}
]

def main():
    parser = build_parser(cli_templates)
    args = parser.parse_args()
    # Attach parser for use in help
    setattr(args, "_parser", parser)
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()''', encoding="utf-8")

    shouldPush = False
    if pullFirst:
        postStatus = getUntrackedFiles(packagePath)
        newFiles = postStatus - preStatus
        if newFiles:
            shouldPush = (
                input(
                    f"New files created: {', '.join(sorted(newFiles))}. Push to GitHub? (y/N): "
                )
                .strip()
                .lower()
                == "y"
            )
    if shouldPush:
        pushHandler(SimpleNamespace(message="Add missing files", tag=False))

    # --- Create virtual environment if missing ---
    venvPath = packagePath / ".venv"
    if not venvPath.exists():
        subprocess.run(['python', '-m', 'venv', str(venvPath)], check=True)

    # --- Initialize git repository if missing ---
    if not (packagePath / ".git").exists():
        subprocess.run(['git', 'init', str(packagePath)], check=True)

    # --- Define venv python path ---
    if os.name == "nt":
        venvPython = venvPath / "Scripts" / "python.exe"
    else:
        venvPython = venvPath / "bin" / "python"

    # --- Install build and twine in venv using the venv's python ---
    if venvPython.exists():
        # Install build tools first
        print("Installing build dependencies...")
        subprocess.run([str(venvPython), "-m", "pip", "install", "build", "twine"], cwd=str(packagePath), check=True)
        
        # Install the package itself in editable mode
        subprocess.run([str(venvPython), "-m", "pip", "install", "-e", "."], cwd=str(packagePath), check=True)
    else:
        print("Virtual environment not detected or python missing. Please install 'build' and 'twine' manually.")

    # --- Create .vscode/settings.json for VS Code Python interpreter ---
    vscodeDir = packagePath / ".vscode"
    if not vscodeDir.exists():
        vscodeDir.mkdir(exist_ok=True)
        settings = {
            "python.defaultInterpreterPath": str(venvPython)
        }
        import json
        settingsPath = vscodeDir / "settings.json"
        with open(settingsPath, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)

    # --- Add remote "origin" if missing ---
    if not remoteExists(packagePath):
        if commitExists(packagePath):
            if branchExists(packagePath, "main"):
                if repoExists(packagePath.name, authorGitHub):
                    if linkToRepo():
                        print("Remote repository linked successfully.")
                        return
                    else:
                       print("Unable to link to remote repository.") 
                else:
                    print("Unable to create repo.")
            else:
                print("Unable to create 'main' branch.")
                return
        else:
            print("Unable to create initial commit.")
            return
    else:
        print(f"GitHub remote already set.")

def getUntrackedFiles(packagePath: Path) -> set[str]:
    try:
        statusResult = subprocess.run(
            ["git", "-C", str(packagePath), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
        return {line[3:] for line in statusResult.stdout.splitlines() if line.startswith("??")}
    except subprocess.CalledProcessError:
        return set()

def commitExists(packagePath: Path) -> bool:
    print("Checking for initial commit...")
    try:
        subprocess.run(['git', '-C', str(packagePath), 'checkout', '-b', 'main'], check=True)
        subprocess.run(['git', '-C', str(packagePath), 'commit', '--allow-empty', '-m', 'Initial commit'], check=True)
        return True
    except subprocess.CalledProcessError:
        print("Initial commit already exists or failed.")
        return False
    
def repoExists(repository: str, gitUserName: str) -> bool:
    print(f"Checking if remote repository '{repository}' exists...")
    repoURL = f"https://github.com/{gitUserName}/{repository}.git"
    try:
        # Check if remote repository exists and is accessible
        subprocess.check_output(['git', 'ls-remote', repoURL], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        # Remote repo does not exist or can't be accessed
        print("Remote repository does not exist or is inaccessible.")

        # Attempt to create the repository using the GitHub CLI if available.
        gh = shutil.which("gh")
        if not gh:
            print("'gh' CLI not found. Cannot create repo on GitHub.")
            return False

        try:
            subprocess.run(
                [
                    gh,
                    "repo",
                    "create",
                    f"{gitUserName}/{repository}",
                    "--source",
                    str(userProjectPath),
                    "--remote",
                    "origin",
                    "--public",
                    "--confirm",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Failed to create repo on GitHub using gh: {e}")
            return False

    return True
    
def branchExists(packagePath: Path, branch: str) -> bool:
    print(f"Checking if branch '{branch}' exists @ {packagePath}")
    try:
        branches = subprocess.check_output(
            ['git', '-C', str(packagePath), 'branch'],
            encoding='utf-8'
        )

        if not branch in branches.split():
            try:
                subprocess.run(['git', '-C', str(packagePath), 'branch', branch], check=True)
            except subprocess.CalledProcessError:
                return False
        return True
    
    except Exception:
        return False

def remoteExists(packagePath: Path) -> bool:
    print("Checking if remote 'origin' exists @", packagePath)
    try:
        remotes = subprocess.check_output(
            ['git', '-C', str(packagePath), 'remote'],
            encoding='utf-8'
        )
        if "origin" in remotes.split():
            return True
        else:
            return False
    except Exception:
        return False

def linkToRepo() -> bool:
    try:
        subprocess.run([
                "git", "push", "--set-upstream", "origin", "main"
            ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error linking to remote repository: {e}")
        return False
    return True

def getAuthorDetails() -> tuple[str, str, str]:
    """Get author details from pckgr settings, git config, or prompt."""
    from .fileUtilities import _getAuthorDetailsFromSettings
    
    # Try to get author details from settings first
    authorDetails = _getAuthorDetailsFromSettings()
    authorName = authorDetails.get("name", "")
    authorEmail = authorDetails.get("email", "")
    authorGitHub = authorDetails.get("github", "")
    
    # If still missing from settings, try git config as fallback
    if not authorName or not authorEmail or not authorGitHub:
        def git_config_get(key: str) -> str:
            result = subprocess.run(
                ["git", "config", "--global", key],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return ""

        authorName = authorName or git_config_get("user.name")
        authorEmail = authorEmail or git_config_get("user.email")
        authorGitHub = authorGitHub or git_config_get("user.github")

    # If any are missing, prompt the user with validation
    if not authorName or not authorEmail or not authorGitHub:
        from .validationUtilities import promptWithValidation, validateEmail, validateGitHubUsername, promptChoice
        
        print("\nAuthor details required for package initialization:")
        
        if not authorName:
            authorName = promptWithValidation(
                "Author Name",
                lambda x: len(x.strip()) > 0,
                "Author name cannot be empty"
            )
        
        if not authorEmail:
            authorEmail = promptWithValidation(
                "Author Email",
                validateEmail,
                "Please enter a valid email address (e.g., user@example.com)"
            )
        
        if not authorGitHub:
            authorGitHub = promptWithValidation(
                "GitHub Username",
                validateGitHubUsername,
                "Please enter a valid GitHub username (alphanumeric and hyphens only, max 39 chars)"
            )

        # Ask where to save these details
        save_option = promptChoice(
            "Save these details to",
            ["1", "2", "3"],
            "1"
        )
        
        if save_option == "1":
            # Save to pckgr settings
            from .fileUtilities import setGlobalSetting
            authorInfo = {
                "name": authorName,
                "email": authorEmail,
                "github": authorGitHub
            }
            setGlobalSetting("author", authorInfo)
            print("Author details saved to pckgr settings.")
        elif save_option == "2":
            # Save to git config
            try:
                subprocess.run(
                    ["git", "config", "--global", "user.name", authorName],
                    check=True,
                )
                subprocess.run(
                    ["git", "config", "--global", "user.email", authorEmail],
                    check=True,
                )
                subprocess.run(
                    ["git", "config", "--global", "user.github", authorGitHub],
                    check=True,
                )
                print("Author details saved to git config.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to save to git config: {e}")
    else:
        print(f"Using author details: {authorName} <{authorEmail}> ({authorGitHub})")

    return authorName, authorEmail, authorGitHub