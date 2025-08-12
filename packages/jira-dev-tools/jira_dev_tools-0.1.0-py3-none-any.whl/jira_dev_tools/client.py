#!/usr/bin/env python3

from jira import JIRA
from .utils import extract_key_from_input
import click
import os
import json
import sys
import redis
from rich.console import Console
from typing import Dict, Any, Optional
from pathlib import Path

console = Console()
error_console = Console(stderr=True)

def load_config():
    """Load configuration from various sources in priority order"""
    # Default config
    config = {
        "JIRA_DOMAIN": None,
        "JIRA_USERNAME": None,
        "JIRA_API_TOKEN": None,
        "REDIS_HOST": "localhost",
        "REDIS_PORT": 6379,
        "JIRA_CACHE_EXPIRE": 864000,
    }
    
    # Check for config file in user's home directory
    config_file = Path.home() / ".config/jira-dev-tools/.credentials.json"
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    
    # Environment variables override file config
    for key in config:
        if key in os.environ:
            config[key] = os.environ[key]
    
    # Convert port to int if it's a string
    if isinstance(config["REDIS_PORT"], str):
        config["REDIS_PORT"] = int(config["REDIS_PORT"])
    
    return config

# Configuration
DEFAULT_CACHE_PATH = os.path.join(os.getenv("HOME", ""), ".cache", "jira_info.json")

class JiraCache:
    """Cache for Jira issue information using Redis or file storage"""

    def __init__(self, path: str = DEFAULT_CACHE_PATH):
        self._config = load_config()
        self._path = path
        self._redis = None
        self._file_cache = {}
        self.type = self._initialize_cache()

    def _initialize_cache(self) -> str:
        """Initialize the cache backend"""
        # Try Redis first
        try:
            self._redis = redis.Redis(
                host=self._config["REDIS_HOST"],
                port=self._config["REDIS_PORT"],
                decode_responses=True
            )
            self._redis.ping()
            return 'redis'
        except redis.exceptions.ConnectionError:
            # Fall back to file cache
            try:
                os.makedirs(os.path.dirname(self._path), exist_ok=True)
                if os.path.exists(self._path):
                    with open(self._path, 'r') as f:
                        self._file_cache = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                self._file_cache = {}
            return 'file'
        except Exception as e:
            sys.stderr.write(f"Cache initialization error: {e}\n")
            return 'memory'

    def update(self, key: str, value: Dict[str, Any]) -> None:
        """Update cache with new value (alias for set)"""
        self.set(key, value)

    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Set a value in the cache"""
        if self.type == 'redis':
            try:
                self._redis.hset(f'jira-info:{key}', mapping=value)
                self._redis.expire(f'jira-info:{key}', self._config["JIRA_CACHE_EXPIRE"])
            except Exception as e:
                sys.stderr.write(f"Redis cache error: {e}\n")
        else:
            self._file_cache[key] = value
            try:
                with open(self._path, 'w') as file:
                    json.dump(self._file_cache, file)
            except Exception as e:
                sys.stderr.write(f"File cache write error: {e}\n")

    def get(self, key, default=None):
        """Get a value from the cache"""
        if self.type == 'redis':
            try:
                result = self._redis.hgetall(f'jira-info:{key}')
                return result if result else default
            except Exception as e:
                sys.stderr.write(f"Redis cache read error: {e}\n")
                return default
        else:
            return self._file_cache.get(key, default)

class JiraClient:
    """Client for interacting with Jira API"""

    def __init__(self, cache: Optional[JiraCache] = None):
        config = load_config()

        # Validate configuration
        if not all([config["JIRA_DOMAIN"], config["JIRA_USERNAME"], config["JIRA_API_TOKEN"]]):
            raise ValueError(
                "Missing Jira configuration. Please set JIRA_DOMAIN, "
                "JIRA_USERNAME, and JIRA_API_TOKEN environment variables."
            )

        try:
            self.jira = JIRA(f'https://{config["JIRA_DOMAIN"]}', basic_auth=(config["JIRA_USERNAME"], config["JIRA_API_TOKEN"]))
            # Verify connection (optional but good practice)
            self.jira.myself()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Jira: {e}") from e

        self.cache = cache or JiraCache()

    def get_issue_info(self, issue_key: str, fresh: bool = False) -> Dict[str, Any]:
        """Get information about a Jira issue"""
        issue = None
        info = None
        if not fresh:
            issue = self.cache.get(issue_key)
            if issue:  # Check if issue is in cache
                info = {
                    'key': issue.get('key', issue_key),
                    'title': issue.get('title', ''),
                    'type': issue.get('type', ''),
                    'status': issue.get('status', ''),
                    'issuetype': issue.get('issuetype', ''),
                    'assignee': issue.get('assignee', ''),
                }
        # Fetch issue from Jira
        if not issue:
            issue = self.jira.issue(issue_key, fields='summary,issuetype,status,description,comment,issuelinks,parent,resolution,assignee,subtasks,reporter,progress')
            # Extract relevant information
            info = {
                'key': issue.key,
                'title': issue.fields.summary,
                'type': issue.fields.issuetype.name,
                'status': issue.fields.status.name,
                'issuetype': issue.fields.issuetype.name,
                'assignee': issue.fields.assignee.displayName if issue.fields.assignee else '',
            }
        self.cache.update(issue_key, info)

        return info

@click.command()
@click.argument('issue_keys', nargs=-1)
# optional argument to read from stdin
@click.option('--fresh', is_flag=True, help="Force fresh data retrieval")
def main(issue_keys: list[str], fresh: bool = False):
    """Command-line interface for jira_info"""
    try:
        client = JiraClient()
        if not issue_keys and not sys.stdin.isatty():
            issue_keys = [line.strip() for line in sys.stdin if line.strip()]

        if len(issue_keys) > 0:
            for issue_text in issue_keys:
                issue = issue_text.strip()
                if issue:
                    process_and_print_issue(client, issue, fresh)

    except Exception as e:
        error_console.print(f"Error: {str(e)}")
        sys.exit(1)

def process_and_print_issue(client: JiraClient, issue: str, fresh: bool):
    """Process a single issue and print the formatted output"""
    try:
        issue_key = extract_key_from_input(issue)
        if not issue_key:
            return None

        issue_info = client.get_issue_info(issue_key, fresh)
        if not issue_info:
            error_console.print(f"Could not retrieve info for {issue_info['key']}")
            return

        json.dump(issue_info, sys.stdout)
        sys.stdout.write('\n')

    except Exception as e:
        error_console.print(f"Error processing {issue}: {str(e)}", style="red", highlight=False)

if __name__ == "__main__":
    main()
