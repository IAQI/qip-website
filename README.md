# QIP website

[![Netlify Status](https://api.netlify.com/api/v1/badges/2d3b6d5c-0a7d-4fea-a32e-9a1f7cbaa79a/deploy-status)](https://app.netlify.com/sites/qip-website/deploys)

Hugo-powered website for the Quantum Information Processing (QIP) conference, live at https://qipconference.org/ (and https://qip-website.netlify.app). QIP is a leading annual international conference for students and researchers working in the theoretical aspects of quantum information science.

[Hugo](https://gohugo.io/) is a fast static website generator. Deploy previews and production builds are generously hosted by [Netlify](https://www.netlify.com/) under an [Open Source Plan](https://www.netlify.com/legal/open-source-policy/) :heart:!

This repository was forked from https://github.com/IAQI/tqc-website for the QIP conference website. The TQC repository originated from https://github.com/QCrypt/qcrypt-website, which has been maintained since 2020 by [Christian Schaffner](https://github.com/cschaffner).

## History
Originally based on the Hugo template from https://github.com/GDGToulouse/devfest-theme-hugo
adapted from the fork by the cloudnative-amsterdam people: https://github.com/cloudnative-amsterdam/public-website

Since 2026, the theme is shared with the QCrypt and TQC websites as the Hugo module [IAQI/conference-theme](https://github.com/IAQI/conference-theme).

This site starts with QIP 2027. Earlier editions are archived on https://qip.iaqi.org; `/2015` to `/2026` on this site redirect there.

## Working on the site

**The [website guide](https://github.com/IAQI/conference-theme/blob/main/docs/website-guide.md)** (in the shared theme) explains everything that is the same for QCrypt, TQC and QIP: running the site locally, how the content is organised, shortcodes, menus, footer, home page, team, sponsors, speakers and sessions, setting up a new year, colours. In short:

```bash
git clone https://github.com/IAQI/qip-website.git
cd qip-website
npm clean-install  # PostCSS
hugo server        # needs Hugo (extended), Dart Sass and Go; see the guide
```

Push to a branch and open a pull request to get a Netlify deploy preview; merging into `main` publishes https://qipconference.org.

## Setting up the next year

Follow the guide's [new year](https://github.com/IAQI/conference-theme/blob/main/docs/website-guide.md#a-new-year) section (`new_year.py` copies the previous year's pages as drafts). QIP specifics:

### design
1. create a new logo, using previous editions for inspiration.
2. choose a background image for the main site and make a related banner, e.g. [2027](/static/images/2027/).
3. pick the colours: QIP 2027 has a white top bar (`--primary: #fdfdfd`) with blue and green accents, set with `--header-txt`, `--button-bg` and `--box-bg` in [assets/style/theme-2027.scss](assets/style/theme-2027.scss).

### Steps you will need help with
1. on https://github.com/orgs/IAQI/teams, create a new team `qip-<year>`
2. add admins and repositories to that team
3. in Netlify, add the new admin as collaborator to the `qip-website` site
4. on https://api.slack.com/apps/A01P06YNCCU/incoming-webhooks , create a new Webhook (on the bottom of the page)
5. paste the Webhook URL into Netlify site notifications for the current QIP site (for successful and failed deploys)
6. add admins to Slack channel
7. We probably need new email addresses like `<year>@qipconference.org` and `pcchairs<year>@qipconference.org`.
8. connect new admins to admins from last year
9. Is it time to update the hugo version? check what needs to be updated.

## Accepted papers, schedule, presenters and videos
The shared theme's [README](https://github.com/IAQI/conference-theme#from-accepted-papers-to-the-schedule) describes the pipeline, from the HotCRP export to a schedule with linked papers, presenters and videos. In short (run from this folder, with `conference-theme` cloned next to it):

1. **Accepted papers and posters:** `python3 ../conference-theme/scripts/sanitize_hotcrp_json.py private_data/hotcrp.json --decision accept --talk-type-from-decision --search-arxiv -o data/accepted-papers-2027.json` (same for `posters-2027.json`); `--talk-type-from-decision` sorts papers into long-plenary / plenary / talk for the accepted-papers page.
2. **Schedule:** fill in `program/program-2027.csv` (one row per slot; see the theme README), then `python3 ../conference-theme/scripts/generate_schedule.py --year 2027 --program program/program-2027.csv`
3. **Presenters:** `python3 ../conference-theme/scripts/quantumdb_presenters.py --venue qip --year 2027` once QIP 2027 is in QuantumDB, or `mark_presenters.py` with the registration export
4. **Videos:** `python3 ../conference-theme/scripts/fetch_videos.py --year 2027 --playlist <URL> --playlist <URL> ...` (one `--playlist` per track playlist of the QIP channel)

Raw HotCRP exports and registration lists contain personal data: keep them in `private_data/` (git-ignored), never in `data/`.

## What this site does differently
QIP keeps its own versions of a few theme files: the colours of the schedule categories (`assets/style/_root.scss`, `partials/_tags.scss`), talk durations (`partials/_type.scss`), the schedule styling (`pages/_schedule.scss`), wider dropdown menus (`partials/_header.scss`), the venue images and spacing (`partials/_base.scss`, `_jumbo.scss`), and the sponsors page without table of contents (`layouts/partners/list.html`). Fixes to these parts of the shared theme do not reach QIP automatically.
