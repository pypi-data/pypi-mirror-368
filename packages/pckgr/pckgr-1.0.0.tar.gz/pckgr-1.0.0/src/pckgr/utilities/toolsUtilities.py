"""
Tools utilities for pckgr - various mini-tools and utilities for project management.
"""

import re
import sys
import os
import random
import time
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass
from noexcept import no
from .pathFinder import userProjectPath
from .fileUtilities import directoryMapper, _loadModuleSettings
from .cliUtilities import updateDependencies
from .errorCodes import ErrorCodes

@dataclass
class TodoItem:
    """Represents a TODO item found in code."""
    file: str
    line: int
    content: str
    tag: str
    priority: str = "normal"

# Pre-compiled regex patterns for TODO scanning
# Note: Using string literals to avoid self-detection in scanning
TODO_PATTERNS = {
    'todo': re.compile(r'(?:#|//|/\*|\*|<!--)\s*' + 'todo' + r'\s*:?\s*(.+?)(?:\*/|-->|$)', re.IGNORECASE),
    'fixme': re.compile(r'(?:#|//|/\*|\*|<!--)\s*' + 'fixme' + r'\s*:?\s*(.+?)(?:\*/|-->|$)', re.IGNORECASE),
    'hack': re.compile(r'(?:#|//|/\*|\*|<!--)\s*' + 'hack' + r'\s*:?\s*(.+?)(?:\*/|-->|$)', re.IGNORECASE),
    'xxx': re.compile(r'(?:#|//|/\*|\*|<!--)\s*' + 'xxx' + r'\s*:?\s*(.+?)(?:\*/|-->|$)', re.IGNORECASE),
    'note': re.compile(r'(?:#|//|/\*|\*|<!--)\s*' + 'note' + r'\s*:?\s*(.+?)(?:\*/|-->|$)', re.IGNORECASE),
    'warning': re.compile(r'(?:#|//|/\*|\*|<!--)\s*' + 'warning' + r'\s*:?\s*(.+?)(?:\*/|-->|$)', re.IGNORECASE),
    'bug': re.compile(r'(?:#|//|/\*|\*|<!--)\s*' + 'bug' + r'\s*:?\s*(.+?)(?:\*/|-->|$)', re.IGNORECASE),
}

def scanTodos(includePriority: bool = False, filterTags: Optional[List[str]] = None) -> List[TodoItem]:
    """
    Scan the project for TODO items and related comments.
    
    Args:
        includePriority: Whether to parse priority indicators like (HIGH), [CRITICAL]
        filterTags: Only include specific tags (e.g., ['todo', 'fixme'])
    
    Returns:
        List of TodoItem objects
    """
    todos: List[TodoItem] = []
    
    # Get all project files
    projectFiles = directoryMapper(userProjectPath)
    
    # Filter to text-based files we can scan
    textExtensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
        '.cs', '.php', '.rb', '.go', '.rs', '.kt', '.swift', '.dart', '.scala',
        '.html', '.css', '.scss', '.sass', '.less', '.xml', '.yaml', '.yml',
        '.json', '.md', '.txt', '.cfg', '.ini', '.toml', '.sh', '.bat', '.ps1',
        '.sql', '.r', '.m', '.mm', '.pl', '.lua', '.vim', '.el', '.clj', '.ex'
    }
    
    scanFiles = [f for f in projectFiles if f.is_file() and f.suffix.lower() in textExtensions]
    
    for file in scanFiles:
        try:
            content = file.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            
            for lineNum, line in enumerate(lines, 1):
                for tag, pattern in TODO_PATTERNS.items():
                    if filterTags and tag not in filterTags:
                        continue
                        
                    match = pattern.search(line)
                    if match:
                        todoContent = match.group(1).strip()
                        
                        # Always extract priority and clean content for consistency
                        priority = _extractPriority(todoContent)
                        todoContent = _cleanPriorityFromContent(todoContent)
                        
                        # If priority parsing is not requested, reset to normal
                        if not includePriority:
                            priority = "normal"
                        
                        relativePath = str(file.relative_to(userProjectPath))
                        
                        todoItem = TodoItem(
                            file=relativePath,
                            line=lineNum,
                            content=todoContent,
                            tag=tag.upper(),
                            priority=priority
                        )
                        todos.append(todoItem)
                        
        except (UnicodeDecodeError, PermissionError, FileNotFoundError) as e:
            # Skip files we can't read
            no(ErrorCodes.FILE_READ_ERROR, f"Cannot read file {file}: {e}", soften=True)
            continue
    
    return sorted(todos, key=lambda x: (x.file, x.line))

def _extractPriority(content: str) -> str:
    """Extract priority from TODO content."""
    priority_patterns = [
        (r'\b(?:critical|urgent|high)\b', 'critical'),
        (r'\b(?:medium|normal|med)\b', 'medium'),
        (r'\b(?:low|minor|trivial)\b', 'low'),
        (r'\[(?:critical|urgent|high)\]', 'critical'),
        (r'\[(?:medium|normal|med)\]', 'medium'),
        (r'\[(?:low|minor|trivial)\]', 'low'),
        (r'\((?:critical|urgent|high)\)', 'critical'),
        (r'\((?:medium|normal|med)\)', 'medium'),
        (r'\((?:low|minor|trivial)\)', 'low'),
        (r'!!!', 'critical'),
        (r'!!', 'medium'),
        (r'!', 'low'),
    ]
    
    content_lower = content.lower()
    for pattern, priority in priority_patterns:
        if re.search(pattern, content_lower):
            return priority
    
    return 'normal'

def _cleanPriorityFromContent(content: str) -> str:
    """Remove priority indicators from TODO content."""
    # Remove common priority indicators - more specific patterns first
    patterns = [
        r'\[(?:critical|urgent|high|medium|normal|med|low|minor|trivial)\]',  # [PRIORITY]
        r'\((?:critical|urgent|high|medium|normal|med|low|minor|trivial)\)',  # (PRIORITY)
        r'\b(?:critical|urgent|high|medium|normal|med|low|minor|trivial)\b',  # standalone words
        r'!{1,3}',  # exclamation marks
        r'\(\s*\)',  # empty parentheses left behind
        r'\[\s*\]',  # empty brackets left behind
    ]
    
    for pattern in patterns:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    content = ' '.join(content.split())
    
    return content.strip()

def displayTodos(todos: List[TodoItem], groupBy: str = 'file', showPriority: bool = False) -> None:
    """
    Display TODO items in a formatted way.
    
    Args:
        todos: List of TodoItem objects
        groupBy: How to group todos ('file', 'tag', 'priority')
        showPriority: Whether to show priority in output
    """
    if not todos:
        print("✅ No TODO items found in the project!")
        return
    
    print(f"\n📝 Found {len(todos)} TODO items:\n")
    
    if groupBy == 'file':
        _displayTodosByFile(todos, showPriority)
    elif groupBy == 'tag':
        _displayTodosByTag(todos, showPriority)
    elif groupBy == 'priority':
        _displayTodosByPriority(todos, showPriority)
    else:
        _displayTodosList(todos, showPriority)

def _displayTodosByFile(todos: List[TodoItem], showPriority: bool) -> None:
    """Display todos grouped by file."""
    currentFile = None
    for todo in todos:
        if currentFile != todo.file:
            currentFile = todo.file
            print(f"\n📁 {todo.file}")
            print("-" * (len(todo.file) + 4))
        
        priority_str = f" [{todo.priority.upper()}]" if showPriority and todo.priority != 'normal' else ""
        print(f"  {todo.line:4d} | {todo.tag}{priority_str}: {todo.content}")

def _displayTodosByTag(todos: List[TodoItem], showPriority: bool) -> None:
    """Display todos grouped by tag."""
    tagGroups: Dict[str, List[TodoItem]] = {}
    for todo in todos:
        tagGroups.setdefault(todo.tag, []).append(todo)
    
    for tag, items in sorted(tagGroups.items()):
        print(f"\n🏷️  {tag} ({len(items)} items)")
        print("-" * (len(tag) + 10))
        for todo in items:
            priority_str = f" [{todo.priority.upper()}]" if showPriority and todo.priority != 'normal' else ""
            print(f"  {todo.file}:{todo.line}{priority_str}: {todo.content}")

def _displayTodosByPriority(todos: List[TodoItem], showPriority: bool) -> None:
    """Display todos grouped by priority."""
    priorityGroups: Dict[str, List[TodoItem]] = {}
    for todo in todos:
        priorityGroups.setdefault(todo.priority, []).append(todo)
    
    # Order by priority
    priorityOrder = ['high', 'medium', 'normal', 'low']
    for priority in priorityOrder:
        if priority in priorityGroups:
            items = priorityGroups[priority]
            emoji = {'high': '🔴', 'medium': '🟡', 'normal': '🔵', 'low': '⚪'}[priority]
            print(f"\n{emoji} {priority.upper()} PRIORITY ({len(items)} items)")
            print("-" * (len(priority) + 20))
            for todo in items:
                print(f"  {todo.file}:{todo.line} | {todo.tag}: {todo.content}")

def _displayTodosList(todos: List[TodoItem], showPriority: bool) -> None:
    """Display todos as a simple list."""
    for todo in todos:
        priority_str = f" [{todo.priority.upper()}]" if showPriority and todo.priority != 'normal' else ""
        print(f"{todo.file}:{todo.line} | {todo.tag}{priority_str}: {todo.content}")

def codeStats() -> None:
    """Display code statistics for the project."""
    print("📊 Code Statistics")
    print("=" * 20)
    
    projectFiles = directoryMapper(userProjectPath)
    
    # Count files by extension
    extensionCounts: Dict[str, int] = {}
    totalLines = 0
    totalFiles = 0
    totalSize = 0
    
    codeExtensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp', '.cs'}
    
    for file in projectFiles:
        if file.is_file():
            ext = file.suffix.lower()
            extensionCounts[ext] = extensionCounts.get(ext, 0) + 1
            totalFiles += 1
            
            try:
                size = file.stat().st_size
                totalSize += size
                
                if ext in codeExtensions:
                    content = file.read_text(encoding='utf-8', errors='ignore')
                    lines = len(content.splitlines())
                    totalLines += lines
            except (PermissionError, UnicodeDecodeError):
                continue
    
    print(f"Total Files: {totalFiles}")
    print(f"Total Size: {totalSize / 1024:.1f} KB")
    print(f"Total Lines of Code: {totalLines:,}")
    print()
    
    # Display top file types
    print("File Types:")
    sortedExts = sorted(extensionCounts.items(), key=lambda x: x[1], reverse=True)[:10]
    for ext, count in sortedExts:
        ext_display = ext if ext else "(no extension)"
        print(f"  {ext_display:<15} {count:>5} files")

def miniGames() -> None:
    """Fun mini-games for developers."""
    games = [
        ("🎯 Number Guessing Game", numberGuessingGame),
        ("🎲 Dice Roll", diceRoll),
        ("🔮 Magic 8-Ball", magic8Ball),
        ("💭 Random Programming Quote", programmingQuote),
        ("🎪 Code Fact", randomCodeFact),
    ]
    
    print("\n🎮 Available Mini-Games:")
    for i, (name, _) in enumerate(games, 1):
        print(f"  {i}. {name}")
    
    try:
        choice = input("\nChoose a game (1-5, or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            return
        
        gameIndex = int(choice) - 1
        if 0 <= gameIndex < len(games):
            print()
            games[gameIndex][1]()
        else:
            print("Invalid choice!")
    except (ValueError, KeyboardInterrupt):
        print("Invalid input or cancelled.")

def numberGuessingGame() -> None:
    """Simple number guessing game."""
    number = random.randint(1, 100)
    attempts = 0
    
    print("🎯 Guess the number between 1 and 100!")
    
    while True:
        try:
            guess = int(input("Your guess: "))
            attempts += 1
            
            if guess == number:
                print(f"🎉 Congratulations! You got it in {attempts} attempts!")
                break
            elif guess < number:
                print("📈 Higher!")
            else:
                print("📉 Lower!")
                
        except (ValueError, KeyboardInterrupt):
            print("Game cancelled.")
            break

def diceRoll() -> None:
    """Roll virtual dice."""
    try:
        sides = input("How many sides on the dice? (default: 6): ").strip()
        sides = int(sides) if sides else 6
        
        count = input("How many dice? (default: 1): ").strip()
        count = int(count) if count else 1
        
        print(f"\n🎲 Rolling {count} {sides}-sided dice...")
        time.sleep(1)
        
        results = [random.randint(1, sides) for _ in range(count)]
        
        if count == 1:
            print(f"Result: {results[0]}")
        else:
            print(f"Results: {', '.join(map(str, results))}")
            print(f"Total: {sum(results)}")
            
    except ValueError:
        print("Invalid input!")

def magic8Ball() -> None:
    """Magic 8-ball responses."""
    responses = [
        "It is certain", "Reply hazy, try again", "Don't count on it",
        "It is decidedly so", "Ask again later", "My reply is no",
        "Without a doubt", "Better not tell you now", "My sources say no",
        "Yes definitely", "Cannot predict now", "Outlook not so good",
        "You may rely on it", "Concentrate and ask again", "Very doubtful",
        "As I see it, yes", "Most likely", "Outlook good",
        "Yes", "Signs point to yes"
    ]
    
    question = input("🔮 Ask the Magic 8-Ball a question: ").strip()
    if question:
        print(f"\n🎱 {random.choice(responses)}")
    else:
        print("You need to ask a question!")

def programmingQuote() -> None:
    """Display a random programming quote."""
    quotes = [
        ("Programs must be written for people to read, and only incidentally for machines to execute.", "Harold Abelson"),
        ("Talk is cheap. Show me the code.", "Linus Torvalds"),
        ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
        ("Any fool can write code that a computer can understand. Good programmers write code that humans can understand.", "Martin Fowler"),
        ("First, solve the problem. Then, write the code.", "John Johnson"),
        ("Experience is the name everyone gives to their mistakes.", "Oscar Wilde"),
        ("The best error message is the one that never shows up.", "Thomas Fuchs"),
        ("Debugging is twice as hard as writing the code in the first place.", "Brian Kernighan"),
        ("Code never lies, comments sometimes do.", "Ron Jeffries"),
        ("Simplicity is the ultimate sophistication.", "Leonardo da Vinci"),
    ]
    
    quote, author = random.choice(quotes)
    print(f"💭 \"{quote}\" - {author}")

def randomCodeFact() -> None:
    """Display a random coding fact."""
    facts = [
        "The first computer bug was an actual bug - a moth trapped in a Harvard Mark II computer in 1947.",
        "Python was named after Monty Python's Flying Circus, not the snake.",
        "The term 'debugging' was coined by Admiral Grace Hopper in the 1940s.",
        "JavaScript was created in just 10 days by Brendan Eich in 1995.",
        "The first computer programmer was Ada Lovelace in the 1840s.",
        "Linux was created by a 21-year-old Finnish student named Linus Torvalds.",
        "The '@' symbol in email addresses was chosen by Ray Tomlinson in 1971.",
        "The original name for Java was 'Oak'.",
        "Git was created by Linus Torvalds in just 2 weeks.",
        "The phrase 'Hello, World!' was first used in a C programming tutorial by Brian Kernighan.",
    ]
    
    print(f"🎪 {random.choice(facts)}")

def toolsHandler(args) -> None:
    """Main handler for the tools command."""
    moduleSettings = _loadModuleSettings()
    
    if hasattr(args, 'todo') and args.todo:
        # Handle TODO scanning
        filterTags = []
        if hasattr(args, 'tags') and args.tags:
            filterTags = [tag.lower() for tag in args.tags.split(',')]
        
        includePriority = hasattr(args, 'priority') and args.priority
        groupBy = getattr(args, 'group_by', 'file')
        
        todos = scanTodos(includePriority=includePriority, filterTags=filterTags)
        displayTodos(todos, groupBy=groupBy, showPriority=includePriority)
        
    elif hasattr(args, 'update_dependencies') and args.update_dependencies:
        # Handle dependency updates
        print("🔄 Running dependency update...")
        updateDependencies()
        
    elif hasattr(args, 'stats') and args.stats:
        # Handle code statistics
        codeStats()
        
    elif hasattr(args, 'games') and args.games:
        # Handle mini-games
        miniGames()
        
    else:
        # Show help for tools command
        print("🛠️  pckgr tools - Project utilities")
        print("=" * 35)
        print()
        print("Available tools:")
        print("  --todo                 Scan for TODO items in code")
        print("  --update-dependencies  Update project dependencies")
        print("  --stats               Show code statistics")
        print("  --games               Fun mini-games for developers")
        print()
        print("TODO scanner options:")
        print("  --tags TAGS           Filter by tags (todo,fixme,hack,etc)")
        print("  --priority            Parse and show priority indicators")
        print("  --group-by GROUP      Group by 'file', 'tag', or 'priority'")
        print()
        print("Examples:")
        print("  pckgr tools --todo")
        print("  pckgr tools --todo --tags todo,fixme --priority")
        print("  pckgr tools --todo --group-by priority")
        print("  pckgr tools --stats")
        print("  pckgr tools --games")
