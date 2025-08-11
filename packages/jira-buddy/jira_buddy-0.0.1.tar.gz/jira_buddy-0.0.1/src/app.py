import sys
import json
import requests
from requests.auth import HTTPBasicAuth
import os
import argparse


def load_config():
    config_file = os.path.expanduser("~/.jiraconfig")
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                return {
                    "jira_url": config.get("url"),
                    "username": config.get("username"),
                    "api_token": config.get("api_token"),
                    "project": config.get("project")
                }
        except Exception as e:
            print(f"Error reading config file: {e}")
            sys.exit(1)
    else:
        print("Configuration file not found. Please create ~/.jiraconfig.")
        sys.exit(1)


def get_assignee_name(assignee):
    if not assignee:
        return "Unassigned"
    return assignee.get("displayName", assignee.get("name", "Unknown"))


def truncate_text(text, max_length=100):
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def format_results(issues, config):
    results = []

    issues.sort(
        key=lambda x: (
            x.get("fields", {}).get("issuetype", {}).get("name", ""),
            x.get("key", ""),
        )
    )

    for issue in issues:
        fields = issue.get("fields", {})

        ticket = {
            "key": issue.get("key", "UNKNOWN"),
            "summary": fields.get("summary", "No summary"),
            "description": truncate_text(fields.get("description", "")),
            "status": fields.get("status", {}).get("name", "Unknown"),
            "priority": fields.get("priority", {}).get("name", "Unknown"),
            "issuetype": fields.get("issuetype", {}).get("name", "Unknown"),
            "assignee": get_assignee_name(fields.get("assignee")),
            "assignedToMe": fields.get("assignee") and fields.get("assignee", {}).get("emailAddress") == config["username"],
            "url": f"{config['jira_url']}/browse/{issue.get('key', '')}",
        }

        results.append(ticket)

    return results


def search_tickets(config, search_term, max_results=50, own_only=False):
    jql_parts = []
    if search_term:
        jql_parts = [f'text ~ "{search_term}" OR summary ~ "{search_term}"']

    if config.get("project"):
        jql_parts.append(f'project = "{config["project"]}"')

    if own_only:
        jql_parts.append(f'assignee = "{config["username"]}"')

    jql_parts.append('status != "Canceled"')
    jql_parts.append('status != "Done"')

    jql = " AND ".join([f"({part})" for part in jql_parts])

    url = f"{config['jira_url']}/rest/api/3/search/jql"

    params = {
        "jql": jql,
        "maxResults": max_results,
        "fields": "key,summary,description,status,assignee,priority,issuetype,project",
    }

    try:
        response = requests.get(
            url,
            params=params,
            auth=HTTPBasicAuth(config["username"], config["api_token"]),
            headers={"Accept": "application/json"},
            timeout=30,
        )

        if response.status_code == 401:
            print("Authentication failed. Check username and API token.")
            return []
        elif response.status_code != 200:
            print(
                f"JIRA API error: {response.status_code} - {response.text}"
            )
            return []

        data = response.json()
        return format_results(data.get("issues", []), config)

    except requests.exceptions.Timeout:
        print("Request timed out")
        return []
    except requests.exceptions.ConnectionError:
        print("Connection error. Check JIRA URL.")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def filter_results(results, fields):
    if not fields:
        return results

    filtered_results = []
    for ticket in results:
        filtered_ticket = {}
        for field in fields:
            if field in ticket:
                filtered_ticket[field] = ticket[field]
        filtered_results.append(filtered_ticket)

    return filtered_results


def format_text_output(results, fields=None):
    if not results:
        return "No tickets found."

    if not fields:
        fields = ["key", "summary"]

    output = []
    for ticket in results:
        parts = []
        for field in fields:
            if field in ticket:
                parts.append(str(ticket[field]))
        output.append(": ".join(parts))

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Search JIRA tickets")
    parser.add_argument("search_term", nargs="?", help="Search term to look for in tickets")
    parser.add_argument("--own", action="store_true", help="Filter for only tickets assigned to you")
    parser.add_argument("--json", action="store_true", default=True, help="Output in JSON format (default)")
    parser.add_argument("--text", action="store_true", help="Output in plain text format")
    parser.add_argument("--fields", help="Comma-separated list of fields to include (e.g., key,summary,status)")

    args = parser.parse_args()

    if args.text:
        args.json = False

    fields = None
    if args.fields:
        fields = [field.strip() for field in args.fields.split(",")]
    elif args.text:
        fields = ["key", "summary"]

    config = load_config()
    
    if not all([config["jira_url"], config["username"], config["api_token"]]):
        print(
            "Missing JIRA configuration. Set environment variables or config file."
        )
        sys.exit(1)

    results = search_tickets(config, args.search_term, own_only=args.own)

    filtered_results = filter_results(results, fields)

    if args.text:
        print(format_text_output(filtered_results, fields))
    else:
        print(json.dumps(filtered_results, indent=2))


if __name__ == "__main__":
    main()
