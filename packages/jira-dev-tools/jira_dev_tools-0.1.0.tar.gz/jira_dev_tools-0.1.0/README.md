> [!NOTE]
> This is still a work in progress and considered in beta. I built this as a fun project to learn python (also bash in parallel)

Jira Tools
A command-line toolkit for retrieving and displaying Jira ticket information.

Installation
Install using pipx (recommended):

```bash
cd /path/to/jira-dev-tools
pipx install .

jira_init
```

This makes the commands available globally without needing to activate any virtual environment.

# Configuration
`jira_init` command walks you through the creation of this credentials.json file
Create a configuration file at `~/.config/.credentials.json` with your Jira credentials:

```json
{
  "JIRA_DOMAIN": "your-domain.atlassian.net",
  "JIRA_USERNAME": "your-email@example.com",
  "JIRA_API_TOKEN": "your-api-token",
  "REDIS_HOST": "localhost",
  "REDIS_PORT": 6379,
  "JIRA_CACHE_EXPIRE": 864000
}
```

Optionally change file permissions to restrict access by other users

```bash
chmod 600 ~/.config/jira-dev-tools/.credentials.json
```

# Available Commands

## jira_init

Initialize the credentials. Prompts for the necessary jira values.

```bash
jira_init
```

## jira_titles

Display Jira ticket titles and optionally their status.

```bash
# Basic usage - show ticket titles
jira_titles ABC-123 DEF-456

# Show ticket titles with status
jira_titles --status ABC-123 DEF-456

# Force fresh data retrieval (bypass cache)
jira_titles --fresh ABC-123

# Plain output (no colors or formatting)
jira_titles --plain ABC-123

# Customize the separator between ticket ID and title
# Default is tab `\t`
jira_titles --separator " | " ABC-123

# Combine options
jira_titles --status --plain --separator ": " ABC-123 DEF-456

# Pipe ticket IDs from another command
git log --oneline | grep -o '[A-Z]\+-[0-9]\+' | jira_titles --status
```

## jira_info

Retrieve detailed JSON information about Jira tickets.

```bash
# Get information about a single issue
jira_info ABC-123

# Get information about multiple issues
jira_info ABC-123 DEF-456

# Force fresh data retrieval (bypass cache)
jira_info --fresh ABC-123

# Pipe issue keys from another command
git log --oneline | grep -o '[A-Z]\+-[0-9]\+' | jira_info
```

# Features

- Fast retrieval: Gets ticket information directly from Jira API
- Caching: Caches results to minimize API calls (Redis if available, otherwise local file)
- Flexible input: Accept ticket IDs as arguments or via stdin (pipe)
- Formatting options: Customize output format for integration with other tools
- JSON output: `jira_info` provides structured JSON output for scripting

# Examples

## Show tickets mentioned in recent commits

```bash
git log --oneline -n 10 | grep -o '[A-Z]\+-[0-9]\+' | sort -u | jira_titles --status
```

## Create a report of all tickets in the current branch

```bash
git log main..HEAD --oneline | grep -o '[A-Z]\+-[0-9]\+' | sort -u | jira_titles > branch-tickets.txt
```

## Get detailed information about a ticket and process with jq

```bash
jira_info ABC-123 | jq '.status'
```

# Shell function examples

You can add the following shell functions to your `.bashrc` or `.zshrc` to simplify usage:

## Print Jira titles for all branches (only branches starting with jira ticket IDs will include titles)

```bash
git_branches_with_jira_titles() {
    git branch | jira_titles --status
}
```

## Commit with Jira title

```bash
git_commit_jira_title() {
    local branch
    branch=${1:-$(git rev-parse --abbrev-ref HEAD)}
    if [[ -z "$branch" ]]; then
        echo "Not on a branch" >&2
        return 1
    fi
    local jira_title
    jira_title=$(jira_titles "$branch")
    if [[ -z "$jira_title" ]]; then
        echo "No Jira title found for branch $branch" >&2
        return 1
    fi
    git commit -m "$jira_title" -e -v
}
```

## Create a GitHub Pull Request with Jira information

This function creates a GitHub Pull Request using the current branch's Jira ticket information.
It requires the `gh` CLI tool to be installed and authenticated.

```bash
gh_pr_create() {
    IFS=$'\t' read -r jira_key jira_title jira_issuetype < <(jira_info $(git rev-parse --abbrev-ref HEAD) | jq -r '[.key, .title, .issuetype] | @tsv' 2>/dev/null)
    local jira_label
    if [[ -z $jira_key ]]; then
        print -u2 "Error: Failed to retrieve or parse Jira info for $(git rev-parse --abbrev-ref HEAD)."
        return 1
    fi

    jira_issuetype="$(echo "${jira_issuetype}" | awk '{print tolower($0)}')"
    case "${jira_issuetype}" in
        "technical story")
            jira_label="tech-story"
            ;;
        "user story")
            jira_label="user-story"
            ;;
        "bug")
            jira_label="bug"
            ;;
    esac

    local -a gh_args=()

    if [[ -n "$jira_label" ]]; then
        gh_args+=('--label' "$jira_label")
    fi

    gh_args+=('--label' 'other-label-example')  # Add any other labels you want
    gh_args+=('--title' "$jira_key: $jira_title")
    gh_args+=('-T' 'PULL_REQUEST_TEMPLATE.md')
    gh_args+=("$@")

    gh pr create "${gh_args[@]}"
}
```

Example usage:

```bash
gh_pr_create --draft --editor
```

# Uninstallation

To uninstall the tool, run:

```bash
pipx uninstall jira-dev-tools
```

# Updating

After making changes to the code, update your installation with:

```bash
pipx upgrade jira-dev-tools
```

# Troubleshooting

## Missing Configuration

If you see an error about missing Jira configuration, make sure your `~/.config/.jira-dev-tools.json` file exists and has the correct permissions.

## API Rate Limiting

If you encounter rate limiting from Jira's API, the tool will use cached data when available. Use the `--fresh` flag only when necessary.

## Cache Issues

To clear the cache:

```bash
rm ~/.cache/jira_info.json
```

Or if using Redis:

```bash
redis-cli KEYS "jira-info:*" | xargs redis-cli DEL
```

# Development

To contribute to this tool:

1. Clone the repository
2. Install in development mode:

```bash
cd /path/to/jira-dev-tools
pip install -e .
```

3. Make your changes
4. Test thoroughly
5. Submit a pull request

# License

MIT
# jira-dev-tools
