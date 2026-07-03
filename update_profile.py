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

svg_counter = 0

def generate_badge_svg(number, label_line1, label_line2):
    global svg_counter
    svg_counter += 1
    grad_id = f"purpleGrad_{svg_counter}"
    shadow_id = f"shadow_{svg_counter}"
    return f"""<svg width="140" height="140" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" style="display: inline-block; vertical-align: middle; margin: 15px;">
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

    report = []
    report.append(f'<div align="center">\n  <img src="https://visitor-badge.laobi.icu/badge?page_id={user}.{user}" />\n</div>\n')
    
    # Centered Gauges Table
    gauges_html = f"""<table align="center" style="border: none; border-collapse: collapse; margin: 20px auto; background: transparent;">
  <tr style="border: none; background: transparent;">
    <td align="center" style="border: none; padding: 10px;">
      {generate_badge_svg(foss_prs_count, "FOSS PRs", "MERGED")}
    </td>
    <td align="center" style="border: none; padding: 10px;">
      {generate_badge_svg(foss_issues_count, "FOSS ISSUES", "AUTHORED")}
    </td>
  </tr>
</table>"""

    report.append(gauges_html)
    report.append(f'\n\n<div align="center">Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC</div>')

    # Write output to README.md
    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print("README.md successfully updated!")

if __name__ == "__main__":
    main()
