"""
Configuration utilities for pckgr - handles advanced configuration options.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from noexcept import no
from .pathFinder import userProjectPath
from .fileUtilities import _loadModuleSettings
from .errorCodes import ErrorCodes

class GitConfig:
    """
    Git configuration management with customizable remotes and commands.
    """
    
    def __init__(self, project_path: Optional[Path] = None):
        """
        Initialize git configuration.
        
        Args:
            project_path: Path to the project (defaults to userProjectPath)
        """
        self.project_path = project_path or userProjectPath
        self._config = self._loadGitConfig()
    
    def _loadGitConfig(self) -> Dict[str, Any]:
        """Load git configuration from pckgr settings."""
        settings_path = self.project_path / ".pckgr" / "settings.json"
        default_config = {
            "git": {
                "default_remote": "origin",
                "default_branch": "main",
                "remotes": {
                    "origin": {"url": "", "type": "github"}
                },
                "commands": {
                    "push_flags": [],
                    "pull_flags": [],
                    "commit_flags": ["-S"] if self._hasGpgSigning() else []
                },
                "hooks": {
                    "pre_push": [],
                    "post_push": [],
                    "pre_pull": [],
                    "post_pull": []
                }
            }
        }
        
        if settings_path.exists():
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults
                    git_config = config.get("git", {})
                    for key, value in default_config["git"].items():
                        if isinstance(value, dict):
                            git_config.setdefault(key, {}).update(value)
                        else:
                            git_config.setdefault(key, value)
                    return {"git": git_config}
            except (json.JSONDecodeError, FileNotFoundError) as e:
                no(ErrorCodes.CONFIG_PARSE_ERROR, f"Failed to load git config: {e}", soften=True)
        
        return default_config
    
    def _hasGpgSigning(self) -> bool:
        """Check if GPG signing is configured."""
        try:
            result = subprocess.run(
                ["git", "config", "--global", "user.signingkey"],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0 and result.stdout.strip()
        except Exception:
            return False
    
    def getRemotes(self) -> Dict[str, Dict[str, str]]:
        """Get configured remotes."""
        return self._config["git"]["remotes"]
    
    def addRemote(self, name: str, url: str, remote_type: str = "github") -> None:
        """
        Add a new remote configuration.
        
        Args:
            name: Remote name
            url: Remote URL
            remote_type: Type of remote (github, gitlab, bitbucket, other)
        """
        self._config["git"]["remotes"][name] = {
            "url": url,
            "type": remote_type
        }
        self._saveConfig()
    
    def getDefaultRemote(self) -> str:
        """Get the default remote name."""
        return self._config["git"]["default_remote"]
    
    def setDefaultRemote(self, remote: str) -> None:
        """Set the default remote."""
        self._config["git"]["default_remote"] = remote
        self._saveConfig()
    
    def getDefaultBranch(self) -> str:
        """Get the default branch name."""
        return self._config["git"]["default_branch"]
    
    def setDefaultBranch(self, branch: str) -> None:
        """Set the default branch."""
        self._config["git"]["default_branch"] = branch
        self._saveConfig()
    
    def getCommandFlags(self, command: str) -> List[str]:
        """
        Get additional flags for git commands.
        
        Args:
            command: Git command (push, pull, commit)
            
        Returns:
            List of additional flags
        """
        return self._config["git"]["commands"].get(f"{command}_flags", [])
    
    def addCommandFlag(self, command: str, flag: str) -> None:
        """Add a flag to a git command."""
        key = f"{command}_flags"
        if key not in self._config["git"]["commands"]:
            self._config["git"]["commands"][key] = []
        if flag not in self._config["git"]["commands"][key]:
            self._config["git"]["commands"][key].append(flag)
            self._saveConfig()
    
    def removeCommandFlag(self, command: str, flag: str) -> None:
        """Remove a flag from a git command."""
        key = f"{command}_flags"
        if key in self._config["git"]["commands"]:
            try:
                self._config["git"]["commands"][key].remove(flag)
                self._saveConfig()
            except ValueError:
                pass
    
    def getHooks(self, hook_type: str) -> List[str]:
        """
        Get hooks for a specific event.
        
        Args:
            hook_type: Hook type (pre_push, post_push, pre_pull, post_pull)
            
        Returns:
            List of hook commands
        """
        return self._config["git"]["hooks"].get(hook_type, [])
    
    def addHook(self, hook_type: str, command: str) -> None:
        """Add a hook command."""
        if hook_type not in self._config["git"]["hooks"]:
            self._config["git"]["hooks"][hook_type] = []
        if command not in self._config["git"]["hooks"][hook_type]:
            self._config["git"]["hooks"][hook_type].append(command)
            self._saveConfig()
    
    def runHooks(self, hook_type: str) -> bool:
        """
        Run hooks for a specific event.
        
        Args:
            hook_type: Hook type to run
            
        Returns:
            True if all hooks succeeded, False otherwise
        """
        hooks = self.getHooks(hook_type)
        for hook in hooks:
            try:
                result = subprocess.run(
                    hook,
                    shell=True,
                    cwd=self.project_path,
                    check=False
                )
                if result.returncode != 0:
                    print(f"❌ Hook failed: {hook}")
                    return False
            except Exception as e:
                print(f"❌ Hook error: {hook} - {e}")
                return False
        return True
    
    def _saveConfig(self) -> None:
        """Save configuration to file."""
        settings_path = self.project_path / ".pckgr" / "settings.json"
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing settings
        existing_config = {}
        if settings_path.exists():
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Merge git config
        existing_config["git"] = self._config["git"]
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, indent=4)

class BuildConfig:
    """
    Build system configuration management.
    """
    
    def __init__(self, project_path: Optional[Path] = None):
        """Initialize build configuration."""
        self.project_path = project_path or userProjectPath
        self._config = self._loadBuildConfig()
    
    def _loadBuildConfig(self) -> Dict[str, Any]:
        """Load build configuration."""
        module_settings = _loadModuleSettings()
        return module_settings.get("build", {
            "backend": "setuptools",
            "upload_to": "pypi",
            "test_pypi": False,
            "build_requirements": [],
            "dist_formats": ["wheel", "sdist"],
            "upload_options": {}
        })
    
    def getBuildBackend(self) -> str:
        """Get the build backend."""
        return self._config.get("backend", "setuptools")
    
    def setBuildBackend(self, backend: str) -> None:
        """Set the build backend."""
        valid_backends = ["setuptools", "flit", "poetry", "hatch"]
        if backend not in valid_backends:
            raise ValueError(f"Invalid backend. Must be one of: {valid_backends}")
        self._config["backend"] = backend
        self._saveConfig()
    
    def getUploadTarget(self) -> str:
        """Get the upload target."""
        return self._config.get("upload_to", "pypi")
    
    def setUploadTarget(self, target: str) -> None:
        """Set the upload target."""
        valid_targets = ["pypi", "test-pypi", "custom"]
        if target not in valid_targets:
            raise ValueError(f"Invalid target. Must be one of: {valid_targets}")
        self._config["upload_to"] = target
        self._saveConfig()
    
    def isTestPypi(self) -> bool:
        """Check if using test PyPI."""
        return self._config.get("test_pypi", False)
    
    def setTestPypi(self, use_test: bool) -> None:
        """Set whether to use test PyPI."""
        self._config["test_pypi"] = use_test
        self._saveConfig()
    
    def getDistFormats(self) -> List[str]:
        """Get distribution formats."""
        return self._config.get("dist_formats", ["wheel", "sdist"])
    
    def setDistFormats(self, formats: List[str]) -> None:
        """Set distribution formats."""
        valid_formats = ["wheel", "sdist", "egg"]
        for fmt in formats:
            if fmt not in valid_formats:
                raise ValueError(f"Invalid format '{fmt}'. Must be one of: {valid_formats}")
        self._config["dist_formats"] = formats
        self._saveConfig()
    
    def _saveConfig(self) -> None:
        """Save build configuration."""
        # This would typically save to module settings
        # For now, we'll print a message
        print(f"Build configuration updated: {self._config}")

def initializeProjectConfig() -> None:
    """Initialize project configuration with sensible defaults."""
    git_config = GitConfig()
    build_config = BuildConfig()
    
    print("🔧 Initializing project configuration...")
    
    # Set up basic git configuration
    try:
        # Try to detect current remote
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            cwd=git_config.project_path,
            check=False
        )
        if result.returncode == 0:
            remote_url = result.stdout.strip()
            git_config.addRemote("origin", remote_url)
            print(f"✅ Detected git remote: {remote_url}")
    except Exception:
        pass
    
    print("✅ Configuration initialized")

def showConfig() -> None:
    """Display current configuration."""
    git_config = GitConfig()
    build_config = BuildConfig()
    
    print("⚙️  Current Configuration")
    print("=" * 30)
    
    print("\n📋 Git Configuration:")
    print(f"  Default Remote: {git_config.getDefaultRemote()}")
    print(f"  Default Branch: {git_config.getDefaultBranch()}")
    
    remotes = git_config.getRemotes()
    if remotes:
        print("  Remotes:")
        for name, info in remotes.items():
            print(f"    {name}: {info.get('url', 'Not set')} ({info.get('type', 'unknown')})")
    
    print("\n🔨 Build Configuration:")
    print(f"  Backend: {build_config.getBuildBackend()}")
    print(f"  Upload Target: {build_config.getUploadTarget()}")
    print(f"  Test PyPI: {build_config.isTestPypi()}")
    print(f"  Formats: {', '.join(build_config.getDistFormats())}")

def configHandler(args) -> None:
    """Handle config command."""
    if hasattr(args, 'show') and args.show:
        showConfig()
    elif hasattr(args, 'init') and args.init:
        initializeProjectConfig()
    else:
        print("🔧 Configuration Management")
        print("=" * 25)
        print()
        print("Available options:")
        print("  --show    Show current configuration")
        print("  --init    Initialize configuration with defaults")
        print()
        print("Examples:")
        print("  pckgr config --show")
        print("  pckgr config --init")
