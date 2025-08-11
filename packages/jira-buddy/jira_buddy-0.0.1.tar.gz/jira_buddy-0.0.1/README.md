# JIRA Buddy

A python tool to interact with Jira

## Installation

```bash
uv add .
```

## Configuration

Create a `~/.jiraconfig` file with your JIRA credentials:

```json
{
  "url": "https://your-company.atlassian.net",
  "username": "your-email@company.com",
  "api_token": "your-api-token",
  "project": "PROJECT-KEY"
}
```

To generate an API token, go to: https://id.atlassian.com/manage-profile/security/api-tokens

## Usage

### Search for tickets
```bash
uv run jira-buddy "search term"
```

### Show only your assigned tickets
```bash
uv run jira-buddy --own
```

### Search your assigned tickets
```bash
uv run jira-buddy "search term" --own
```

### Output formats

#### JSON output (default)
```bash
uv run jira-buddy "search term"
uv run jira-buddy "search term" --json
```

#### Text output
```bash
uv run jira-buddy "search term" --text
```

### Field filtering

#### Show only specific fields (JSON)
```bash
uv run jira-buddy "search term" --fields key,summary,status
```

#### Custom text output
```bash
uv run jira-buddy "search term" --text --fields key,assignee,status
```

### Show help
```bash
uv run jira-buddy --help
```
