#!/usr/bin/env python3

from jira_dev_tools import JiraClient, JiraCache
from jira_dev_tools.utils import extract_key_from_input
import click
import sys
import os
from typing import List, Dict, Optional, Tuple
from rich.console import Console

# Set up the console for output
console = Console()
error_console = Console(stderr=True)

cache = JiraCache(os.path.join(os.getenv("HOME"), ".cache", "jira_info.json"))
jira_client = JiraClient(cache)

def get_issue_info(issue: str, fresh: bool = False) -> Optional[Dict]:
	"""Get Jira issue information with caching"""
	issue_key = extract_key_from_input(issue)
	if not issue_key:
		return None

	# Fetch from Jira if not in cache
	try:
		return jira_client.get_issue_info(issue_key, fresh)
	except Exception as e:
		error_console.print(f"Error fetching {issue_key}: {str(e)}")
		return None

def parse_line(line: str) -> Tuple[str, bool]:
	"""Parse a line of input to extract issue key and highlight status"""
	highlight_worthy = line.startswith("*")
	issue_text = line[1:].strip() if highlight_worthy else line.strip()
	return issue_text, highlight_worthy

def format_issue(issue: str, issue_info: Optional[Dict], show_status: bool = False, highlight_worthy: bool = False, separator: str = ': ') -> str:
	# append part: issue input
	parts = [f"[green]{issue}[/]" if highlight_worthy else issue]

	# If no issue_info is provided return the parts here.
	if not issue_info:
		return parts.pop()

	# append part: status
	if show_status:
		status_color = "yellow" if issue_info['status'].upper() != "DONE" else "green"
		parts.append(f"[{status_color}]{issue_info['status']}[/]")

	# append part: title
	parts.append(f"[cyan]{issue_info['title']}[/]")

	return separator.join(parts)

def process_issue(issue, show_status: bool = False, fresh: bool = False, separator: str = ': '):
	"""Process a single line of input"""
	try:
		# Parse the line
		issue_text, highlight_worthy = parse_line(issue)

		# Get issue information
		issue_info = get_issue_info(issue_text, fresh)

		# Format and print
		output = format_issue(issue_text, issue_info, show_status, highlight_worthy, separator)
		console.print(output, highlight=False)
	except Exception as e:
		# Write error to stderr and return simple output for stdout
		error_console.print(f"{issue}: {str(e)}", style="red", highlight=False)

@click.command()
@click.argument('issues', nargs=-1)
@click.option('--status', '-s', is_flag=True, help='Show ticket status')
@click.option('--fresh', is_flag=True, help='Force fresh data')
@click.option('--plain', '-p', is_flag=True, help='Plain output')
@click.option('--separator', default=": ", help='Separator for output')
def main(issues: List[str], status: bool, fresh: bool, plain: bool, separator: str):
	"""
	Display Jira ticket information.

	Pass ticket IDs as arguments or pipe input.
	"""
	# Override console if plain output is requested
	if plain:
		global console
		console = Console(highlight=False, color_system=None)

	try:
		# Process stdin if no arguments and stdin is available
		if not issues and not sys.stdin.isatty():
			for line in sys.stdin:
				if line.strip():
					process_issue(line.strip(), status, fresh, separator)
		# Process explicit issues
		elif issues:
			for issue in issues:
				process_issue(issue, status, fresh, separator)
		# Show usage if no input
		else:
			error_console.print("No input provided. Pipe data or provide issue keys.")
			error_console.print("Example: git branch | jira-titles")
			sys.exit(1)

	except KeyboardInterrupt:
		# Handle Ctrl+C gracefully
		sys.exit(130)  # 128 + SIGINT(2)
	except Exception as e:
		error_console.print(f"Error: {str(e)}", style="red")
		sys.exit(1)

if __name__ == "__main__":
	main()
