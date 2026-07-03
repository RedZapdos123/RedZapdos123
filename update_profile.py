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
    # Expanded vertically stacked layout with extra-large circles (r=65)
    return f"""<svg width="300" height="440" viewBox="0 0 300 440" xmlns="http://www.w3.org/2000/svg" style="background: transparent; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <defs>
    <!-- Purple Gradient for PRs -->
    <linearGradient id="purpleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#C084FC" />
      <stop offset="100%" stop-color="#7C3AED" />
    </linearGradient>
    <!-- Green Gradient for Issues -->
    <linearGradient id="greenGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#34D399" />
      <stop offset="100%" stop-color="#059669" />
    </linearGradient>
    
    <!-- Drop Shadows -->
    <filter id="shadowPurple" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#7C3AED" flood-opacity="0.25" />
    </filter>
    <filter id="shadowGreen" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#059669" flood-opacity="0.25" />
    </filter>
  </defs>

  <style>
    /* Default Light Mode Styles */
    .title {{ fill: #000000; }}
    .line-div {{ stroke: #E9D5FF; }}
    .prs-track {{ stroke: #F3E8FF; }}
    .prs-num {{ fill: #4C1D95; }}
    .prs-lbl1 {{ fill: #7C3AED; }}
    .prs-lbl2 {{ fill: #A78BFA; }}
    
    .iss-track {{ stroke: #ECFDF5; }}
    .iss-num {{ fill: #064E3B; }}
    .iss-lbl1 {{ fill: #059669; }}
    .iss-lbl2 {{ fill: #10B981; }}

    /* Dark Mode Adaptive Styles */
    @media (prefers-color-scheme: dark) {{
      .title {{ fill: #FFFFFF; }}
      .line-div {{ stroke: #334155; }}
      .prs-track {{ stroke: #1E1B4B; }}
      .prs-num {{ fill: #FAF5FF; }}
      .prs-lbl1 {{ fill: #C084FC; }}
      .prs-lbl2 {{ fill: #A78BFA; }}
      
      .iss-track {{ stroke: #062F24; }}
      .iss-num {{ fill: #ECFDF5; }}
      .iss-lbl1 {{ fill: #34D399; }}
      .iss-lbl2 {{ fill: #6EE7B7; }}
    }}
  </style>

  <!-- Transparent Card Background -->
  <rect x="1" y="1" width="298" height="438" rx="16" fill="none" stroke="none" />

  <!-- Header (FOSS Contributions: in Black) -->
  <text x="25" y="35" font-size="15" font-weight="bold" class="title" letter-spacing="0.5">FOSS Contributions:</text>

  <!-- Divider line -->
  <line x1="20" y1="48" x2="280" y2="48" class="line-div" stroke-width="1" />

  <!-- Gauge 1: FOSS PRs Merged (Purple Theme) -->
  <g transform="translate(150, 145)">
    <!-- Background track circle (r=65, stroke-dasharray="306.3 102.1" for 270-degree cutout) -->
    <circle cx="0" cy="0" r="65" class="prs-track" stroke-width="11" stroke-linecap="round" fill="none" 
            stroke-dasharray="306.3 102.1" transform="rotate(135)" />
    <!-- Foreground Gauge -->
    <circle cx="0" cy="0" r="65" stroke="url(#purpleGrad)" stroke-width="11" stroke-linecap="round" fill="none" 
            stroke-dasharray="306.3 102.1" transform="rotate(135)" filter="url(#shadowPurple)" />
    <!-- Centered Number -->
    <text x="0" y="-10" font-size="32" font-weight="bold" class="prs-num" text-anchor="middle" dominant-baseline="middle">{prs_count}</text>
    <!-- Labels inside circle with optimized vertical space -->
    <text x="0" y="22" font-size="13" font-weight="800" class="prs-lbl1" text-anchor="middle">FOSS PRs</text>
    <text x="0" y="36" font-size="11" font-weight="600" class="prs-lbl2" text-anchor="middle">MERGED</text>
  </g>

  <!-- Gauge 2: FOSS Issues Authored (Green Theme) -->
  <g transform="translate(150, 320)">
    <!-- Background track circle -->
    <circle cx="0" cy="0" r="65" class="iss-track" stroke-width="11" stroke-linecap="round" fill="none" 
            stroke-dasharray="306.3 102.1" transform="rotate(135)" />
    <!-- Foreground Gauge -->
    <circle cx="0" cy="0" r="65" stroke="url(#greenGrad)" stroke-width="11" stroke-linecap="round" fill="none" 
            stroke-dasharray="306.3 102.1" transform="rotate(135)" filter="url(#shadowGreen)" />
    <!-- Centered Number -->
    <text x="0" y="-10" font-size="32" font-weight="bold" class="iss-num" text-anchor="middle" dominant-baseline="middle">{issues_count}</text>
    <!-- Labels inside circle with optimized vertical space -->
    <text x="0" y="22" font-size="13" font-weight="800" class="iss-lbl1" text-anchor="middle">FOSS ISSUES</text>
    <text x="0" y="36" font-size="11" font-weight="600" class="iss-lbl2" text-anchor="middle">AUTHORED</text>
  </g>
</svg>"""

def main():
    user = "RedZapdos123"
    exclude_users = ["RedZapdos123", "WhiteMetagross", "Digvijay-x1", "swarupn17", "Paraspandey-debugs", "yenode", "RajanPatil1904", "LevelSilence", "BlackRaichu"]
    
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

    # Generate README.md referencing the SVG file with cache-busting timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    report = []
    report.append('<div align="center">')
    report.append(f'  <img src="https://visitor-badge.laobi.icu/badge?page_id={user}.{user}" alt="Visitor Count" />')
    report.append('  <br/><br/>')
    report.append(f'  <img src="profile-summary.svg?v={timestamp}" alt="FOSS Contributions" />')
    report.append('</div>')

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print("README.md successfully updated!")

if __name__ == "__main__":
    main()
