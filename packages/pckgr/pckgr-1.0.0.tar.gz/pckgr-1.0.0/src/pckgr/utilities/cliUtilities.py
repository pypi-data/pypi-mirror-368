import sys, os, toml, subprocess, glob, argparse, re
from pathlib import Path
from noexcept import no
from .pathFinder import userProjectPath
from .errorCodes import ErrorCodes
from typing import List, Dict, Set, Optional
from .fileUtilities import getProjectDependencies, getParam, mod, directoryMapper, settings

def validateAndSetVersion(repo_path: Path, version: str) -> bool:
    """
    Validate version format and set it in pyproject.toml.
    Returns True if successful, False otherwise.
    """
    # Validate semantic version format (major.minor.patch with optional pre-release)
    version_pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$'
    if not re.match(version_pattern, version):
        print(f"  ❌ Invalid version format: {version}")
        print(f"     Expected format: major.minor.patch (e.g., '1.2.3', '1.0.0-alpha.1')")
        return False
    
    pyproject_path = repo_path / 'pyproject.toml'
    if not pyproject_path.exists():
        print(f"  ❌ No pyproject.toml found in {repo_path}")
        return False
    
    try:
        # Load and update version
        data = toml.load(pyproject_path)
        if "project" not in data or "version" not in data["project"]:
            print(f"  ❌ No version field found in pyproject.toml")
            return False
        
        old_version = data["project"]["version"]
        data["project"]["version"] = version
        
        # Write back updated pyproject.toml
        with open(pyproject_path, "w", encoding="utf-8") as f:
            toml.dump(data, f)
        
        print(f"  📝 Version updated: {old_version} -> {version}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error updating version: {e}")
        return False

def buildTree(paths: List[Path], basePath: Path) -> dict:
    """
    Build a nested dictionary representation of directory structure.
    
    Creates a tree-like structure from a list of file paths, useful for
    displaying directory hierarchies in a human-readable format.
    
    Args:
        paths: List of Path objects to include in the tree
        basePath: Base path to calculate relative paths from
        
    Returns:
        Nested dictionary representing the directory structure
        
    Example:
        >>> paths = [Path("src/main.py"), Path("src/utils/helper.py")]
        >>> base = Path(".")
        >>> tree = buildTree(paths, base)
        >>> # Returns: {"src": {"main.py": {}, "utils": {"helper.py": {}}}}
    """
    tree: dict = {}
    for path in paths:
        parts = path.relative_to(basePath).parts
        node = tree
        for part in parts:
            node = node.setdefault(part, {})
    return tree

def showTree(tree: dict, indent: str = "") -> None:
    """
    Display a directory tree structure in a human-readable format.
    
    Recursively prints a tree representation using Unicode box-drawing
    characters to show the hierarchical structure.
    
    Args:
        tree: Nested dictionary representing the directory structure
        indent: Current indentation level for recursive calls
        
    Example:
        myproject/
        ├─ src/
        │  ├─ main.py
        │  └─ utils/
        │     └─ helper.py
        └─ README.md
    """
    entries = sorted(tree.items(), key=lambda item: (not item[1], item[0].lower()))
    for idx, (name, children) in enumerate(entries):
        connector = "└─" if idx == len(entries) - 1 else "├─"
        label = f"{name}/" if children else name
        print(f"{indent}{connector} {label}")
        if children:
            nextIndent = indent + ("   " if idx == len(entries) - 1 else "│  ")
            showTree(children, nextIndent)

def buildParser(cli_templates):
    parser = argparse.ArgumentParser(prog="pckgr")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for tmpl in cli_templates:
        cmd = tmpl["command"]
        desc = tmpl.get("description", None)
        func = tmpl.get("func", None)
        args = tmpl.get("args", [])
        sub = subparsers.add_parser(cmd, help=desc)
        for arg in args:
            flags = arg.get("flags", [])
            kwargs = {k: v for k, v in arg.items() if k not in ("name", "flags")}
            if flags:
                sub.add_argument(*flags, dest=arg["name"], **kwargs)
            else:
                sub.add_argument(arg["name"], **kwargs)
        if func:
            sub.set_defaults(func=func)
    return parser

def fixTomlLists(filePath: Path, fieldMap: Dict[str, List[str]]) -> None:
    if fieldMap == {}:
        return
    
    print(f"Fixing the following fields @ {filePath}:")

    for fieldName, values in fieldMap.items():
        print(f"  {fieldName}: {', '.join(values)}")

    for fieldName, values in fieldMap.items():
        listLiteral = "[" + ", ".join(f'\"{v}\"' for v in values) + "]"
        print(f"  Updating {fieldName} to: {listLiteral}")
        try:
            mod(filePath, fieldName, listLiteral)
        except RuntimeError:
            continue

def addDependenciesToProject(dependencies: Set[str], basePath: Path, install: bool = False) -> None:
    if not dependencies:
        return

    pyprojectPath = basePath / "pyproject.toml"
    setupPath = basePath / "setup.py"

    tomlData = {"project": {}}
    if pyprojectPath.exists():
        tomlData = toml.load(pyprojectPath)
    projectSection = tomlData.setdefault("project", {})
    existingTomlDeps = set(projectSection.get("dependencies", []))
    combinedDeps = sorted(existingTomlDeps | dependencies)
    projectSection["dependencies"] = combinedDeps
    with open(pyprojectPath, "w", encoding="utf-8") as f:
        toml.dump(tomlData, f)
    fixTomlLists(pyprojectPath, {"dependencies": combinedDeps})

    setupDepsList = getParam(setupPath, "install_requires") or []
    if isinstance(setupDepsList, (list, tuple, set)):
        setupDeps = set(setupDepsList)
    else:
        setupDeps = {str(setupDepsList)} if setupDepsList else set()
    setupCombined = sorted(setupDeps | dependencies)
    listLiteral = "[" + ", ".join(f'\"{d}\"' for d in setupCombined) + "]"
    mod(setupPath, "install_requires", listLiteral)

    if install:
        venvPath = basePath / ".venv"
        venvPython = venvPath / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
        print(f"Installing {', '.join(sorted(dependencies))}…")
        if venvPython.exists():
            subprocess.run([str(venvPython), "-m", "pip", "install", *sorted(dependencies)], check=False)
        else:
            subprocess.run([sys.executable, "-m", "pip", "install", *sorted(dependencies)], check=False)

def isGitRepository(path: Path) -> bool:
    """Check if a directory is git-managed."""
    git_dir = path / ".git"
    return git_dir.exists() and (git_dir.is_dir() or git_dir.is_file())

def findGitRepositories(base_path: Path) -> List[Path]:
    """Find git repositories in immediate subdirectories only."""
    git_repos = []
    try:
        for item in base_path.iterdir():
            if item.is_dir() and isGitRepository(item):
                git_repos.append(item)
    except (PermissionError, OSError):
        # Skip directories we can't access
        pass
    return sorted(git_repos)

def pushSingleRepository(repo_path: Path, args, dry_run: bool = False) -> bool:
    """Push a single git repository. Returns True on success."""
    print(f"\n🔄 Processing repository: {repo_path.name}")
    
    if dry_run:
        print(f"  🔍 DRY RUN MODE - No actual changes will be made")
    
    try:
        # Check if there are changes to commit
        result = subprocess.run(
            ['git', '-C', str(repo_path), 'status', '--porcelain'], 
            capture_output=True, text=True, check=True
        )
        
        has_changes = bool(result.stdout.strip())
        
        if has_changes:
            print(f"  📝 Found uncommitted changes")
            
            # Set custom version if specified (only for single repository pushes)
            custom_version = getattr(args, 'version', None)
            if custom_version and (repo_path / "pyproject.toml").exists():
                if not validateAndSetVersion(repo_path, custom_version):
                    return False
            
            # Update dependencies if this looks like a Python project and not skipped
            skip_deps = getattr(args, 'skip_deps', False)
            if not skip_deps and ((repo_path / "pyproject.toml").exists() or (repo_path / "setup.py").exists()):
                try:
                    # Run dependency update in the specific directory with timeout
                    import sys
                    result = subprocess.run([
                        sys.executable, '-c',
                        f"""
import os
os.chdir(r'{repo_path}')
from pckgr.utilities.cliUtilities import updateDependencies
updateDependencies()
"""
                    ], capture_output=True, text=True, timeout=30)  # 30 second timeout
                    
                    if result.returncode == 0:
                        print(f"  ✅ Dependencies updated")
                    else:
                        print(f"  ⚠️  Could not update dependencies: {result.stderr}")
                except subprocess.TimeoutExpired:
                    print(f"  ⚠️  Dependency update timed out (skipping)")
                except Exception as e:
                    print(f"  ⚠️  Could not update dependencies: {e}")
            
            if not dry_run:
                # Stage all changes
                subprocess.run(['git', '-C', str(repo_path), 'add', '.'], check=True)
                print(f"  📦 Changes staged")
                
                # Commit with provided message
                subprocess.run(['git', '-C', str(repo_path), 'commit', '-m', args.message], check=True)
                print(f"  💾 Changes committed")
            else:
                print(f"  📦 Would stage changes")
                print(f"  💾 Would commit with message: '{args.message}'")
        else:
            print(f"  ℹ️  No changes to commit")
        
        if not dry_run:
            # Push
            subprocess.run(['git', '-C', str(repo_path), 'push'], check=True)
            print(f"  🚀 Pushed to remote")
            
            # Push tags if requested
            if args.tag:
                subprocess.run(['git', '-C', str(repo_path), 'push', '--tags'], check=True)
                print(f"  🏷️  Tags pushed")
        else:
            print(f"  🚀 Would push to remote")
            if args.tag:
                print(f"  🏷️  Would push tags")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error: {e}")
        return False

def pushHandler(args):
    """Stage, commit, and push changes to GitHub (optionally push tags).
    
    If run in a non-git directory, scans immediate children for git repositories
    and offers to push them individually.
    """
    current_dir = userProjectPath
    
    # Check if current directory is git-managed
    if not isGitRepository(current_dir):
        print(f"📂 Current directory is not git-managed: {current_dir}")
        
        # Check if --version flag is used (not allowed for multi-repo pushes)
        custom_version = getattr(args, 'version', None)
        if custom_version:
            print(f"❌ --version flag is not available for multi-repository pushes")
            print(f"   Use --version only when pushing from within a single git repository")
            return
        
        # Look for git repositories in immediate subdirectories
        git_repos = findGitRepositories(current_dir)
        
        if not git_repos:
            print("❌ No git repositories found in immediate subdirectories.")
            return
        
        print(f"\n🔍 Found {len(git_repos)} git repositories:")
        for repo in git_repos:
            print(f"  📁 {repo.name}")
        
        # Filter repositories to only those with changes
        repos_with_changes = []
        print(f"\n🔍 Checking for uncommitted changes...")
        
        for repo in git_repos:
            try:
                result = subprocess.run(
                    ['git', '-C', str(repo), 'status', '--porcelain'], 
                    capture_output=True, text=True, check=True
                )
                has_changes = bool(result.stdout.strip())
                
                if has_changes:
                    repos_with_changes.append(repo)
                    print(f"  📝 {repo.name} - has uncommitted changes")
                else:
                    print(f"  ✅ {repo.name} - no changes to commit")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ {repo.name} - error checking status: {e}")
                # Still include it in case user wants to try pushing
                repos_with_changes.append(repo)
        
        if not repos_with_changes:
            print(f"\n✨ No repositories have uncommitted changes to push!")
            return
        
        print(f"\n🚀 Ready to push {len(repos_with_changes)} repositories with message: '{args.message}'")
        if args.tag:
            print(f"🏷️  Will also push tags")
        
        # Ask for each repository that has changes
        from .validationUtilities import promptChoice
        successful_pushes = 0
        
        # Check if we have a dry_run argument
        dry_run = getattr(args, 'dry_run', False)
        
        # Check if --all flag was used
        push_all = getattr(args, 'all', False)
        
        # Ask for push strategy if more than one repo and --all not specified
        if len(repos_with_changes) > 1 and not push_all:
            try:
                # Create a more user-friendly choice prompt
                def validate_strategy_choice(response: str) -> bool:
                    response = response.lower().strip()
                    return response in ['i', 'individual', 'a', 'all', 'c', 'cancel', '1', '2', '3']
                
                from .validationUtilities import promptWithValidation
                
                response = promptWithValidation(
                    f"Push strategy for {len(repos_with_changes)} repositories [i]ndividual/[a]ll/[c]ancel",
                    validate_strategy_choice,
                    "Please enter 'i', 'a', 'c' or full words 'individual', 'all', 'cancel'",
                    default="individual"
                )
                
                # Map response to full choice
                response = response.lower().strip()
                if response in ['i', 'individual', '1']:
                    choice = "individual"
                elif response in ['a', 'all', '2']:
                    choice = "all"
                elif response in ['c', 'cancel', '3']:
                    choice = "cancel"
                else:
                    choice = "individual"  # fallback
                if choice == "all":
                    push_all = True
                elif choice == "cancel":
                    print("🛑 Push operation cancelled")
                    return
            except no.way as e:
                if ErrorCodes.USER_CANCELLED in e.nos:
                    print(f"\n🛑 Push operation cancelled by user")
                    return
        elif push_all:
            print(f"🚀 Auto-pushing all {len(repos_with_changes)} repositories...")
        
        for repo in repos_with_changes:
            try:
                should_push = push_all
                
                if not push_all:
                    from .validationUtilities import promptYesNo
                    should_push = promptYesNo(f"\nPush repository '{repo.name}' (has changes)?", default=True)
                
                if should_push:
                    if push_all:
                        print(f"\n🔄 Auto-pushing repository: {repo.name}")
                    
                    if pushSingleRepository(repo, args, dry_run=dry_run):
                        successful_pushes += 1
                        action = "would be pushed" if dry_run else "pushed successfully"
                        print(f"  ✅ {repo.name} {action}")
                    else:
                        print(f"  ❌ Failed to process {repo.name}")
                        if push_all:
                            # Ask if they want to continue with remaining repos
                            from .validationUtilities import promptYesNo
                            if not promptYesNo(f"Continue with remaining repositories?", default=True):
                                break
                else:
                    print(f"  ⏭️  Skipped {repo.name}")
                    
            except no.way as e:
                if ErrorCodes.USER_CANCELLED in e.nos:
                    print(f"\n🛑 Push operation cancelled by user")
                    break
            except Exception as e:
                print(f"  ❌ Unexpected error with {repo.name}: {e}")
                if push_all:
                    from .validationUtilities import promptYesNo
                    if not promptYesNo(f"Continue with remaining repositories?", default=True):
                        break
        
        print(f"\n📊 Summary: {successful_pushes}/{len(repos_with_changes)} repositories pushed successfully")
        return
    
    # Original single repository logic
    dry_run = getattr(args, 'dry_run', False)
    if not pushSingleRepository(current_dir, args, dry_run=dry_run):
        no(ErrorCodes.PUSH_FAILED, "Failed to push current repository")

def pullHandler(args):
    """Pull latest changes from GitHub for the given branch and remote."""
    try:
        subprocess.run([
            'git', '-C', str(userProjectPath),
            'pull', args.remote, args.branch
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error pulling changes: {e}")
        return

def patchHandler(_):
    """Apply all patch files from .pckgr/patches using git apply."""
    patchDir = userProjectPath / ".pckgr" / "patches"
    if not patchDir.exists():
        print(f"No patches directory found at {patchDir}")
        return
    patchFiles = sorted(patchDir.glob("*.patch"))
    if not patchFiles:
        print(f"No patch files found in {patchDir}")
        return
    failed: Dict[str, subprocess.CalledProcessError] = {}
    succeeded = []
    for patchFile in patchFiles:
        try:
            subprocess.run(['git', '-C', str(userProjectPath), 'apply', str(patchFile)], check=True)
            succeeded.append(patchFile.name)
            print(f"Applied patch {patchFile.name}")
        except subprocess.CalledProcessError as e:
            failed[patchFile.name] = e

    if failed:
        print(f"Attempt to patch the following files failed:")
        for patch, error in failed.items():
            print(f"  - {patch}: {error}")

    if succeeded:
        # Move to the patches archive, creating it if necessary
        archiveDir = userProjectPath / ".pckgr" / "patches" / "archive"
        archiveDir.mkdir(parents=True, exist_ok=True)
        for patch in succeeded:
            patchFile = patchDir / patch
            if patchFile.exists():
                patchFile.rename(archiveDir / patch)

def buildHandler(args):
    """Bump version, build the package, and upload to PyPI."""
    updateDependencies()

    pyproject_path = userProjectPath / 'pyproject.toml'

    # Load project data
    data = toml.load(pyproject_path)
    version = data["project"]["version"]
    name = data["project"]["name"]
    
    # Check if custom version is specified
    custom_version = getattr(args, 'version', None)
    
    if custom_version:
        # Use custom version
        if not validateAndSetVersion(userProjectPath, custom_version):
            sys.exit(1)
        new_version = custom_version
    else:
        # Auto-bump version based on flags
        major, minor, patch = map(int, version.split('.'))

        # Bump according to CLI args (defaults to minor if all unset)
        if getattr(args, 'major', False):
            major += 1
            minor = 0
            patch = 0
        elif getattr(args, 'patch', False):  # patch bump
            patch += 1
        else:
            minor += 1
            patch = 0

        new_version = f"{major}.{minor}.{patch}"
        data["project"]["version"] = new_version

        # Write back updated pyproject.toml
        with open(pyproject_path, "w", encoding="utf-8") as f:
            toml.dump(data, f)
        
        print(f"Bumped version: {version} -> {new_version}")
    
    # Fix TOML lists formatting
    projectSection = data.get("project", {})
    buildSystem = data.get("build-system", {})
    listsToFix: Dict[str, List[str]] = {}
    if "dependencies" in projectSection:
        listsToFix["dependencies"] = projectSection["dependencies"]
    for branch, deps in projectSection.get("optional-dependencies", {}).items():
        listsToFix[branch] = deps
    if "requires" in buildSystem:
        listsToFix["requires"] = buildSystem["requires"]
    if listsToFix:
        fixTomlLists(pyproject_path, listsToFix)

    # Find the venv's python for running build/twine (same as before)
    venv_path = userProjectPath / ".venv"
    venv_python = venv_path / "Scripts" / "python.exe" if os.name == "nt" else venv_path / "bin" / "python"
    if not venv_python.exists():
        print("No venv found, aborting build.")
        sys.exit(1)

    # Build the package
    print(f"Building package...")
    try:
        subprocess.run(
            [str(venv_python), "-m", "build"],
            cwd=str(userProjectPath),
            check=True
        )
    except subprocess.CalledProcessError as e:
        if "No module named build" in str(e):
            print(f"❌ Build module not found. Installing build dependencies...")
            try:
                subprocess.run([str(venv_python), "-m", "pip", "install", "build", "twine"], check=True)
                print(f"✅ Build dependencies installed. Retrying build...")
                subprocess.run(
                    [str(venv_python), "-m", "build"],
                    cwd=str(userProjectPath),
                    check=True
                )
            except subprocess.CalledProcessError as install_error:
                print(f"❌ Failed to install build dependencies: {install_error}")
                sys.exit(1)
        else:
            print(f"❌ Build failed: {e}")
            sys.exit(1)
    
    # Find all new files for this version
    dist_pattern = f"{name.replace('-', '_')}-{new_version}*"
    dist_files = glob.glob(str(userProjectPath / "dist" / dist_pattern))

    if not dist_files:
        print(f"No distribution files found for version {new_version} in dist/.")
        return

    print(f"Built files: {[Path(f).name for f in dist_files]}")

    # Upload if requested
    upload = getattr(args, 'upload', False)
    test_pypi = getattr(args, 'test_pypi', False)
    
    if upload or test_pypi:
        upload_args = [str(venv_python), "-m", "twine", "upload"]
        
        if test_pypi:
            upload_args.extend(["--repository", "testpypi"])
            print(f"Uploading to Test PyPI...")
        else:
            print(f"Uploading to PyPI...")
            
        upload_args.extend(dist_files)
        
        subprocess.run(
            upload_args,
            cwd=str(userProjectPath),
            check=True
        )
        
        if test_pypi:
            print(f"✅ Package uploaded to Test PyPI successfully!")
        else:
            print(f"✅ Package uploaded to PyPI successfully!")
    else:
        print(f"✅ Package built successfully! Use --upload to publish to PyPI or --test-pypi for Test PyPI.")

def treeHandler(cliArguments):
    paths = directoryMapper(userProjectPath)
    tree = buildTree(paths, userProjectPath)
    print(f"{userProjectPath.name}/")
    showTree(tree)

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

def installDependency(importName: str, pypiName: str) -> Optional[str]:
    currentName = pypiName
    while True:
        venvPath = userProjectPath / ".venv"
        venvPython = venvPath / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
        executor = str(venvPython) if venvPython.exists() else sys.executable
        result = subprocess.run(
            [executor, "-m", "pip", "install", currentName],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            if currentName != importName:
                setAlias(currentName, importName)
            return currentName
        if (
            "Could not find a version that satisfies the requirement" in result.stderr
            or "No matching distribution found" in result.stderr
        ):
            choice = input(
                f"Package '{currentName}' not found. Provide alias or cancel? (a/c): "
            ).strip().lower()
            if choice.startswith("a"):
                aliasName = input("PyPI package name: ").strip()
                if aliasName:
                    currentName = aliasName
                    continue
                else:
                    continue
            else:
                print(f"Failed to install '{currentName}'.")
                return None
        else:
            print(result.stderr)
            return None

def extractPackageName(dependencyString: str) -> str:
    """
    Extract package name from dependency string that may include version specifiers.
    Examples:
    - "dearpygui>=1.9.0" -> "dearpygui"
    - "requests==2.25.1" -> "requests"
    - "numpy~=1.20" -> "numpy"
    - "flask" -> "flask"
    """
    from .fileUtilities import VERSION_SPECIFIER_PATTERN
    
    # Split by common version specifiers and take the first part
    packageName = VERSION_SPECIFIER_PATTERN.split(dependencyString)[0].strip()
    
    # Also handle brackets for extras like "package[extra]>=1.0"
    packageName = packageName.split('[')[0].strip()
    
    # Clean any remaining whitespace
    return packageName

def parseDependencySet(dependencies: set) -> set:
    """
    Parse a set of dependency strings to extract clean package names.
    Handles version specifiers like >=, ==, !=, <=, >, <, ~=, ^
    """
    # Use set comprehension for better performance
    return {
        extractPackageName(dep) if isinstance(dep, str) else str(dep)
        for dep in dependencies
        if (isinstance(dep, str) and extractPackageName(dep)) or not isinstance(dep, str)
    }

def updateDependencies() -> bool:
    print("Updating dependencies...")
    files = [path for path in directoryMapper(userProjectPath)
             if path.suffix == ".py" and not path == userProjectPath / "setup.py"
             ]

    pyprojectPath = userProjectPath / "pyproject.toml"
    setupPath = userProjectPath / "setup.py"

    tomlData = {"project": {}}
    if pyprojectPath.exists():
        tomlData = toml.load(pyprojectPath)
    projectSection = tomlData.setdefault("project", {})
    tomlDeps = parseDependencySet(set(projectSection.get("dependencies", [])))
    tomlExtras = {k: parseDependencySet(set(v)) for k, v in projectSection.get("optional-dependencies", {}).items()}

    setupDepsList = getParam(setupPath, "install_requires") or []
    if isinstance(setupDepsList, (list, tuple, set)):
        setupDeps = parseDependencySet(set(setupDepsList))
    else:
        setupDeps = parseDependencySet({str(setupDepsList)}) if setupDepsList else set()

    extrasDict = getParam(setupPath, "extras_require") or {}
    setupExtras = {}
    if isinstance(extrasDict, dict):
        for key, val in extrasDict.items():
            if isinstance(val, (list, tuple, set)):
                setupExtras[key] = parseDependencySet(set(val))
            else:
                setupExtras[key] = parseDependencySet({str(val)}) if val else set()

    branchDeps = {"main": tomlDeps | setupDeps}
    for branch, deps in tomlExtras.items():
        branchDeps.setdefault(branch, set()).update(deps)
    for branch, deps in setupExtras.items():
        branchDeps.setdefault(branch, set()).update(deps)

    ignoredPkgs = set(ignore())

    knownDependencies = set().union(*branchDeps.values()) if branchDeps else set()
    if knownDependencies:
        knownDependencies = checkForAlias(knownDependencies, "known")

    foundDependencies = getProjectDependencies(files)
    if foundDependencies:
        foundDependencies = checkForAlias(foundDependencies, "found")

    if ignoredPkgs:
        knownDependencies -= ignoredPkgs
        foundDependencies -= ignoredPkgs

    stale = knownDependencies - foundDependencies
    removeStale = False
    if stale:
        for pkg in sorted(stale):
            print("The following dependencies are no longer used in the project:")
        for pkg in sorted(stale):
            print(f"  - {pkg}")
        for pkg in list(stale):
            from .validationUtilities import promptYesNo
            if promptYesNo(f"Remove stale dependency '{pkg}'?", default=False):
                removeStale = True
                foundDependencies.discard(pkg)
                for branch, deps in list(branchDeps.items()):
                    if pkg in deps:
                        deps.discard(pkg)
                        if not deps and branch != "main":
                            if promptYesNo(f"Branch '{branch}' is now empty. Remove branch?", default=False):
                                del branchDeps[branch]
                if promptYesNo(f"Uninstall '{pkg}' from the virtual environment?", default=False):
                    venvPath = userProjectPath / ".venv"
                    venvPython = venvPath / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
                    if venvPython.exists():
                        subprocess.run([str(venvPython), "-m", "pip", "uninstall", "-y", pkg], check=False)
                    else:
                        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", pkg], check=False)
            else:
                print(f"Keeping '{pkg}' as a project dependency.")
                ignore(pkg)

    knownDependencies = set().union(*branchDeps.values()) if branchDeps else set()
    missing = foundDependencies - knownDependencies
    if not missing and not removeStale:
        print("Dependencies are up to date.")
        return False

    for importName in list(foundDependencies):
        if importName not in knownDependencies:
            includePkg = input(
                f"Include '{importName}' as a project dependency? (y/n/a for alias): "
            ).strip().lower()

            pypiName = importName
            if includePkg.startswith("a"):
                aliasName = input(
                    f"PyPI name for '{importName}': "
                ).strip()
                if aliasName:
                    pypiName = aliasName
                    # Add it to the alias list
                    setAlias(pypiName, importName)
            elif not includePkg.startswith("y"):
                addIgnore = input(
                    f"Add '{importName}' to ignore list? (y/n): "
                ).strip().lower()
                if addIgnore.startswith("y"):
                    ignore(importName)
                else:
                    installDependency(importName, importName)
                foundDependencies.discard(importName)
                continue

            branchList = list(branchDeps.keys())
            branchName = "main"
            if len(branchList) > 1:
                branchPrompt = (
                    f"Add '{pypiName}' to which branch ({', '.join(branchList)}) or new name: "
                )
            else:
                branchPrompt = (
                    f"Add '{pypiName}' to which branch (main or <new name>): "
                )
            chosenBranch = input(branchPrompt).strip()
            if chosenBranch:
                branchName = chosenBranch
            if branchName not in branchDeps:
                createBranch = input(
                    f"Branch '{branchName}' does not exist. Create it? (y/n): "
                ).strip().lower()
                if createBranch.startswith("y"):
                    branchDeps[branchName] = set()
                else:
                    branchName = "main"
            branchDeps.setdefault(branchName, set()).add(pypiName)

            try:
                __import__(importName)
            except ImportError:
                finalName = installDependency(importName, pypiName)
                if finalName:
                    if finalName != pypiName:
                        branchDeps[branchName].discard(pypiName)
                        branchDeps[branchName].add(finalName)
                        pypiName = finalName
                else:
                    branchDeps[branchName].discard(pypiName)
                    cancelIgnore = input(
                        f"Add '{importName}' to ignore list? (y/n): "
                    ).strip().lower()
                    if cancelIgnore.startswith("y"):
                        ignore(importName)
                    foundDependencies.discard(importName)
                    continue

    mainDeps = sorted(branchDeps.get("main", set()))
    optionalDeps = {k: sorted(v) for k, v in branchDeps.items() if k != "main"}

    projectSection["dependencies"] = mainDeps
    if optionalDeps:
        projectSection["optional-dependencies"] = optionalDeps
    else:
        projectSection.pop("optional-dependencies", None)
    with open(pyprojectPath, "w", encoding="utf-8") as f:
        toml.dump(tomlData, f)
    listsToFix: Dict[str, List[str]] = {"dependencies": mainDeps}
    listsToFix.update(optionalDeps)
    fixTomlLists(pyprojectPath, listsToFix)

    listLiteral = "[" + ", ".join(f'\"{d}\"' for d in mainDeps) + "]"
    mod(setupPath, "install_requires", listLiteral)

    if optionalDeps:
        extrasLiteral = "{" + ", ".join(
            f'\"{b}\": [' + ", ".join(f'\"{d}\"' for d in deps) + "]" for b, deps in optionalDeps.items()
        ) + "}"
        try:
            mod(setupPath, "extras_require", extrasLiteral)
        except RuntimeError:
            setupText = setupPath.read_text(encoding="utf-8")
            pattern = r"(install_requires\s*=\s*\[[^\]]*\],\n)"
            setupText = re.sub(pattern, f"\\1    extras_require={extrasLiteral},\n", setupText)
            setupPath.write_text(setupText, encoding="utf-8")
    else:
        setupText = setupPath.read_text(encoding="utf-8")
        setupText = re.sub(r"\s*extras_require\s*=\s*\{[^}]*\},\n", "\n", setupText, flags=re.MULTILINE | re.DOTALL)
        setupPath.write_text(setupText, encoding="utf-8")

    knownDependencies = set().union(*branchDeps.values()) if branchDeps else set()
    missing = foundDependencies - knownDependencies
    print(f"Updated dependencies: {', '.join(missing)}")

    return True

def setAlias(pypiName: str, importName: str) -> None:
    """
    Set an alias in .pckgr/settings.json for a PyPI package name to its import name.
    """
    config = settings()
    aliases = config.setdefault("alias", {})
    aliases[pypiName] = importName
    settings(config)
    print(f"Alias set: {pypiName} -> {importName}")
    
def checkForAlias(dependencies: Set[str], aliasType: str) -> Set[str]:
    """
    Check aliases in both module-level common aliases and project-level custom aliases.
    {"pypy": "nameOnPyPi", "imported": "nameToImport"}

    If empty then return the dependencies as is.
    """
    from .fileUtilities import _loadModuleSettings
    
    # Get common aliases from module settings
    moduleSettings = _loadModuleSettings()
    commonAliases = moduleSettings.get("common_aliases", {})
    
    # Get custom aliases from project settings  
    config = settings()
    customAliases = config.get("alias", {})
    
    # Combine aliases (custom overrides common)
    allAliases = {**commonAliases, **customAliases}
    
    if not allAliases:
        return dependencies
        
    if aliasType == "known": # This was found in the current toml/setup.py
        pass
    elif aliasType == "found": # This was an import found in the project
        for imported, pypi in allAliases.items():  # Note: swapped order for common_aliases
            if imported in dependencies:
                dependencies.discard(imported)
                dependencies.add(pypi)
    return dependencies

def ignore(pckg: Optional[str] = None) -> List[str]:
    config = settings()
    ignoreList = config.setdefault("ignore", [])
    if pckg:
        if pckg in ignoreList:
            ignoreList.remove(pckg)
            print(f"Removed '{pckg}' from ignore list")
        else:
            ignoreList.append(pckg)
            print(f"Added '{pckg}' to ignore list")
        settings(config)
    return ignoreList

