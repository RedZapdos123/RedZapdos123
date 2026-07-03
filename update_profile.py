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

def get_commit_count(user, repos=None, exclude_users=None):
    if not repos:
        query = f"author:{user}"
        if exclude_users:
            query += " " + " ".join(f"-user:{u}" for u in exclude_users)
    else:
        query = f"author:{user}+" + "+".join(f"repo:{r}" for r in repos)
    
    query = query.replace(" ", "+")
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

def main():
    user = "RedZapdos123"
    exclude_users = ["RedZapdos123", "WhiteMetagross", "Digvijay-x1", "swarupn17", "Paraspandey-debugs", "yenode", "RajanPatil1904", "LevelSilence"]
    
    report = []
    report.append(f"# Hi there, I'm @{user}\n")
    report.append(f'<div align="center">\n  <img src="https://visitor-badge.laobi.icu/badge?page_id={user}.{user}" />\n</div>\n')
    report.append("Welcome to my GitHub profile! This page is automatically updated with my latest FOSS contributions and metrics.\n")

    # 1. Fetch commit counts with exclusions applied
    print(f"Fetching commit counts for {user}...")
    overall_commits = get_commit_count(user, exclude_users=exclude_users)
    target_commits = get_commit_count(user, TARGET_REPOS)
    
    # 2. Fetch merged PRs
    print(f"Fetching merged PRs for {user}...")
    prs_args = ["search", "prs", "--author", user, "--merged", "--limit", "1000", "--json", "repository"]
    merged_prs = run_gh_command(prs_args)
    if not isinstance(merged_prs, list):
        merged_prs = []
    
    # Exclude self-owned, co-owned, or specified accounts
    def is_excluded(item):
        repo = item.get("repository", {}).get("nameWithOwner", "")
        owner = repo.split("/")[0].lower()
        if owner in {u.lower() for u in exclude_users}:
            return True
        return False

    merged_prs = [p for p in merged_prs if not is_excluded(p)]
    
    # Add co-authored DLT PR
    if not any(p.get("repository", {}).get("nameWithOwner", "") == "dlt-hub/dlt" for p in merged_prs):
        merged_prs.append({"repository": {"nameWithOwner": "dlt-hub/dlt"}})
        
    overall_merged_prs_count = len(merged_prs)
    target_merged_prs_count = len([p for p in merged_prs if p.get("repository", {}).get("nameWithOwner", "") in TARGET_REPOS])

    # 3. Fetch Open PRs
    print(f"Fetching open PRs for {user}...")
    open_prs_args = ["search", "prs", "--author", user, "--state", "open", "--limit", "1000", "--json", "repository"]
    open_prs = run_gh_command(open_prs_args)
    if not isinstance(open_prs, list):
        open_prs = []
    open_prs = [p for p in open_prs if not is_excluded(p)]
    
    # 4. Fetch Opened Issues
    print(f"Fetching opened issues for {user}...")
    issues_open_args = ["search", "issues", "type:issue", "--author", user, "--state", "open", "--limit", "1000", "--json", "repository"]
    open_issues = run_gh_command(issues_open_args)
    if not isinstance(open_issues, list):
        open_issues = []
    open_issues = [i for i in open_issues if not is_excluded(i)]
    
    # 5. Fetch Closed Issues
    print(f"Fetching closed issues for {user}...")
    issues_closed_args = ["search", "issues", "type:issue", "--author", user, "--state", "closed", "--limit", "1000", "--json", "repository"]
    closed_issues = run_gh_command(issues_closed_args)
    if not isinstance(closed_issues, list):
        closed_issues = []
    closed_issues = [i for i in closed_issues if not is_excluded(i)]
    
    # Calculate issues stats
    overall_issues_count = len(open_issues) + len(closed_issues)
    target_issues_count = (
        len([i for i in open_issues if i.get("repository", {}).get("nameWithOwner", "") in TARGET_REPOS]) +
        len([i for i in closed_issues if i.get("repository", {}).get("nameWithOwner", "") in TARGET_REPOS])
    )

    # Generate circular gauge dashboard HTML
    dashboard_html = f"""<table align="center" style="border: none; border-collapse: collapse; width: 100%; max-width: 800px; margin: 20px auto; background: transparent;">
  <tr style="border: none; background: transparent;">
    <th colspan="3" align="center" style="border: none; padding: 10px; font-weight: bold; font-size: 1.1em; color: #4C1D95; letter-spacing: 1px;">
      GLOBAL EXTERNAL STATS
    </th>
    <th colspan="3" align="center" style="border: none; padding: 10px; font-weight: bold; font-size: 1.1em; color: #4C1D95; letter-spacing: 1px;">
      TARGET REPOS STATS
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

    report.append("## Contribution Statistics\n")
    report.append(dashboard_html)
    report.append("\n")
    report.append(f"\n*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*")

    # Write output to README.md
    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print("README.md successfully updated!")

if __name__ == "__main__":
    main()
