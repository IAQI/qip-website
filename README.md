# QIP website

[![Netlify Status](https://api.netlify.com/api/v1/badges/2d3b6d5c-0a7d-4fea-a32e-9a1f7cbaa79a/deploy-status)](https://app.netlify.com/sites/qip-website/deploys)

Hugo-powered website for the Quantum Information Processing (QIP) conference, live at https://qipconference.org/ (and https://qip-website.netlify.app). QIP is a leading annual international conference for students and researchers working in the theoretical aspects of quantum information science.

[Hugo](https://gohugo.io/) is a fast static website generator. Deploy previews and production builds are generously hosted by [Netlify](https://www.netlify.com/) under an [Open Source Plan](https://www.netlify.com/legal/open-source-policy/) :heart:!

This repository was forked from https://github.com/IAQI/tqc-website for the QIP conference website. The TQC repository originated from https://github.com/QCrypt/qcrypt-website, which has been maintained since 2020 by [Christian Schaffner](https://github.com/cschaffner).

## History
Originally based on the Hugo template from https://github.com/GDGToulouse/devfest-theme-hugo
adapted from the fork by the cloudnative-amsterdam people: https://github.com/cloudnative-amsterdam/public-website

The predecessor QCrypt repository used to run https://2020.qcrypt.net, https://2021.qcrypt.net, and https://2022.qcrypt.net.

Since 2023, the theme submodule is included directly in this git repository.

The QIP site follows a multi-year structure with one main codebase and year-specific content, broadly modeled after the IACR flagship websites like https://eurocrypt.iacr.org/2024, https://eurocrypt.iacr.org/2025, https://crypto.iacr.org/2023/, https://asiacrypt.iacr.org/2024/, and the *odd one out (in terms of design)* https://crypto.iacr.org/2024/.


## Building this conference site from scratch
> [!WARNING]
> This has only been tested on macOS and Windows so far, so sharing your experience with other platforms here is very appreciated!

1. Install [Hugo](https://gohugo.io/installation/) and [Dart Sass](https://gohugo.io/hugo-pipes/transpile-sass-to-css/)
2. Clone this repo:

```bash
$ git clone https://github.com/IAQI/qip-website.git
```

3. It's done. Just start Hugo server to see the site live!

```bash
$ cd qip-website
$ hugo server
``` 

4. Edit the Markdown source files ending in `.md` in the `/content/` subdirectories to make changes to the site. You might also have to edit `.json` and `.yml` files in the `/data/` subdirectory. As long as the Hugo server is running, your changes should be visible immediately at http://localhost:1313/.

5. Using a suitable editor like [Visual Studio Code](https://code.visualstudio.com/) allows you to easily search across all source files and find the correct file to edit.

6. When you are happy with the result, commit the changes to the repository. Netlify creates a deploy preview, and production deployments publish the site at https://qipconference.org/. If you have the proper rights, you can see the deployment logs on [Netlify](https://app.netlify.com/sites/qip-website/deploys).


## Customizing the theme
Is described in the [README.md](https://github.com/IAQI/qip-website/blob/main/themes/devfest-theme-hugo/README.md) of the theme.

## High-level overview
This site is built with modern web technologies:

* **Hugo**: [Hugo](https://gohugo.io/) is a fast website builder that turns simple text files into a complete website. It watches for changes in your content and instantly updates the site while you work.

* **JamStack Architecture**: The website follows a modern approach where all pages are created ahead of time. This makes the site fast, secure, and reliable since there's no need to generate pages when visitors arrive. Learn more about [JamStack](https://jamstack.org/).

* **Content Management**: Content is written in [Markdown](https://www.markdownguide.org/) files that are easy to edit and track changes. Multiple people can work on the site together through [GitHub](https://github.com/), and all changes are safely stored and can be reviewed.

* **Styling with CSS/SASS**: The website's appearance is controlled through [CSS](https://developer.mozilla.org/en-US/docs/Web/CSS) and [SASS](https://sass-lang.com/) style files that make it easy to maintain a consistent look. Each conference year can have its own visual theme, and the site works well on all screen sizes.

* **Netlify Hosting**: [Netlify](https://www.netlify.com/) automatically builds and publishes the website whenever changes are made and committed to this repository. It ensures the site is secure, fast, and available worldwide through its global network.

This combination of tools creates a website that's fast, secure, and easy to maintain by the conference organizers. Sounds great? Check out [this guided walk](https://github.com/IAQI/qip-website/tree/main/themes/devfest-theme-hugo#a-guided-walk-through-the-ingredients) to learn how it actually works in more detail.

## Setting up the next conference year based on previous years

### design 
1. create a new logo, using previous editions for inspiration.
2. choose a background image for the main site, e.g. [2027](/static/images/2027/) or [2026](/static/images/2026/)
3. and make a related banner, using previous editions as examples.
4. pick a related themecolor, like `#0099cc` or `#ac191c`.

### create new subdirectories for content
1. It's probably easiest to copy the entire content folder from a previous year like [/content/2027](/content/2027) and start adjusting from there
2. create a new year subfolder in [/static/images](/static/images)
3. put the images (logo, background image, banner) from above to this folder

### add info to main config file [/hugo.toml](/hugo.toml) 
4. In `[params]`, leave `currentYear` and `date` as they are right now. Change them only when the new year site is ready.
5. add a section `[params.<YEAR>]` and supply the required information
6. the timeanddate_cityid can be inferred from https://www.timeanddate.com/worldclock/personal.html by looking at the link after clicking on "Share This Personal World Clock" 
7. Under `[menu]`, create a new `[[menu.<YEAR>]]` structure following the existing yearly menus.

### adjust content files
1. Go through all `.md` files in the new `content/<YEAR>/` directory and the `_index.md` files in the subdirectories, and adjust the front matter.
2. Adjust the `menu:` sub-entry to use the new year instead of the copied one.
3. put `draft: true` in case you want to disable the page for the time being.
4. In general, whenever the year is passed on as a parameter, you might have to update it. Searching inside the newly copied year directory for the previous year and replacing the correct occurrences is usually a good strategy.

### create new style file
1. In [/themes/devfest-theme-hugo/assets/style/](/themes/devfest-theme-hugo/assets/style/), duplicate the most recent yearly stylesheet (for example [theme-2027.scss](/themes/devfest-theme-hugo/assets/style/theme-2027.scss)) and rename it for the new year.
2. adjust the last line to set the `--primary:` variable in `root` to the themecolor picked above.


### Steps you will need help with
1. on https://github.com/orgs/IAQI/teams, create a new team `qip-<year>`
2. add admins
3. add repositories
5. in Netlify, add the new admin as collaborator to the `qip-website` site
1. on https://api.slack.com/apps/A01P06YNCCU/incoming-webhooks , create a new Webhook (on the bottom of the page)
1. paste the Webhook URL into Netlify site notifications for the current QIP site (for successful and failed deploys)
1. add admins to Slack channel
3. We probably need new email addresses like `<year>@qipconference.org` and `pcchairs<year>@qipconference.org`.
3. connect new admins to admins from last year
4. Is it time to update the hugo version? check what needs to be updated.

### bump year
Once the new site is ready to be "promoted" to be the current year, make the following changes:
1. In hugo.toml, in [params], change the currentYear and date
2. In `[[server.redirects]]`, change the forward target to the new current year.
3. In [/netlify.toml](/netlify.toml), adjust the redirect as well.


## Later Updates

### call for papers, venue updates, registration
1. adjust the corresponding `.md` file in the current year directory, possibly by switching back `draft: false` and adjusting the content from the previous year
2. **all changes to the website should be mentioned in a table with "Website Updates"**, for the convenience of website visitors
3. The call-to-action buttons on the main site can be adjusted depending on the news.

### tutorial, invited speakers, panelists are known
1. update the `.md` files in the current year `speakers/` directory
2. remove previous images from the images subdirectory, upload new ones, and make sure the photoURL field of the speaker is pointing there.
3. Use sensible names for the .md files, like eleni_diamanti.md 
4. Per speaker, create a matching session in the current year `sessions/` directory, using the examples from previous years.

### accepted papers and posters are known
1. Get accepted papers as json export from hotcrp from PC chair
2. run [this Python script](/scripts/sanitize_hotcrp_json.py) to sanitize the output, removing all emails, PC conflicts, etc.
3. put the resulting file into [data](/data) using the existing naming convention for accepted papers

Proceed accordingly with the list of accepted posters.

### creating a schedule
1. duplicate the previous year's schedule file in [/data](/data) and rename it for the new year
2. make sure all sessions exist
3. Adjust the id's of the contributed papers in the sessions with contributed papers


## More detailed explanations of the different content sections

Have a look at the [Hugo Documentation](https://gohugo.io/documentation/), ChatGPT is also quite knowledgable.

Hugo's favorite [Content format](https://gohugo.io/content-management/formats/) is markdown, and that's what we use throughout. For [data sources](https://gohugo.io/content-management/data-sources/) and config files, Hugo understands TOML, YAML, JSON, CSV, XML. We use the first three only.

Every content file contains a [front matter](https://gohugo.io/content-management/front-matter/), specifying metadata for the content, usually in yaml format. Important parameters are title, year, type, draft, menu. They influence how content is displayed.

> [!WARNING]
> In this site, we are deviating from the Hugo-recommended [Organization of content source](https://gohugo.io/content-management/organization/#organization-of-content-source), because our top levels in the `content/<DIRECTORIES>` are years, instead of topics. Therefore, the `.Section` variable is often our `$currentYear`.

The original Hugo template had multilingual support (French / English), but we have dropped this in the meanwhile, some reminders of these times are still around, though.

### Hugo Shortcodes
> [!NOTE]
> We often use [Hugo shortcodes](https://gohugo.io/content-management/shortcodes/) in this project. There are two different types:
> * `{{%  %}}` produces markdown content like the `jumbo` element on the main page.
> * `{{<  >}}` produces HTML output, e.g. used to produce links with `button-link` inside the `jumbo` element on the main page.
> Some shortcodes have closing brackets, using the markdown content enclosed between them (like `jumbo`), others don't (like `button-link`).

### file names
> [!IMPORTANT]
> Even though Hugo is quite forgiving, please use sensible and consistent file names for content pages, pictures etc. [This page](https://docs.hugoblox.com/reference/site-structure/) recommends to:
> - Stick to lowercase for all file names, including content files (`about.md`), layouts, and static assets (`images/logo.png`).
> - Use hyphens (`-`) or underscores (`_`) to separate words instead of spaces or capital letters (e.g., `my-article.md` or `my_article.md`).


### Menus in the header
See [Menus](https://gohugo.io/content-management/menus/) in the Hugo documentation. We are using a mix of "In side configuration" and "in front matter" menu definitions.

The basic structure of the top menu is copied from the IACR flagship conference websites (like https://eurocrypt.iacr.org/2024). The basic menu structure is defined in [/hugo.toml](/hugo.toml) under [menu]. We have a menu hierarchy for each year, but these basic entries should basically be the same every year. The items "Technical Program" and "Attend" do not correspond to actual pages, they are used as parent menu items for other pages.

The other items in the menu are defined in the front matter of content pages.

### Footer
The content of the footer is specified in [/data/footer.yml](/data/footer.yml). The "social share" options are currently disabled, the "social follow" options are Twitter and YouTube. 
> [!NOTE]
> Maybe we want to move away from Twitter soon?

The footer rarely needs to be changed. It automatically links to the charter, history and code of conduct of the current year. Just make sure that the content directory of the currentYear also contains these three files:
* `charter.md`
* `history.md`
* `code-of-conduct.md`
  
Copy them over from the previous year and make sure they are up to date!

It is a requirement by the Netlify Open Source plan to link to a code of conduct, so do not remove that part!

### Main page
The main home page per year is the `/content/YEAR/_index.md`, like [/content/2027/_index.md](/content/2027/_index.md). It has `type: home` and `layout: home` in the front matter.

It is the only page without a banner on top, as it starts with a [jumbo element](https://github.com/IAQI/qip-website/blob/main/themes/devfest-theme-hugo/README.md#jumbo-bloc) which takes as arguments the background image, label and logo. The content of it is the date, and various call to actions using button-links, which in turn take arguments like label, url, icon.

The following elements are:
* home-info: some basic information about QIP
* home-keydates: the two most important tables: one with key dates, one with website updates. Again, this is inspired by [the IACR pages](https://eurocrypt.iacr.org/2023/).
* home-location: image, address, and coordinates of the venue
* partners: list of sponsors, or call for sponsors

### Team
One of the first content pages to update and display. Follow the example of previous years.

All committees get their own subfolder, and there is an image folder for all portrait pictures. Ensure the photoURL front matter item points to the correct picture. When creating and naming new files, follow [reasonable conventions](#file-names).

### Partners / Sponsors
The subdirectory is called `partners` but on the website, we commonly refer to them as "Sponsors". There are subfolders for the different categories. Logos should go into the `logos/` subfolders, and the `logo` front matter entry should refer to that logo file.

### Speakers & Sessions
Very similar to the administration of the [team](#Team).

Make sure to create sessions for all speakers. In the session front matter, specify one or more speakers by referring to the `key` entry in the speaker front matter.

The front matter of sessions should specify the `year`, `format` (like `contributed`, `invited`, `industry`, `tutorial` etc.). The `type` has to be `sessions` in order to render the session properly.

For sessions with contributed talks, specify the paper ids once they are known.

There is an overview of speakers (for example [2027](/2027/speakers/)) and an overview of sessions (for example [2027](/2027/sessions/)); both should be added to the "Technical Program" menu when ready.

### Schedule
Once a schedule is drawn up, insert the session names and start times into the new year's `data/schedule-<YEAR>.yml` file like in previous years. A schedule is then automatically generated and can be added to the "Technical Program" submenu by setting `draft: false` in the corresponding `content/<YEAR>/schedule/_index.md` file.
