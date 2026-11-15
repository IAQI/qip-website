# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Hugo-powered static website for the Quantum Information Processing (QIP) conference series. The site is hosted on Netlify. Its theme (layouts, styles, schedule and accepted-papers templates, pipeline scripts) is the shared Hugo module github.com/IAQI/conference-theme, also used by QCrypt and TQC, pinned in go.mod / go.sum and downloaded at build time (needs Go). Its README documents the pipeline scripts (HotCRP export -> data files -> schedule -> presenters -> videos) and its docs/website-guide.md the site structure. Files in this repository's layouts/, assets/ and i18n/ override the module's.

## Development Commands

```bash
# Start local development server (site available at http://localhost:1313/)
hugo server

# Build the site to /public directory
hugo build

# Install PostCSS dependencies (required for theme editing)
npm clean-install

# Test SASS compilation independently
# (styles are compiled by Hugo from assets/style/theme-2027.scss, which starts with @use "theme")
```

Required tools: Hugo, Dart Sass, Node.js (for theme development)

## Architecture

### Multi-Year Structure

The site deviates from standard Hugo organization - top-level directories in `content/` are years (2027; earlier years are archived on qip.iaqi.org), not topics. The `.Section` variable often equals `$currentYear`.

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

The theme lives in the conference-theme module. This site keeps only:

```
assets/style/theme-YEAR.scss   # @use "theme"; then the year's colours (--primary, --header-txt, --button-bg, --box-bg, ...)
assets/style/...               # the few theme styles QIP overrides (see README)
layouts/partners/list.html     # QIP's sponsors page
i18n/en.toml                   # "QIP Charter", "QIP History"
```

To work on the module itself locally: HUGO_MODULE_REPLACEMENTS="github.com/IAQI/conference-theme -> ../conference-theme" hugo server

### Front Matter Conventions

Sessions require `type: sessions` to render properly. Speakers use `key` field for reference in session's `speakers` array.

## Shortcode Syntax

- `{{% shortcode %}}` - produces markdown content (e.g., `jumbo`)
- `{{< shortcode >}}` - produces HTML output (e.g., `button-link`)

## Adding a New Conference Year

Run `python3 ../conference-theme/scripts/new_year.py --year YEAR` (copies the previous year's general pages as drafts, the hugo.toml blocks and the year's stylesheet), then follow its checklist; see the module's docs/website-guide.md.

## Build & Deploy

- Deploys automatically to Netlify on push to main branch
- Hugo version controlled in `netlify.toml` (currently 0.140.0)
- Build command installs Dart Sass and runs `hugo --gc --minify`; `GO_VERSION` in `netlify.toml` lets Hugo download the theme module
