"""File to center all rules related to file type, file extensions and file mappers."""


# Files that belongs to these patters
file_patterns = (
    ".github/workflows/*.yml",
    ".github/workflows/*.yaml",
    ".circleci/config.yml",
    ".circleci/config.yaml",
    ".travis.yml",
    "azure-pipelines*.yml",
    "azure-pipelines*.yaml",
    "noxfile.py",
    "tox.ini",
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "Makefile",
    ".pre-commit-config.yaml",
    "scripts/**/*",
)

# Files that contains some of these keywords in path
keywords = (
    "release", 
    "publish", 
    "bump", 
    "towncrier", 
    "ci", 
    "cd", 
    "deploy"
)

# File type mapper
file_type_mapper = {
    "github_actions": {
        "startswith": (".github/workflows/",),
    },
    "circleci": {
        "equals": (".circleci/config.yml", ".circleci/config.yaml"),
    },
    "travis_ci": {
        "equals": (".travis.yml",),
    },
    "azure_pipelines": {
        "startswith": ("azure-pipelines",),
    },
    "jenkins": {
        "equals": ("jenkinsfile",),
    },
    "pyproject": {
        "endswith": ("pyproject.toml",),
    },
    "setup_cfg": {
        "endswith": ("setup.cfg",),
    },
    "setup_py": {
        "endswith": ("setup.py",),
    },
    "tox_ini": {
        "endswith": ("tox.ini",),
    },
    "noxfile": {
        "endswith": ("noxfile.py",),
    },
    "pre_commit": {
        "endswith": (".pre-commit-config.yaml",),
    },
    "makefile": {
        "endswith": ("makefile",),
    },
    "script": {
        "startswith": ("scripts/",),
    },
    "release_file": {
        "name_contains": ("release", "publish", "bump", "towncrier"),
    },
}

# Discarded files
discarded_files = {
    ".git", 
    ".mypy_cache", 
    ".nox", 
    ".pytest_cache", 
    ".ruff_cache",
    ".tox",
    ".venv",
    "build",
    "dist",
    "venv",
}

# Possible file extensions
possible_file_extensions = {
    "", # Dockerfile, JenkinsFile, Makefile
    ".cfg",
    ".ini",
    ".md", # Include documentation to check for texts that can reveal signals
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

# Workflow file types convenience dict
workflow_file_types = {
    "github_actions",
    "circleci",
    "travis_ci",
    "azure_pipelines",
    "jenkins",
}

