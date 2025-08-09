"""
Error codes registry for pckgr using noexcept.

This module defines all numbered error codes used throughout the pckgr package
and initializes them with the noexcept system.
"""

from noexcept import no

# Initialize error codes registry
def initializeErrorCodes():
    """Initialize all pckgr error codes with noexcept."""
    
    # File System Errors (100-199)
    no.likey(100, "File not found")
    no.likey(101, "Permission denied accessing file")
    no.likey(102, "Invalid file path")
    no.likey(103, "File already exists")
    no.likey(104, "Directory not found")
    no.likey(105, "Cannot create directory")
    no.likey(106, "File read error")
    no.likey(107, "File write error")
    no.likey(108, "Invalid file encoding")
    no.likey(109, "File is empty")
    no.likey(110, "File too large")
    
    # Git/Version Control Errors (200-299)
    no.likey(200, "Git repository not found")
    no.likey(201, "Git command failed")
    no.likey(202, "Remote repository not accessible")
    no.likey(203, "Branch does not exist")
    no.likey(204, "No commits found")
    no.likey(205, "Merge conflict detected")
    no.likey(206, "Invalid git configuration")
    no.likey(207, "Push operation failed")
    no.likey(208, "Pull operation failed")
    no.likey(209, "Patch application failed")
    no.likey(210, "Tag operation failed")
    
    # Package Management Errors (300-399)
    no.likey(300, "Package not found")
    no.likey(301, "Dependency resolution failed")
    no.likey(302, "Virtual environment not found")
    no.likey(303, "Package installation failed")
    no.likey(304, "Package uninstallation failed")
    no.likey(305, "Invalid package name")
    no.likey(306, "Version conflict detected")
    no.likey(307, "Requirements file not found")
    no.likey(308, "Invalid dependency specification")
    no.likey(309, "Build system error")
    no.likey(310, "Upload to PyPI failed")
    
    # Configuration Errors (400-499)
    no.likey(400, "Invalid configuration")
    no.likey(401, "Configuration file not found")
    no.likey(402, "Configuration parsing error")
    no.likey(403, "Missing required configuration")
    no.likey(404, "Invalid configuration value")
    no.likey(405, "Configuration write error")
    no.likey(406, "Settings validation failed")
    no.likey(407, "Environment variable not set")
    no.likey(408, "Invalid author information")
    no.likey(409, "License validation failed")
    
    # User Input Errors (500-599)
    no.likey(500, "Invalid user input")
    no.likey(501, "Input validation failed")
    no.likey(502, "User cancelled operation")
    no.likey(503, "Maximum attempts exceeded")
    no.likey(504, "Invalid email format")
    no.likey(505, "Invalid GitHub username")
    no.likey(506, "Invalid version format")
    no.likey(507, "Invalid choice selection")
    no.likey(508, "Path validation failed")
    no.likey(509, "Input timeout")
    
    # Project Structure Errors (600-699)
    no.likey(600, "Invalid project structure")
    no.likey(601, "pyproject.toml not found")
    no.likey(602, "setup.py parsing error")
    no.likey(603, "Invalid package layout")
    no.likey(604, "Missing source directory")
    no.likey(605, "Invalid module structure")
    no.likey(606, "Circular dependency detected")
    no.likey(607, "AST parsing failed")
    no.likey(608, "Import resolution failed")
    no.likey(609, "Standard library detection failed")
    
    # Build and Distribution Errors (700-799)
    no.likey(700, "Build process failed")
    no.likey(701, "Test execution failed")
    no.likey(702, "Linting failed")
    no.likey(703, "Type checking failed")
    no.likey(704, "Documentation build failed")
    no.likey(705, "Distribution creation failed")
    no.likey(706, "Release process failed")
    no.likey(707, "Version bumping failed")
    no.likey(708, "Changelog generation failed")
    no.likey(709, "Metadata validation failed")
    
    # Network and External Service Errors (800-899)
    no.likey(800, "Network connection failed")
    no.likey(801, "API request failed")
    no.likey(802, "Authentication failed")
    no.likey(803, "Rate limit exceeded")
    no.likey(804, "Service unavailable")
    no.likey(805, "Invalid API response")
    no.likey(806, "Timeout occurred")
    no.likey(807, "SSL/TLS error")
    no.likey(808, "Proxy configuration error")
    no.likey(809, "DNS resolution failed")
    
    # CLI and User Interface Errors (900-999)
    no.likey(900, "Invalid command line arguments")
    no.likey(901, "Command not found")
    no.likey(902, "Subcommand execution failed")
    no.likey(903, "Help system error")
    no.likey(904, "Terminal interaction failed")
    no.likey(905, "Progress tracking failed")
    no.likey(906, "Output formatting error")
    no.likey(907, "Color rendering failed")
    no.likey(908, "Interactive mode error")
    no.likey(909, "CLI initialization failed")
    
    # Soft Errors (1000-1099) - For warnings and recoverable issues
    no.likey(1000, "Deprecation warning", soft=True)
    no.likey(1001, "Performance warning", soft=True)
    no.likey(1002, "Security warning", soft=True)
    no.likey(1003, "Compatibility warning", soft=True)
    no.likey(1004, "Configuration warning", soft=True)
    no.likey(1005, "Missing optional dependency", soft=True)
    no.likey(1006, "Cache invalidation warning", soft=True)
    no.likey(1007, "Fallback mechanism used", soft=True)
    no.likey(1008, "Resource usage warning", soft=True)
    no.likey(1009, "Update available notification", soft=True)

# Error code constants for easy reference
class ErrorCodes:
    """Constants for all pckgr error codes."""
    
    # File System
    FILE_NOT_FOUND = 100
    PERMISSION_DENIED = 101
    INVALID_FILE_PATH = 102
    FILE_EXISTS = 103
    DIRECTORY_NOT_FOUND = 104
    CANNOT_CREATE_DIRECTORY = 105
    FILE_READ_ERROR = 106
    FILE_WRITE_ERROR = 107
    INVALID_FILE_ENCODING = 108
    FILE_EMPTY = 109
    FILE_TOO_LARGE = 110
    
    # Git/Version Control
    GIT_REPO_NOT_FOUND = 200
    GIT_COMMAND_FAILED = 201
    REMOTE_NOT_ACCESSIBLE = 202
    BRANCH_NOT_EXISTS = 203
    NO_COMMITS_FOUND = 204
    MERGE_CONFLICT = 205
    INVALID_GIT_CONFIG = 206
    PUSH_FAILED = 207
    PULL_FAILED = 208
    PATCH_FAILED = 209
    TAG_FAILED = 210
    
    # Package Management
    PACKAGE_NOT_FOUND = 300
    DEPENDENCY_RESOLUTION_FAILED = 301
    VENV_NOT_FOUND = 302
    PACKAGE_INSTALL_FAILED = 303
    PACKAGE_UNINSTALL_FAILED = 304
    INVALID_PACKAGE_NAME = 305
    VERSION_CONFLICT = 306
    REQUIREMENTS_NOT_FOUND = 307
    INVALID_DEPENDENCY_SPEC = 308
    BUILD_SYSTEM_ERROR = 309
    UPLOAD_FAILED = 310
    
    # Configuration
    INVALID_CONFIG = 400
    CONFIG_NOT_FOUND = 401
    CONFIG_PARSE_ERROR = 402
    MISSING_REQUIRED_CONFIG = 403
    INVALID_CONFIG_VALUE = 404
    CONFIG_WRITE_ERROR = 405
    SETTINGS_VALIDATION_FAILED = 406
    ENV_VAR_NOT_SET = 407
    INVALID_AUTHOR_INFO = 408
    LICENSE_VALIDATION_FAILED = 409
    
    # User Input
    INVALID_INPUT = 500
    INPUT_VALIDATION_FAILED = 501
    USER_CANCELLED = 502
    MAX_ATTEMPTS_EXCEEDED = 503
    INVALID_EMAIL = 504
    INVALID_GITHUB_USERNAME = 505
    INVALID_VERSION = 506
    INVALID_CHOICE = 507
    PATH_VALIDATION_FAILED = 508
    INPUT_TIMEOUT = 509
    
    # Project Structure
    INVALID_PROJECT_STRUCTURE = 600
    PYPROJECT_NOT_FOUND = 601
    SETUP_PARSE_ERROR = 602
    INVALID_PACKAGE_LAYOUT = 603
    MISSING_SOURCE_DIR = 604
    INVALID_MODULE_STRUCTURE = 605
    CIRCULAR_DEPENDENCY = 606
    AST_PARSE_FAILED = 607
    IMPORT_RESOLUTION_FAILED = 608
    STDLIB_DETECTION_FAILED = 609
    
    # Build and Distribution
    BUILD_FAILED = 700
    TEST_FAILED = 701
    LINTING_FAILED = 702
    TYPE_CHECK_FAILED = 703
    DOCS_BUILD_FAILED = 704
    DIST_CREATION_FAILED = 705
    RELEASE_FAILED = 706
    VERSION_BUMP_FAILED = 707
    CHANGELOG_FAILED = 708
    METADATA_VALIDATION_FAILED = 709
    
    # Network and External Services
    NETWORK_FAILED = 800
    API_REQUEST_FAILED = 801
    AUTH_FAILED = 802
    RATE_LIMIT_EXCEEDED = 803
    SERVICE_UNAVAILABLE = 804
    INVALID_API_RESPONSE = 805
    TIMEOUT = 806
    SSL_ERROR = 807
    PROXY_ERROR = 808
    DNS_FAILED = 809
    
    # CLI and User Interface
    INVALID_CLI_ARGS = 900
    COMMAND_NOT_FOUND = 901
    SUBCOMMAND_FAILED = 902
    HELP_SYSTEM_ERROR = 903
    TERMINAL_INTERACTION_FAILED = 904
    PROGRESS_TRACKING_FAILED = 905
    OUTPUT_FORMAT_ERROR = 906
    COLOR_RENDER_FAILED = 907
    INTERACTIVE_MODE_ERROR = 908
    CLI_INIT_FAILED = 909
    
    # Soft Errors (Warnings)
    DEPRECATION_WARNING = 1000
    PERFORMANCE_WARNING = 1001
    SECURITY_WARNING = 1002
    COMPATIBILITY_WARNING = 1003
    CONFIG_WARNING = 1004
    MISSING_OPTIONAL_DEP = 1005
    CACHE_INVALIDATION_WARNING = 1006
    FALLBACK_USED = 1007
    RESOURCE_WARNING = 1008
    UPDATE_AVAILABLE = 1009

# Initialize error codes when module is imported
initializeErrorCodes()
