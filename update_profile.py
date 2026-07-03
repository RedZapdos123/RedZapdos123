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
    # Professional github-readme-stats style SVG card
    return f"""<svg width="495" height="195" viewBox="0 0 495 195" xmlns="http://www.w3.org/2000/svg" style="background: transparent; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Ubuntu, sans-serif;">
  <defs>
    <!-- Purple Gradient for the rings -->
    <linearGradient id="purpleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#C084FC" />
      <stop offset="100%" stop-color="#7C3AED" />
    </linearGradient>
    <!-- Drop Shadow Filter for a premium feel -->
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#7C3AED" flood-opacity="0.25" />
    </filter>
  </defs>

  <!-- Card Background (standard github-readme-stats dimensions and border) -->
  <rect x="0.5" y="0.5" width="494" height="194" rx="4.5" fill="#0D0E15" stroke="#312E81" stroke-width="1" />

  <!-- Card Title -->
  <text x="25" y="35" font-size="18" font-weight="bold" fill="#C084FC">FOSS Contributions</text>

  <!-- Divider line -->
  <line x1="25" y1="48" x2="470" y2="48" stroke="#312E81" stroke-width="1.5" />

  <!-- Gauge 1: FOSS PRs Merged -->
  <g transform="translate(150, 105)">
    <!-- Background Track -->
    <circle cx="0" cy="0" r="30" stroke="#1E1B4B" stroke-width="6" stroke-linecap="round" fill="none" 
            stroke-dasharray="141.4 47.1" transform="rotate(135)" />
    <!-- Foreground Gauge -->
    <circle cx="0" cy="0" r="30" stroke="url(#purpleGrad)" stroke-width="6" stroke-linecap="round" fill="none" 
            stroke-dasharray="141.4 47.1" transform="rotate(135)" filter="url(#shadow)" />
    <!-- Centered Number -->
    <text x="0" y="5" font-size="18" font-weight="bold" fill="#FAF5FF" text-anchor="middle" dominant-baseline="middle">{prs_count}</text>
    <!-- Labels (completely separated to prevent overlaps) -->
    <text x="0" y="50" font-size="11" font-weight="bold" fill="#FAF5FF" text-anchor="middle">FOSS PRs</text>
    <text x="0" y="62" font-size="9" font-weight="bold" fill="#A78BFA" text-anchor="middle">MERGED</text>
  </g>

  <!-- Gauge 2: FOSS Issues Authored -->
  <g transform="translate(345, 105)">
    <!-- Background Track -->
    <circle cx="0" cy="0" r="30" stroke="#1E1B4B" stroke-width="6" stroke-linecap="round" fill="none" 
            stroke-dasharray="141.4 47.1" transform="rotate(135)" />
    <!-- Foreground Gauge -->
    <circle cx="0" cy="0" r="30" stroke="url(#purpleGrad)" stroke-width="6" stroke-linecap="round" fill="none" 
            stroke-dasharray="141.4 47.1" transform="rotate(135)" filter="url(#shadow)" />
    <!-- Centered Number -->
    <text x="0" y="5" font-size="18" font-weight="bold" fill="#FAF5FF" text-anchor="middle" dominant-baseline="middle">{issues_count}</text>
    <!-- Labels (completely separated to prevent overlaps) -->
    <text x="0" y="50" font-size="11" font-weight="bold" fill="#FAF5FF" text-anchor="middle">FOSS Issues</text>
    <text x="0" y="62" font-size="9" font-weight="bold" fill="#A78BFA" text-anchor="middle">AUTHORED</text>
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

    # Save SVG card to file
    card_svg = generate_card_svg(foss_prs_count, foss_issues_count)
    with open("profile-summary.svg", "w", encoding="utf-8") as f:
        f.write(card_svg)
    print("profile-summary.svg successfully saved!")

    # Generate README.md referencing the SVG file
    report = []
    report.append('<div align="center">')
    report.append(f'  <img src="https://visitor-badge.laobi.icu/badge?page_id={user}.{user}" alt="Visitor Count" />')
    report.append('  <br/><br/>')
    report.append('  <img src="profile-summary.svg" alt="FOSS Contributions" />')
    report.append('</div>')

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print("README.md successfully updated!")

if __name__ == "__main__":
    main()
