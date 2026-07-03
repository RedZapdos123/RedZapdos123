<div align="center">
<svg width="450" height="200" viewBox="0 0 450 200" xmlns="http://www.w3.org/2000/svg" style="background: transparent; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
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
    <text x="0" y="-4" font-size="18" font-weight="bold" fill="#4C1D95" text-anchor="middle" dominant-baseline="middle">83</text>
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
    <text x="0" y="-4" font-size="18" font-weight="bold" fill="#4C1D95" text-anchor="middle" dominant-baseline="middle">76</text>
    <text x="0" y="16" font-size="8.5" font-weight="800" fill="#7C3AED" text-anchor="middle" letter-spacing="0.5">FOSS ISSUES</text>
    <text x="0" y="26" font-size="7.5" font-weight="600" fill="#A78BFA" text-anchor="middle" letter-spacing="0.5">AUTHORED</text>
  </g>
</svg>
</div>