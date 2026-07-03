import json
import subprocess
import re
import os
from datetime import datetime

def run_gh_command(args):
    env = os.environ.copy()
    if "GITHUB_TOKEN" in env and (not env["GITHUB_TOKEN"] or env["GITHUB_TOKEN"].startswith("gho_")):
        del env["GITHUB_TOKEN"]
    
    gh_path = r"C:\Program Files\GitHub CLI\gh.exe"
    if not os.path.exists(gh_path):
        gh_path = "gh"
        
    cmd = [gh_path] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, encoding="utf-8")
    if result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}\n{result.stderr}")
        return []
    try:
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return []

def clean_body(body, title):
    if not body:
        return title
    # Remove markdown image/link tags like ![image](...)
    body = re.sub(r'!\[.*?\]\(.*?\)', '', body)
    # Remove HTML tags
    body = re.sub(r'<[^>]*>', '', body)
    # Remove markdown headers
    body = re.sub(r'^#+\s+.*$', '', body, flags=re.MULTILINE)
    # Remove checklists like - [x] or - [ ]
    body = re.sub(r'-\s+\[[ xX]\]', '', body)
    # Replace multiple newlines/spaces
    body = re.sub(r'\r\n', '\n', body)
    body = re.sub(r'\n+', '\n', body)
    body = re.sub(r'\s+', ' ', body)
    body = body.strip()
    
    # If cleaned body is too short, fall back to title
    if len(body) < 20:
        return title
    
    # Extract the first few sentences/lines
    sentences = re.split(r'(?<=[.!?])\s+', body)
    summary_sentences = []
    char_count = 0
    for s in sentences:
        if s.strip():
            summary_sentences.append(s.strip())
            char_count += len(s)
            if len(summary_sentences) >= 3 or char_count > 250:
                break
    
    return " ".join(summary_sentences)

def format_date(date_str):
    if not date_str or date_str.startswith("0001-01-01"):
        return "N/A"
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return date_str

def main():
    user = "RedZapdos123"
    exclude_users = ["RedZapdos123", "WhiteMetagross", "Digvijay-x1", "swarupn17", "Paraspandey-debugs", "yenode", "RajanPatil1904", "LevelSilence"]
    
    report = []
    report.append(f'<div align="center">\n  <img src="https://visitor-badge.laobi.icu/badge?page_id={user}.{user}" />\n</div>\n')

    # Exclude self-owned, co-owned, or specified accounts
    def is_excluded(item):
        repo = item.get("repository", {}).get("nameWithOwner", "")
        owner = repo.split("/")[0].lower()
        if owner in {u.lower() for u in exclude_users}:
            return True
        if any(substring in owner for substring in ["digvijay", "swarup", "paraspandey"]):
            return True
        return False

    # 1. Fetch merged PRs
    print(f"Fetching merged PRs for {user}...")
    prs_args = ["search", "prs", "--author", user, "--merged", "--limit", "1000", "--json", "repository,number,title,body,url,createdAt,closedAt"]
    merged_prs = run_gh_command(prs_args)
    if not isinstance(merged_prs, list):
        merged_prs = []
    merged_prs = [p for p in merged_prs if not is_excluded(p)]
    
    # Add co-authored DLT PR
    print("Fetching co-authored DLT PR...")
    coauthored_dlt = run_gh_command(["api", "repos/dlt-hub/dlt/pulls/3851"])
    if coauthored_dlt and isinstance(coauthored_dlt, dict):
        mapped_pr = {
            "body": coauthored_dlt.get("body", ""),
            "closedAt": coauthored_dlt.get("merged_at") or coauthored_dlt.get("closed_at", ""),
            "createdAt": coauthored_dlt.get("created_at", ""),
            "number": coauthored_dlt.get("number"),
            "repository": {
                "name": "dlt",
                "nameWithOwner": "dlt-hub/dlt"
            },
            "title": coauthored_dlt.get("title", "") + " (Co-authored)",
            "url": coauthored_dlt.get("html_url", "")
        }
        if not any(p["number"] == mapped_pr["number"] and p["repository"]["nameWithOwner"] == "dlt-hub/dlt" for p in merged_prs):
            merged_prs.append(mapped_pr)
            
    # Sort merged PRs by closedAt descending
    merged_prs.sort(key=lambda x: x.get("closedAt", ""), reverse=True)

    # 2. Fetch Open PRs
    print(f"Fetching open PRs for {user}...")
    open_prs_args = ["search", "prs", "--author", user, "--state", "open", "--limit", "1000", "--json", "repository,number,title,body,url,createdAt"]
    open_prs = run_gh_command(open_prs_args)
    if not isinstance(open_prs, list):
        open_prs = []
    open_prs = [p for p in open_prs if not is_excluded(p)]
    open_prs.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
    
    # 3. Fetch Opened Issues (Open)
    print(f"Fetching opened issues for {user}...")
    issues_open_args = ["search", "issues", "type:issue", "--author", user, "--state", "open", "--limit", "1000", "--json", "repository,number,title,body,url,createdAt"]
    open_issues = run_gh_command(issues_open_args)
    if not isinstance(open_issues, list):
        open_issues = []
    open_issues = [i for i in open_issues if not is_excluded(i)]
    open_issues.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
    
    # 4. Fetch Closed Issues
    print(f"Fetching closed issues for {user}...")
    issues_closed_args = ["search", "issues", "type:issue", "--author", user, "--state", "closed", "--limit", "1000", "--json", "repository,number,title,body,url,closedAt"]
    closed_issues = run_gh_command(issues_closed_args)
    if not isinstance(closed_issues, list):
        closed_issues = []
    closed_issues = [i for i in closed_issues if not is_excluded(i)]
    closed_issues.sort(key=lambda x: x.get("closedAt", ""), reverse=True)

    # 5. Fetch Triaged Issues
    print(f"Fetching triaged issues for {user}...")
    triaged_args = ["search", "issues", "--commenter", user, "--state", "closed", "--limit", "100", "--json", "repository,number,title,body,url,createdAt,closedAt", "--", f"-author:{user}"]
    triaged_raw = run_gh_command(triaged_args)
    if not isinstance(triaged_raw, list):
        triaged_raw = []
    triaged_issues = [t for t in triaged_raw if not is_excluded(t)]
    triaged_issues.sort(key=lambda x: x.get("closedAt", ""), reverse=True)

    # Format FOSS Pull Requests Section
    report.append("## FOSS Pull Requests\n")
    
    report.append("### Merged Pull Requests\n")
    if merged_prs:
        report.append("| # | Repository | PR | Title | Merged Date | Description |")
        report.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for idx, pr in enumerate(merged_prs, 1):
            repo = pr['repository']['nameWithOwner']
            num = pr['number']
            url = pr['url']
            title = pr['title']
            merged_date = format_date(pr['closedAt'])
            desc = clean_body(pr['body'], title)
            report.append(f"| {idx} | {repo} | [#{num}]({url}) | {title} | {merged_date} | {desc} |")
    else:
        report.append("*No merged pull requests found.*\n")
    report.append("\n")

    report.append("### Open Pull Requests\n")
    if open_prs:
        report.append("| # | Repository | PR | Title | Created Date | Description |")
        report.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for idx, pr in enumerate(open_prs, 1):
            repo = pr['repository']['nameWithOwner']
            num = pr['number']
            url = pr['url']
            title = pr['title']
            created_date = format_date(pr['createdAt'])
            desc = clean_body(pr['body'], title)
            report.append(f"| {idx} | {repo} | [#{num}]({url}) | {title} | {created_date} | {desc} |")
    else:
        report.append("*No open pull requests found.*\n")
    report.append("\n")

    # Format FOSS Issues Authored Section
    report.append("## FOSS Issues Authored\n")

    report.append("### Open Issues\n")
    if open_issues:
        report.append("| # | Repository | Issue | Title | Created Date | Description |")
        report.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for idx, issue in enumerate(open_issues, 1):
            repo = issue['repository']['nameWithOwner']
            num = issue['number']
            url = issue['url']
            title = issue['title']
            created_date = format_date(issue['createdAt'])
            desc = clean_body(issue['body'], title)
            report.append(f"| {idx} | {repo} | [#{num}]({url}) | {title} | {created_date} | {desc} |")
    else:
        report.append("*No open issues found.*\n")
    report.append("\n")

    report.append("### Closed Issues\n")
    if closed_issues:
        report.append("| # | Repository | Issue | Title | Closed Date | Description |")
        report.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for idx, issue in enumerate(closed_issues, 1):
            repo = issue['repository']['nameWithOwner']
            num = issue['number']
            url = issue['url']
            title = issue['title']
            closed_date = format_date(issue['closedAt'])
            desc = clean_body(issue['body'], title)
            report.append(f"| {idx} | {repo} | [#{num}]({url}) | {title} | {closed_date} | {desc} |")
    else:
        report.append("*No closed issues found.*\n")
    report.append("\n")

    report.append("### Triaged Issues\n")
    report.append("Issues opened by others that were closed after you commented or contributed to triaging them.\n\n")
    if triaged_issues:
        report.append("| # | Repository | Issue | Title | Closed Date | Description |")
        report.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for idx, issue in enumerate(triaged_issues, 1):
            repo = issue['repository']['nameWithOwner']
            num = issue['number']
            url = issue['url']
            title = issue['title']
            closed_date = format_date(issue['closedAt'])
            desc = clean_body(issue['body'], title)
            report.append(f"| {idx} | {repo} | [#{num}]({url}) | {title} | {closed_date} | {desc} |")
    else:
        report.append("*No triaged issues found.*\n")
    report.append("\n")

    report.append(f"\n*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*")

    # Write output to README.md
    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print("README.md successfully updated!")

if __name__ == "__main__":
    main()
