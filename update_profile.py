import json
import subprocess
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

def generate_card_svg(prs_count, issues_count):
    return f"""<svg width="450" height="200" viewBox="0 0 450 200" xmlns="http://www.w3.org/2000/svg" style="background: transparent; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <defs>
    <!-- Gradient for the rings -->
    <linearGradient id="purpleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#C084FC" />
      <stop offset="100%" stop-color="#7C3AED" />
    </linearGradient>
    <!-- Drop Shadow Filter -->
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#7C3AED" flood-opacity="0.15" />
    </filter>
  </defs>

  <!-- Card Body -->
  <rect width="450" height="200" rx="16" fill="#FAF5FF" stroke="#E9D5FF" stroke-width="1.5" />

  <!-- Header -->
  <text x="25" y="34" font-size="15" font-weight="bold" fill="#4C1D95" letter-spacing="0.5">FOSS Contributions</text>
  <!-- Embedded Live Visitor Badge -->
  <image href="https://visitor-badge.laobi.icu/badge?page_id=RedZapdos123.RedZapdos123" x="315" y="18" width="110" height="20" />

  <line x1="20" y1="52" x2="430" y2="52" stroke="#E9D5FF" stroke-width="1" />

  <!-- Gauge 1: PRs -->
  <g transform="translate(130, 120)">
    <!-- Background circle (270 degree arc: dasharray="165 55" for r=35) -->
    <circle cx="0" cy="0" r="35" stroke="#F3E8FF" stroke-width="7" stroke-linecap="round" fill="none" 
            stroke-dasharray="164.9 55" transform="rotate(135)" />
    <!-- Foreground circle -->
    <circle cx="0" cy="0" r="35" stroke="url(#purpleGrad)" stroke-width="7" stroke-linecap="round" fill="none" 
            stroke-dasharray="164.9 55" transform="rotate(135)" filter="url(#shadow)" />
    <!-- Text -->
    <text x="0" y="-4" font-size="18" font-weight="bold" fill="#4C1D95" text-anchor="middle" dominant-baseline="middle">{prs_count}</text>
    <text x="0" y="16" font-size="8.5" font-weight="800" fill="#7C3AED" text-anchor="middle" letter-spacing="0.5">FOSS PRs</text>
    <text x="0" y="26" font-size="7.5" font-weight="600" fill="#A78BFA" text-anchor="middle" letter-spacing="0.5">MERGED</text>
  </g>

  <!-- Gauge 2: Issues -->
  <g transform="translate(320, 120)">
    <!-- Background circle -->
    <circle cx="0" cy="0" r="35" stroke="#F3E8FF" stroke-width="7" stroke-linecap="round" fill="none" 
            stroke-dasharray="164.9 55" transform="rotate(135)" />
    <!-- Foreground circle -->
    <circle cx="0" cy="0" r="35" stroke="url(#purpleGrad)" stroke-width="7" stroke-linecap="round" fill="none" 
            stroke-dasharray="164.9 55" transform="rotate(135)" filter="url(#shadow)" />
    <!-- Text -->
    <text x="0" y="-4" font-size="18" font-weight="bold" fill="#4C1D95" text-anchor="middle" dominant-baseline="middle">{issues_count}</text>
    <text x="0" y="16" font-size="8.5" font-weight="800" fill="#7C3AED" text-anchor="middle" letter-spacing="0.5">FOSS ISSUES</text>
    <text x="0" y="26" font-size="7.5" font-weight="600" fill="#A78BFA" text-anchor="middle" letter-spacing="0.5">AUTHORED</text>
  </g>
</svg>"""

def main():
    user = "RedZapdos123"
    exclude_users = ["RedZapdos123", "WhiteMetagross", "Digvijay-x1", "swarupn17", "Paraspandey-debugs", "yenode", "RajanPatil1904", "LevelSilence"]
    
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
    prs_args = ["search", "prs", "--author", user, "--merged", "--limit", "1000", "--json", "repository"]
    merged_prs = run_gh_command(prs_args)
    if not isinstance(merged_prs, list):
        merged_prs = []
    merged_prs = [p for p in merged_prs if not is_excluded(p)]
    
    # Add co-authored DLT PR
    merged_prs.append({"repository": {"nameWithOwner": "dlt-hub/dlt"}})
    foss_prs_count = len(merged_prs)

    # 2. Fetch Open Issues
    print(f"Fetching open issues for {user}...")
    issues_open_args = ["search", "issues", "type:issue", "--author", user, "--state", "open", "--limit", "1000", "--json", "repository"]
    open_issues = run_gh_command(issues_open_args)
    if not isinstance(open_issues, list):
        open_issues = []
    open_issues = [i for i in open_issues if not is_excluded(i)]
    
    # 3. Fetch Closed Issues
    print(f"Fetching closed issues for {user}...")
    issues_closed_args = ["search", "issues", "type:issue", "--author", user, "--state", "closed", "--limit", "1000", "--json", "repository"]
    closed_issues = run_gh_command(issues_closed_args)
    if not isinstance(closed_issues, list):
        closed_issues = []
    closed_issues = [i for i in closed_issues if not is_excluded(i)]
    
    foss_issues_count = len(open_issues) + len(closed_issues)

    # Generate output
    report = []
    report.append('<div align="center">')
    report.append(generate_card_svg(foss_prs_count, foss_issues_count))
    report.append('</div>')

    # Write output to README.md
    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print("README.md successfully updated!")

if __name__ == "__main__":
    main()
