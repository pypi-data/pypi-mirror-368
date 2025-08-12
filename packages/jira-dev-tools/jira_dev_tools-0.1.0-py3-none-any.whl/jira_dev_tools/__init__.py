"""Jira information retrieval tool."""

__version__ = "0.1.0"

# Import and expose the main classes
from .client import JiraClient, JiraCache

# This makes them available when someone does:
# from jira_dev_tools import JiraClient, JiraCache
