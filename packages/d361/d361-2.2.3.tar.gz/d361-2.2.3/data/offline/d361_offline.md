The tool: 

- map: url = "https://docs.document360.com/sitemap-en.xml" # sitemap that defines the scope of the job (all links)
- nav: url # page to gather the nav, use the first link from sitemap if not provided
- dir: str | Path # work folder, use cwd + domain of the map url (like "./site.document360.com") 
- css: str | Path # path to a css file to use for the site.html file, `d361_offline` by default.
- effort: bool = False # try hard to mirror all map links in the nav

The tool should: 

## prep phase

- Read the `map` and use it to build a flat target list of URLs

- Inspired by d360_getsitenav.py , visit the `nav` page and extract the nav. Try to map between the page URLs between the map and the map. If effort is True, try harder to map all the links from the map. 

- FIXME: In the `dir`, write a `nav.json`, `nav.md` and `nav.html` file

## fetch phase

- Create a `html` and `md` folder in the `dir`

- Inspired by `d360_makesite.py`, mirror all the pages from the `map` into the `html` folder, but for each page only store the H1 and the article elements. Use `map` because that's flat and "authoritative". 

- Convert each one to markdown in `md`.

## build phase
- When we have all pages, and the nav, we can try to build the final files: 

- Inspired by `d360_makesite.py`, create a single `site.html` file and a `site.md` file. 

