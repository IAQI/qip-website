# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Hugo-powered static website for the Quantum Information Processing (QIP) conference series. The site is hosted on Netlify and uses the `devfest-theme-hugo` theme (included directly in the repo, not as a submodule).

## Development Commands

```bash
# Start local development server (site available at http://localhost:1313/)
hugo server

# Build the site to /public directory
hugo build

# Install PostCSS dependencies (required for theme editing)
npm clean-install

# Test SASS compilation independently
sass themes/devfest-theme-hugo/assets/style/theme-2027.scss themes/devfest-theme-hugo/assets/style/theme-2027.css
```

Required tools: Hugo, Dart Sass, Node.js (for theme development)

## Architecture

### Multi-Year Structure

The site deviates from standard Hugo organization - top-level directories in `content/` are years (2024, 2027), not topics. The `.Section` variable often equals `$currentYear`.

Key configuration in `hugo.toml`:
- `params.currentYear` - determines which year is "active"
- `[params.YEAR]` - year-specific settings (city, themeColor, logos)
- `[[menu.YEAR]]` - navigation menu per year
- `[[server.redirects]]` and `netlify.toml` redirects - control root URL redirect

### Content Organization

```
content/YEAR/
├── _index.html          # Home page (type: home, layout: home)
├── sessions/            # Talk/event sessions
├── speakers/            # Speaker profiles (organized by type: invited, tutorial, contributed)
├── partners/            # Sponsors (organized by tier: gold, silver, bronze)
├── team/                # Committee members
├── schedule/            # Schedule page (_index.html)
├── code-of-conduct.md   # Required by Netlify open source plan
├── charter.md
└── history.md
```

### Data Files (`data/`)

- `schedule-YEAR.yml` - Conference schedule linking sessions to times
- `accepted-papers-YEAR.json` - Papers exported from HotCRP (sanitized)
- `posters-YEAR.json` - Poster submissions
- `footer.yml` - Footer links and social media

### Theme Assets

```
themes/devfest-theme-hugo/
├── layouts/             # Hugo templates
│   ├── _default/baseof.html  # Base template
│   ├── partials/        # Reusable components (header, footer, css, js)
│   └── shortcodes/      # Custom shortcodes (jumbo, button-link, home-info, etc.)
└── assets/
    ├── style/           # SCSS files (theme-YEAR.scss per year)
    └── icons/           # SVG icons (add new icons here)
```

### Front Matter Conventions

Sessions require `type: sessions` to render properly. Speakers use `key` field for reference in session's `speakers` array.

## Shortcode Syntax

- `{{% shortcode %}}` - produces markdown content (e.g., `jumbo`)
- `{{< shortcode >}}` - produces HTML output (e.g., `button-link`)

## Adding a New Conference Year

1. Copy entire `content/YEAR/` from previous year
2. Create `[params.YEAR]` section in `hugo.toml` with city, themeColor, logos
3. Create `[[menu.YEAR]]` entries in `hugo.toml`
4. Create `theme-YEAR.scss` in `themes/devfest-theme-hugo/assets/style/` (set `--primary` color)
5. Update `params.currentYear` and redirects when ready to "go live"

## Build & Deploy

- Deploys automatically to Netlify on push to main branch
- Hugo version controlled in `netlify.toml` (currently 0.140.0)
- Build command installs Dart Sass and runs `hugo --gc --minify`
