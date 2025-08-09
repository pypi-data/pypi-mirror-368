"""
Input validation and user experience utilities for pckgr.
"""

import re
import sys
from typing import List, Optional, Union, Callable, Any
from pathlib import Path
from noexcept import no
from .errorCodes import ErrorCodes

def validateEmail(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validateGitHubUsername(username: str) -> bool:
    """
    Validate GitHub username format.
    
    Args:
        username: GitHub username to validate
        
    Returns:
        True if username format is valid, False otherwise
    """
    # GitHub usernames can contain alphanumeric chars and hyphens
    # Cannot start or end with hyphen, cannot have consecutive hyphens
    if not username:
        return False
    
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$'
    return bool(re.match(pattern, username)) and len(username) <= 39

def validateVersionString(version: str) -> bool:
    """
    Validate semantic version string format.
    
    Args:
        version: Version string to validate (e.g., "1.2.3")
        
    Returns:
        True if version format is valid, False otherwise
    """
    pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$'
    return bool(re.match(pattern, version))

def validateYesNo(response: str) -> bool:
    """
    Validate yes/no response.
    
    Args:
        response: User response to validate
        
    Returns:
        True if response is valid yes/no, False otherwise
    """
    return response.lower().strip() in ['y', 'yes', 'n', 'no', '1', '0', 'true', 'false']

def promptWithValidation(
    prompt: str,
    validator: Optional[Callable[[str], bool]] = None,
    error_message: str = "Invalid input. Please try again.",
    default: Optional[str] = None,
    max_attempts: int = 3
) -> str:
    """
    Prompt user for input with validation.
    
    Args:
        prompt: Prompt message to display
        validator: Function to validate input (returns True if valid)
        error_message: Message to show on validation failure
        default: Default value if user provides empty input
        max_attempts: Maximum number of attempts before giving up
        
    Returns:
        Validated user input
        
    Raises:
        ValueError: If max attempts exceeded or user cancels
    """
    for attempt in range(max_attempts):
        try:
            if default:
                response = input(f"{prompt} (default: {default}): ").strip()
                if not response:
                    response = default
            else:
                response = input(f"{prompt}: ").strip()
            
            if validator is None or validator(response):
                return response
            else:
                print(f"❌ {error_message}")
                if attempt < max_attempts - 1:
                    print(f"   ({max_attempts - attempt - 1} attempts remaining)")
                    
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Input cancelled by user.")
            no(ErrorCodes.USER_CANCELLED)
    
    no(ErrorCodes.MAX_ATTEMPTS_EXCEEDED)

def promptChoice(
    prompt: str,
    choices: List[str],
    default: Optional[str] = None,
    case_sensitive: bool = False
) -> str:
    """
    Prompt user to choose from a list of options.
    
    Args:
        prompt: Prompt message to display
        choices: List of valid choices
        default: Default choice if user provides empty input
        case_sensitive: Whether choices are case sensitive
        
    Returns:
        Selected choice
        
    Raises:
        ValueError: If user cancels or provides invalid input
    """
    if not case_sensitive:
        choices_lower = [c.lower() for c in choices]
    
    choices_display = "/".join(choices)
    if default:
        choices_display += f" (default: {default})"
    
    def validate_choice(response: str) -> bool:
        if case_sensitive:
            return response in choices
        else:
            return response.lower() in choices_lower
    
    error_msg = f"Please choose from: {', '.join(choices)}"
    
    try:
        response = promptWithValidation(
            f"{prompt} [{choices_display}]",
            validate_choice,
            error_msg,
            default
        )
    except no.way as e:
        # Re-raise with more specific error
        if ErrorCodes.USER_CANCELLED in e.nos:
            no(ErrorCodes.USER_CANCELLED)
        elif ErrorCodes.MAX_ATTEMPTS_EXCEEDED in e.nos:
            no(ErrorCodes.INVALID_CHOICE)
    
    # Return the original case version
    if not case_sensitive:
        for i, choice in enumerate(choices_lower):
            if response.lower() == choice:
                return choices[i]
    
    return response

def promptYesNo(prompt: str, default: Optional[bool] = None) -> bool:
    """
    Prompt user for yes/no input.
    
    Args:
        prompt: Prompt message to display
        default: Default value (True for yes, False for no)
        
    Returns:
        True for yes, False for no
    """
    default_str = None
    if default is True:
        default_str = "y"
    elif default is False:
        default_str = "n"
    
    response = promptChoice(
        prompt,
        ["y", "n", "yes", "no"],
        default_str,
        case_sensitive=False
    )
    
    return response.lower() in ['y', 'yes']

def promptPath(
    prompt: str,
    must_exist: bool = False,
    must_be_file: bool = False,
    must_be_dir: bool = False,
    default: Optional[str] = None
) -> Path:
    """
    Prompt user for a file/directory path with validation.
    
    Args:
        prompt: Prompt message to display
        must_exist: Whether the path must exist
        must_be_file: Whether the path must be a file
        must_be_dir: Whether the path must be a directory
        default: Default path
        
    Returns:
        Validated Path object
    """
    def validate_path(path_str: str) -> bool:
        try:
            path = Path(path_str).expanduser().resolve()
            
            if must_exist and not path.exists():
                print(f"❌ Path does not exist: {path}")
                return False
            
            if must_be_file and path.exists() and not path.is_file():
                print(f"❌ Path is not a file: {path}")
                return False
                
            if must_be_dir and path.exists() and not path.is_dir():
                print(f"❌ Path is not a directory: {path}")
                return False
                
            return True
        except Exception as e:
            print(f"❌ Invalid path: {e}")
            return False
    
    path_str = promptWithValidation(
        prompt,
        validate_path,
        "Invalid path",
        default
    )
    
    return Path(path_str).expanduser().resolve()

def validatePackageName(name: str) -> bool:
    """
    Validate Python package name.
    
    Args:
        name: Package name to validate
        
    Returns:
        True if package name is valid, False otherwise
    """
    # Python package names should be lowercase, can contain hyphens and underscores
    # Should not start with numbers
    if not name:
        return False
    
    pattern = r'^[a-z][a-z0-9._-]*$'
    return bool(re.match(pattern, name)) and len(name) <= 214  # PyPI limit

def safeInput(prompt: str, hide_input: bool = False) -> Optional[str]:
    """
    Safe input function that handles interruptions gracefully.
    
    Args:
        prompt: Prompt message to display
        hide_input: Whether to hide input (for passwords)
        
    Returns:
        User input or None if cancelled
    """
    try:
        if hide_input:
            import getpass
            return getpass.getpass(prompt)
        else:
            return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\n❌ Input cancelled.")
        no(ErrorCodes.USER_CANCELLED, soften=True)
        return None

def displayProgress(current: int, total: int, prefix: str = "Progress", length: int = 50) -> None:
    """
    Display a progress bar.
    
    Args:
        current: Current progress value
        total: Total value
        prefix: Prefix text
        length: Length of progress bar
    """
    if total == 0:
        return
        
    percent = min(100, (current * 100) // total)
    filled_length = (length * current) // total
    bar = '█' * filled_length + '-' * (length - filled_length)
    
    print(f'\r{prefix}: |{bar}| {percent}% ({current}/{total})', end='', flush=True)
    
    if current >= total:
        print()  # New line when complete

def confirmAction(action: str, danger_level: str = "medium") -> bool:
    """
    Confirm a potentially destructive action.
    
    Args:
        action: Description of the action
        danger_level: "low", "medium", or "high"
        
    Returns:
        True if user confirms, False otherwise
    """
    emojis = {
        "low": "⚠️",
        "medium": "🚨", 
        "high": "💀"
    }
    
    emoji = emojis.get(danger_level, "⚠️")
    
    print(f"\n{emoji} {action}")
    
    if danger_level == "high":
        # For high danger, require typing "yes"
        response = safeInput("Type 'yes' to confirm: ")
        return response == "yes"
    else:
        return promptYesNo("Do you want to continue?", default=False)
