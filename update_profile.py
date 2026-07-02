import json
import subprocess
import re
import os
from datetime import datetime

# Selected target repositories from UpdatePrompt.md
TARGET_REPOS = {
    "CAPTAIN-WHU/iSAID_Devkit",
    "Delgan/loguru",
    "JDAI-CV/fast-reid",
    "dlt-hub/dlt",
    "duckdb/duckdb",
    "fb55/css-select",
    "ibis-project/ibis",
    "joke2k/faker",
    "koaning/drawdata",
    "koaning/scikit-lego",
    "openSUSE/obs-landing",
    "openSUSE/open-build-service",
    "openSUSE/osem",
    "plotly/plotly.rs",
    "pola-rs/polars",
    "pydantic/pydantic-extra-types",
    "python/tzdata",
    "rage-rb/rage",
    "rubocop/rubocop",
    "tobymao/sqlglot",
    "unionai-oss/pandera",
    "uyuni-project/uyuni",
    "uyuni-project/uyuni-tools",
}

def run_gh_command(args):
    env = os.environ.copy()
    if "GITHUB_TOKEN" in env and (not env["GITHUB_TOKEN"] or env["GITHUB_TOKEN"].startswith("gho_")):
        del env["GITHUB_TOKEN"]
    
    # Try standard Windows installation path, fall back to "gh" command in PATH (Linux Actions runner)
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
        print(f"Failed to parse JSON for command {' '.join(cmd)}: {e}")
        return []

def get_commit_count(user, repos=None):
    if not repos:
        query = f"author:{user}"
    else:
        query = f"author:{user}+" + "+".join(f"repo:{r}" for r in repos)
    
    res = run_gh_command(["api", f"search/commits?q={query}"])
    if isinstance(res, dict):
        return res.get("total_count", 0)
    return 0

svg_counter = 0

def generate_badge_svg(number, label_line1, label_line2):
    global svg_counter
    svg_counter += 1
    grad_id = f"purpleGrad_{svg_counter}"
    shadow_id = f"shadow_{svg_counter}"
    return f"""<svg width="120" height="120" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" style="display: inline-block; vertical-align: middle; margin: 10px;">
  <defs>
    <!-- Purple Gradient for the ring -->
    <linearGradient id="{grad_id}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#C084FC" />
      <stop offset="100%" stop-color="#7C3AED" />
    </linearGradient>
    <!-- Drop Shadow Filter for premium feel -->
    <filter id="{shadow_id}" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#7C3AED" flood-opacity="0.15" />
    </filter>
  </defs>
  <!-- Background Track -->
  <circle cx="60" cy="60" r="40" stroke="#F3E8FF" stroke-width="8" stroke-linecap="round" fill="none" 
          stroke-dasharray="188.5 62.8" transform="rotate(135 60 60)" />
  <!-- Foreground Track with Gradient -->
  <circle cx="60" cy="60" r="40" stroke="url(#{grad_id})" stroke-width="8" stroke-linecap="round" fill="none" 
          stroke-dasharray="188.5 62.8" transform="rotate(135 60 60)" filter="url(#{shadow_id})" />
  <!-- Number -->
  <text x="60" y="55" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" 
        font-size="20" font-weight="bold" fill="#4C1D95" text-anchor="middle" dominant-baseline="middle">{number}</text>
  <!-- Label Line 1 -->
  <text x="60" y="76" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" 
        font-size="8.5" font-weight="800" fill="#7C3AED" text-anchor="middle" letter-spacing="0.5">{label_line1}</text>
  <!-- Label Line 2 -->
  <text x="60" y="86" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" 
        font-size="7.5" font-weight="600" fill="#A78BFA" text-anchor="middle" letter-spacing="0.5">{label_line2}</text>
</svg>"""

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
    
    triaged_data = []
    if os.path.exists("triaged_issues.json"):
        try:
            with open("triaged_issues.json", "r", encoding="utf-8") as f:
                triaged_data = json.load(f)
        except Exception as e:
            print(f"Error loading triaged issues: {e}")

    report = []
    report.append(f"# Hi there, I'm @{user} 👋\n")
    report.append("Welcome to my GitHub profile! This page is automatically updated with my latest FOSS contributions and metrics.\n")

    # 1. Fetch commit counts
    print(f"Fetching commit counts for {user}...")
    overall_commits = get_commit_count(user)
    target_commits = get_commit_count(user, TARGET_REPOS)
    
    # 2. Fetch merged PRs
    print(f"Fetching merged PRs for {user}...")
    prs_args = ["search", "prs", "--author", user, "--merged", "--limit", "100", "--json", "repository,number,title,body,url,createdAt,closedAt"]
    merged_prs = run_gh_command(prs_args)
    
    # Exclude self-owned, co-owned, or specified accounts
    def is_excluded(item):
        repo = item.get("repository", {}).get("nameWithOwner", "")
        owner = repo.split("/")[0].lower()
        if owner in {"redzapdos123", "whitemetagross"}:
            return True
        if "digvijay" in owner or "swarup" in owner or "paraspandey" in owner:
            return True
        return False

    merged_prs = [p for p in merged_prs if not is_excluded(p)]
    
    # Fetch co-authored DLT PR
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
    
    # Sort all merged PRs by closedAt descending
    merged_prs.sort(key=lambda x: x.get("closedAt", ""), reverse=True)
        
    # Calculate merged PR stats
    overall_merged_prs_count = len(merged_prs)
    target_merged_prs_count = len([p for p in merged_prs if p.get("repository", {}).get("nameWithOwner", "") in TARGET_REPOS])

    # 3. Fetch Open PRs
    print(f"Fetching open PRs for {user}...")
    open_prs_args = ["search", "prs", "--author", user, "--state", "open", "--limit", "100", "--json", "repository,number,title,body,url,createdAt"]
    open_prs = run_gh_command(open_prs_args)
    open_prs = [p for p in open_prs if not is_excluded(p)]
    
    # 4. Fetch Opened Issues
    print(f"Fetching opened issues for {user}...")
    issues_open_args = ["search", "issues", "type:issue", "--author", user, "--state", "open", "--limit", "100", "--json", "repository,number,title,body,url,createdAt"]
    open_issues = run_gh_command(issues_open_args)
    open_issues = [i for i in open_issues if not is_excluded(i)]
    
    # 5. Fetch Closed Issues
    print(f"Fetching closed issues for {user}...")
    issues_closed_args = ["search", "issues", "type:issue", "--author", user, "--state", "closed", "--limit", "100", "--json", "repository,number,title,body,url,closedAt"]
    closed_issues = run_gh_command(issues_closed_args)
    closed_issues = [i for i in closed_issues if not is_excluded(i)]
    
    # Calculate issues stats
    overall_issues_count = len(open_issues) + len(closed_issues)
    target_issues_count = (
        len([i for i in open_issues if i.get("repository", {}).get("nameWithOwner", "") in TARGET_REPOS]) +
        len([i for i in closed_issues if i.get("repository", {}).get("nameWithOwner", "") in TARGET_REPOS])
    )

    # 6. Generate circular gauge dashboard HTML
    dashboard_html = f"""<table align="center" style="border: none; border-collapse: collapse; width: 100%; max-width: 800px; margin: 20px auto; background: transparent;">
  <tr style="border: none; background: transparent;">
    <th colspan="3" align="center" style="border: none; padding: 10px; font-weight: bold; font-size: 1.1em; color: #4C1D95; letter-spacing: 1px;">
      🌐 GLOBAL EXTERNAL STATS
    </th>
    <th colspan="3" align="center" style="border: none; padding: 10px; font-weight: bold; font-size: 1.1em; color: #4C1D95; letter-spacing: 1px;">
      🎯 TARGET REPOS STATS
    </th>
  </tr>
  <tr style="border: none; background: transparent;">
    <td align="center" style="border: none; padding: 5px; width: 16.66%;">
      {generate_badge_svg(overall_commits, "GLOBAL", "COMMITS")}
    </td>
    <td align="center" style="border: none; padding: 5px; width: 16.66%;">
      {generate_badge_svg(overall_merged_prs_count, "PRs", "MERGED")}
    </td>
    <td align="center" style="border: none; padding: 5px; width: 16.66%;">
      {generate_badge_svg(overall_issues_count, "ISSUES", "AUTHORED")}
    </td>
    <td align="center" style="border: none; padding: 5px; width: 16.66%;">
      {generate_badge_svg(target_commits, "TARGET", "COMMITS")}
    </td>
    <td align="center" style="border: none; padding: 5px; width: 16.66%;">
      {generate_badge_svg(target_merged_prs_count, "TARGET PRs", "MERGED")}
    </td>
    <td align="center" style="border: none; padding: 5px; width: 16.66%;">
      {generate_badge_svg(target_issues_count, "TARGET ISSUES", "AUTHORED")}
    </td>
  </tr>
</table>
"""
    report.append(dashboard_html)
    report.append("\n")

    # Merged Pull Requests detail table
    report.append("### 🚀 Merged Pull Requests\n")
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

    # Open Pull Requests detail table
    report.append("### ⏳ Open Pull Requests\n")
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

    # Opened Issues detail table
    report.append("### 📋 Opened Issues\n")
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

    # Closed Issues detail table
    report.append("### ✅ Closed Issues\n")
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

    # Triaged Issues detail table
    user_triaged = [i for i in triaged_data if i.get("user") == user]
    report.append("### 🔍 Triaged Issues\n")
    report.append("Issues opened by others that were closed after commenting or contributing to triaging.\n")
    if user_triaged:
        report.append("| # | Repository | Issue | Title | Closed Date | Description |")
        report.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for idx, issue in enumerate(user_triaged, 1):
            repo = issue['repo']
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
