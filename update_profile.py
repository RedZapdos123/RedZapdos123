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
    print(f"Running CLI command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, encoding="utf-8")
    print(f"Command finished with return code {result.returncode}")
    if result.returncode != 0:
        print(f"Error output: {result.stderr}")
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
    
    # URL-encode spaces as +
    query = query.replace(" ", "+")
    print(f"Calculating commits count with query: {query}")
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
    exclude_users = ["RedZapdos123", "WhiteMetagross", "Digvijay-x1", "swarupn17"]
    
    report = []
    report.append(f"# Hi there, I'm @{user}\n")
    report.append(f'<div align="center">\n  <img src="https://visitor-badge.laobi.icu/badge?page_id={user}.{user}" />\n</div>\n')
    report.append("Welcome to my GitHub profile! This page is automatically updated with my latest FOSS contributions and metrics.\n")

    # 1. Fetch commit counts with exclusions applied
    print(f"Fetching commit counts for {user}...")
    overall_commits = get_commit_count(user, exclude_users=exclude_users)
    print(f"Overall commits: {overall_commits}")
    target_commits = get_commit_count(user, TARGET_REPOS)
    print(f"Target commits: {target_commits}")
    
    # 2. Fetch merged PRs
    print(f"Fetching merged PRs for {user}...")
    prs_args = ["search", "prs", "--author", user, "--merged", "--limit", "1000", "--json", "repository"]
    merged_prs = run_gh_command(prs_args)
    if not isinstance(merged_prs, list):
        merged_prs = []
    print(f"Total raw merged PRs: {len(merged_prs)}")
    
    # Exclude self-owned, co-owned, or specified accounts
    def is_excluded(item):
        repo = item.get("repository", {}).get("nameWithOwner", "")
        owner = repo.split("/")[0].lower()
        if owner in {u.lower() for u in exclude_users}:
            return True
        return False

    merged_prs = [p for p in merged_prs if not is_excluded(p)]
    print(f"Merged PRs after exclusion: {len(merged_prs)}")
    
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
    print(f"Open PRs after exclusion: {len(open_prs)}")
    
    # 4. Fetch Opened Issues
    print(f"Fetching opened issues for {user}...")
    issues_open_args = ["search", "issues", "type:issue", "--author", user, "--state", "open", "--limit", "1000", "--json", "repository"]
    open_issues = run_gh_command(issues_open_args)
    if not isinstance(open_issues, list):
        open_issues = []
    open_issues = [i for i in open_issues if not is_excluded(i)]
    print(f"Open issues after exclusion: {len(open_issues)}")
    
    # 5. Fetch Closed Issues
    print(f"Fetching closed issues for {user}...")
    issues_closed_args = ["search", "issues", "type:issue", "--author", user, "--state", "closed", "--limit", "1000", "--json", "repository"]
    closed_issues = run_gh_command(issues_closed_args)
    if not isinstance(closed_issues, list):
        closed_issues = []
    closed_issues = [i for i in closed_issues if not is_excluded(i)]
    print(f"Closed issues after exclusion: {len(closed_issues)}")
    
    # Calculate issues stats
    overall_issues_count = len(open_issues) + len(closed_issues)
    target_issues_count = (
        len([i for i in open_issues if i.get("repository", {}).get("nameWithOwner", "") in TARGET_REPOS]) +
        len([i for i in closed_issues if i.get("repository", {}).get("nameWithOwner", "") in TARGET_REPOS])
    )

    # 6. Fetch code reviews count
    print(f"Fetching code reviews count for {user}...")
    reviews_res = run_gh_command(["search", "prs", "--reviewed-by", user, "--limit", "1000", "--json", "repository"])
    if not isinstance(reviews_res, list):
        reviews_res = []
    reviews = [r for r in reviews_res if not is_excluded(r)]
    target_reviews_count = len([r for r in reviews if r.get("repository", {}).get("nameWithOwner", "") in TARGET_REPOS])
    print(f"Target reviews count: {target_reviews_count}")

    # 7. Aggregate top repos
    repo_counts = {}
    for items in [merged_prs, open_prs, open_issues, closed_issues]:
        for item in items:
            repo = item.get("repository", {}).get("nameWithOwner", "")
            if repo:
                repo_counts[repo] = repo_counts.get(repo, 0) + 1
    
    # Filter top repos to only include those in TARGET_REPOS for target card description
    target_repo_counts = {r: c for r, c in repo_counts.items() if r in TARGET_REPOS}
    sorted_target_repos = sorted(target_repo_counts.items(), key=lambda x: x[1], reverse=True)
    top_target_repos = [r[0] for r in sorted_target_repos]
    other_target_repos_count = max(0, len(target_repo_counts) - 3)

    if len(top_target_repos) >= 3:
        repos_desc = f"Contributed to <strong>{top_target_repos[0]}</strong>, <strong>{top_target_repos[1]}</strong>, <strong>{top_target_repos[2]}</strong> and <strong>{other_target_repos_count} other target repositories</strong>."
    elif len(top_target_repos) == 2:
        repos_desc = f"Contributed to <strong>{top_target_repos[0]}</strong> and <strong>{top_target_repos[1]}</strong> among target repositories."
    elif len(top_target_repos) == 1:
        repos_desc = f"Contributed to <strong>{top_target_repos[0]}</strong> among target repositories."
    else:
        repos_desc = "Actively contributing to selected target open-source repositories."

    # 8. Calculate percentages for radar chart (Target repositories only)
    total_target_activity = target_commits + target_merged_prs_count + target_issues_count + target_reviews_count
    if total_target_activity == 0:
        total_target_activity = 1
        
    p_commits = target_commits / total_target_activity
    p_prs = target_merged_prs_count / total_target_activity
    p_issues = target_issues_count / total_target_activity
    p_reviews = target_reviews_count / total_target_activity

    d_max = 70
    x_center = 120
    y_center = 110
    
    # West (left): Commits
    x_commits = x_center - d_max * p_commits
    # South (bottom): Pull Requests
    y_prs = y_center + d_max * p_prs
    # East (right): Issues
    x_issues = x_center + d_max * p_issues
    # North (top): Code Reviews
    y_reviews = y_center - d_max * p_reviews

    polygon_points = f"{x_center},{y_reviews:.1f} {x_issues:.1f},{y_center} {x_center},{y_prs:.1f} {x_commits:.1f},{y_center}"

    radar_chart_svg = f"""<svg width="240" height="220" viewBox="0 0 240 220" xmlns="http://www.w3.org/2000/svg" style="background: transparent; display: block; margin: auto;">
  <!-- Grid Lines (Diamonds) -->
  <polygon points="120,92.5 137.5,110 120,127.5 102.5,110" fill="none" stroke="#E9D5FF" stroke-width="1" stroke-dasharray="2 2" />
  <polygon points="120,75 155,110 120,145 85,110" fill="none" stroke="#E9D5FF" stroke-width="1" stroke-dasharray="2 2" />
  <polygon points="120,57.5 172.5,110 120,162.5 67.5,110" fill="none" stroke="#E9D5FF" stroke-width="1" stroke-dasharray="2 2" />
  <polygon points="120,40 190,110 120,180 50,110" fill="none" stroke="#D8B4FE" stroke-width="1" />

  <!-- Axes -->
  <line x1="120" y1="40" x2="120" y2="180" stroke="#C084FC" stroke-width="1.5" />
  <line x1="50" y1="110" x2="190" y2="110" stroke="#C084FC" stroke-width="1.5" />

  <!-- Activity Polygon -->
  <polygon points="{polygon_points}" fill="#A78BFA" fill-opacity="0.4" stroke="#7C3AED" stroke-width="2" />

  <!-- Data Points -->
  <circle cx="{x_center}" cy="{y_reviews:.1f}" r="3" fill="#FFFFFF" stroke="#7C3AED" stroke-width="1.5" />
  <circle cx="{x_issues:.1f}" cy="{y_center}" r="3" fill="#FFFFFF" stroke="#7C3AED" stroke-width="1.5" />
  <circle cx="{x_center}" cy="{y_prs:.1f}" r="3" fill="#FFFFFF" stroke="#7C3AED" stroke-width="1.5" />
  <circle cx="{x_commits:.1f}" cy="{y_center}" r="3" fill="#FFFFFF" stroke="#7C3AED" stroke-width="1.5" />

  <!-- Labels -->
  <!-- North (Code Review) -->
  <text x="120" y="25" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="9" font-weight="bold" fill="#6B21A8" text-anchor="middle">{p_reviews:.0%} Code review</text>
  <!-- East (Issues) -->
  <text x="196" y="113" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="9" font-weight="bold" fill="#6B21A8" text-anchor="start">{p_issues:.0%} Issues</text>
  <!-- South (Pull Requests) -->
  <text x="120" y="196" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="9" font-weight="bold" fill="#6B21A8" text-anchor="middle">{p_prs:.0%} Pull requests</text>
  <!-- West (Commits) -->
  <text x="44" y="113" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="9" font-weight="bold" fill="#6B21A8" text-anchor="end">{p_commits:.0%} Commits</text>
</svg>"""

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

    activity_overview_card = f"""<table align="center" style="border: 1px solid #E9D5FF; border-radius: 12px; width: 100%; max-width: 800px; margin: 20px auto; background: #FAF5FF; border-collapse: separate; padding: 15px; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.05);">
  <tr style="border: none; background: transparent;">
    <td style="width: 55%; vertical-align: middle; padding: 15px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; border: none;">
      <h3 style="margin-top: 0; color: #4C1D95; font-size: 1.2em;">Target Repositories Activity Overview</h3>
      <p style="color: #6D28D9; font-size: 0.95em; line-height: 1.6;">
        {repos_desc}
      </p>
      <div style="margin-top: 20px;">
        <span style="display: inline-block; background: #F3E8FF; color: #7C3AED; font-size: 0.8em; font-weight: bold; padding: 5px 12px; border-radius: 20px; margin-right: 8px; margin-bottom: 8px; border: 1px solid #D8B4FE;">Commits: {target_commits}</span>
        <span style="display: inline-block; background: #F3E8FF; color: #7C3AED; font-size: 0.8em; font-weight: bold; padding: 5px 12px; border-radius: 20px; margin-right: 8px; margin-bottom: 8px; border: 1px solid #D8B4FE;">PRs: {target_merged_prs_count}</span>
        <span style="display: inline-block; background: #F3E8FF; color: #7C3AED; font-size: 0.8em; font-weight: bold; padding: 5px 12px; border-radius: 20px; margin-right: 8px; margin-bottom: 8px; border: 1px solid #D8B4FE;">Issues: {target_issues_count}</span>
        <span style="display: inline-block; background: #F3E8FF; color: #7C3AED; font-size: 0.8em; font-weight: bold; padding: 5px 12px; border-radius: 20px; margin-bottom: 8px; border: 1px solid #D8B4FE;">Reviews: {target_reviews_count}</span>
      </div>
    </td>
    <td align="center" style="width: 45%; vertical-align: middle; padding: 15px; border: none;">
      {radar_chart_svg}
    </td>
  </tr>
</table>
"""

    report.append("## Contribution Statistics\n")
    report.append(dashboard_html)
    report.append("\n")
    report.append(activity_overview_card)
    report.append("\n")
    report.append(f"\n*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*")

    # Write output to README.md
    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print("README.md successfully updated!")

if __name__ == "__main__":
    main()
