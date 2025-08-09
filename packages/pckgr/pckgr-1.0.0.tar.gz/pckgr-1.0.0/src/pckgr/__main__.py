from .utilities import *

cliTemplates = [
    {
        "command": "init",
        "description": "Initialise the current directory as a python package, link to a GitHub repository, and create a virtual environment.",
        "func": init,
        "args": [
            {
                "name": "pull",
                "flags": ["--pull"],
                "action": "store_true",
                "help": "Link to a repository and sync the local contents via a pull command before creating files.",
            }
        ]
    },
    {
        "command": "patch",
        "description": "Apply patch files from .pckgr/patches using git apply.",
        "func": patchHandler
    },
    {
        "command": "push",
        "description": "Push the package to GitHub.",
        "func": pushHandler,
        "args": [
            {
                "name": "tag",
                "flags": ["-t", "--tag"],
                "action": "store_true",
                "help": "Push tags to the remote."
            },
            {
                "name": "message",
                "flags": ["-m", "--message"],
                "default": "Committed by pckgr",
                "help": "Commit message for the push."
            },
            {
                "name": "dry_run",
                "flags": ["--dry-run"],
                "action": "store_true",
                "help": "Show what would be done without making actual changes."
            },
            {
                "name": "all",
                "flags": ["-a", "--all"],
                "action": "store_true",
                "help": "Push all repositories with changes without individual prompts."
            },
            {
                "name": "skip_deps",
                "flags": ["--skip-deps"],
                "action": "store_true",
                "help": "Skip dependency updates during push to avoid potential hangs."
            },
            {
                "name": "version",
                "flags": ["--version"],
                "type": str,
                "help": "Specify a custom version to set before pushing (e.g., '1.2.3'). Not available for multi-repository pushes."
            },
        ]
    },
    {
        "command": "pull",
        "description": "Pull the latest changes from GitHub.",
        "func": pullHandler,
        "args": [
            {
                "name": "branch",
                "flags": ["-b", "--branch"],
                "default": "main",
                "help": "Branch to pull from."
            },
            {
                "name": "remote",
                "flags": ["-r", "--remote"],
                "default": "origin",
                "help": "Remote to pull from."
            },
        ]
    },
    {
        "command": "build",
        "description": "Build the package and push it to PyPI.",
        "func": buildHandler,
        "args": [
            {
                "name": "patch",
                "flags": ["-p", "--pat", "--patch"],
                "action": "store_true",
                "help": "Bump the patch version."
            },
            {
                "name": "minor",
                "flags": ["-m", "--min", "--minor"],
                "action": "store_true",
                "help": "Bump the minor version (default)."
            },
            {
                "name": "major",
                "flags": ["-M", "--maj", "--major"],
                "action": "store_true",
                "help": "Bump the major version."
            },
            {
                "name": "upload",
                "flags": ["--upload"],
                "action": "store_true",
                "help": "Upload the built package to PyPI."
            },
            {
                "name": "test_pypi",
                "flags": ["--test-pypi"],
                "action": "store_true",
                "help": "Upload the built package to Test PyPI instead of PyPI."
            },
            {
                "name": "version",
                "flags": ["--version"],
                "type": str,
                "help": "Specify a custom version to set before building (e.g., '1.2.3'). Overrides automatic version bumping."
            }
        ]
    },
    {
        "command": "tree",
        "description": "Show a filtered directory tree based on your project's .gitignore",
        "func": treeHandler
    },
    {
        "command": "config",
        "description": "Configuration management for git and build settings",
        "func": configHandler,
        "args": [
            {
                "name": "show",
                "flags": ["--show"],
                "action": "store_true",
                "help": "Show current configuration"
            },
            {
                "name": "init",
                "flags": ["--init"],
                "action": "store_true",
                "help": "Initialize configuration with defaults"
            }
        ]
    },
    {
        "command": "tools",
        "description": "Various project utilities and mini-tools",
        "func": toolsHandler,
        "args": [
            {
                "name": "todo",
                "flags": ["--todo"],
                "action": "store_true",
                "help": "Scan for TODO items in code"
            },
            {
                "name": "update_dependencies",
                "flags": ["--update-dependencies"],
                "action": "store_true",
                "help": "Update project dependencies"
            },
            {
                "name": "stats",
                "flags": ["--stats"],
                "action": "store_true",
                "help": "Show code statistics"
            },
            {
                "name": "games",
                "flags": ["--games"],
                "action": "store_true",
                "help": "Fun mini-games for developers"
            },
            {
                "name": "tags",
                "flags": ["--tags"],
                "help": "Filter TODO items by tags (comma-separated: todo,fixme,hack,xxx,note,warning,bug)"
            },
            {
                "name": "priority",
                "flags": ["--priority"],
                "action": "store_true",
                "help": "Parse and show priority indicators in TODO items"
            },
            {
                "name": "group_by",
                "flags": ["--group-by"],
                "choices": ["file", "tag", "priority"],
                "default": "file",
                "help": "Group TODO items by file, tag, or priority"
            }
        ]
    },
    {
        "command": "help",
        "description": "Show help for a command.",
        "func": helpHandler,
        "args": [
            {
                "name": "command",
                "flags": ["-c", "--command"],
                "nargs": "?",
                "help": "Show help for this command."
            }
        ]
    }
]

def main():
    parser = buildParser(cliTemplates)
    args = parser.parse_args()
    # Attach parser for use in help
    setattr(args, "_parser", parser)
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()