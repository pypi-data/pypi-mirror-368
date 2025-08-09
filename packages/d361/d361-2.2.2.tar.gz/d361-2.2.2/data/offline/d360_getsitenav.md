
# d360_getsitenav

Python Fire CLI tool that uses Playwright, which will: 

- Go to https://docs.document360.com/docs/
- Focus on #left-panel > div.catergory-list > site-category-list-tree-view > d360-data-list-tree-view
- Scroll all the way down and keep clicking the small triangles to recursively expand all items, and gather the links, gradually working your way upwards, until you have gathered all links from https://docs.document360.com/sitemap-en.xml (included). 

