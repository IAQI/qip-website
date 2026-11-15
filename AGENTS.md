# AGENTS.md: QIP website

Instructions for AI coding assistants (Claude Code, Codex, Cursor, Copilot, ...)
working on https://qipconference.org, and a checklist for the humans supervising them.
`CLAUDE.md` imports this file; edit this one.

## What this is

A Hugo site for QIP, the Quantum Information Processing conference. Content is organised by year:
`content/<year>/` holds one edition (2027 onwards; earlier years are archived
on https://qip.iaqi.org and redirected there in `netlify.toml`). `params.currentYear`
in `hugo.toml` is the edition the home page shows.

The theme (layouts, styles, shortcodes, schedule and accepted-papers templates,
and the pipeline scripts) is the shared Hugo module
[IAQI/conference-theme](https://github.com/IAQI/conference-theme), also used by
the QCrypt and TQC websites. It is pinned in `go.mod` / `go.sum`.

Read before making changes:

- **The website guide**, shared by all three sites: content structure, shortcodes,
  menus, home page, team, sponsors, speakers, a new year, colours.
  https://github.com/IAQI/conference-theme/blob/main/docs/website-guide.md
  (locally `../conference-theme/docs/website-guide.md`)
- **README.md** of this repository: what is specific to QIP: design of a new
  year, accounts to set up, the accepted papers → schedule → presenters → videos
  commands.

## Commands

```bash
hugo server                 # http://localhost:1313/ (needs Hugo extended, Dart Sass, Go)
hugo server -D              # include draft pages
# with a local clone of the module next to this repository:
HUGO_MODULE_REPLACEMENTS="github.com/IAQI/conference-theme -> ../conference-theme" hugo server
```

Before handing work back, build twice to a scratch directory (not `public/`) and
read the warnings:

```bash
hugo --gc -d /tmp/qip-website-check      # the live site: no new warnings, drafts absent
hugo --gc -D -d /tmp/qip-website-drafts  # everything, drafts included, renders
```

Then check that the links you added point to pages or files that exist.

## Rules

1. **Shared or site?** Changes to layouts, shortcodes, shared styles or the
   scripts go to the conference-theme module, not into this repository, unless
   they touch one of this site's own files (below). Once a module change is
   merged, update the pin here with
   `go get github.com/IAQI/conference-theme@<commit>` (`hugo mod get` does not
   work for this) and commit `go.mod` and `go.sum`.
2. **Never invent conference facts.** Dates, deadlines, venue, fees, hotels,
   committee members, speakers, sponsors and prizes come from the organizers.
   If you do not have them, write "TBA" or leave `<!-- TODO: ... -->`; do not
   fill in plausible-looking values. Never carry people, sponsors, hotels or
   prizes of the previous year over into a new one.
3. **A new year** starts with
   `python3 ../conference-theme/scripts/new_year.py --year <year>`, then work
   through the checklist it prints. New pages stay `draft: true` until the
   organizers approve them. Do not change `params.currentYear`, `params.date` or
   the `/` redirects in `hugo.toml` and `netlify.toml` until you are told that
   the new site goes live.
4. **No blanket year replacement.** History pages, archive redirects, past
   deadlines and links to earlier editions must keep their years. Change year
   references one at a time and look at each.
5. **Personal data:** raw HotCRP exports and registration lists stay in
   `private_data/` (git-ignored). Never put them in `data/`, a commit, a pull
   request or an external service.
6. **Tell visitors what changed:** every visible update gets a line in the
   "Website updates" table on the home page (`content/<year>/_index.html`).
7. **Git:** work on a branch and open a pull request; never push to `main` (that
   publishes https://qipconference.org) and leave merging to a human maintainer. Netlify builds
   deploy previews only for pull requests against `main`, and previews do not
   show draft pages: say so when asking someone to review drafts. Commit only
   the files you meant to change.

## This site

QIP keeps its own versions of a few theme files (the README lists them):
`assets/style/_root.scss`, `partials/_base.scss`, `_jumbo.scss`, `_type.scss`
and `layouts/partners/list.html` (the sponsors page). Fixes to those parts of
the shared theme do not reach QIP automatically.

`assets/style/theme-<year>.scss` sets the year's colours; QIP's top bar is
white, so it also sets `--header-txt`, `--button-bg`, `--box-bg` and friends.
`i18n/en.toml` names the charter and history pages. The home page is
`content/<year>/_index.html` (HTML, not Markdown).
