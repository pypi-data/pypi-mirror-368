
# d360_makesite

Tool `d360_makesite.py` that uses Python Fire CLI that transforms the content of the downloaded Document360 documentation into one long HTML file and one long Markdown file.

## 1. Read the TOC

Read the TOC that's the outout of `d360_getsitenav.py`, which contains links a bit like (but not entirely that format): 

```
<li xmlns="http://www.w3.org/1999/xhtml">
          <a href="/docs/creating-a-sandbox-project">
            <span>Creating a sandbox project</span>
          </a>
        </li>
```

### 1.1. Parse the links

We have locally the subfolder `docs` and therer files like `creating-a-sandbox-project.html`. Adapt the TOC links to the file paths. 

## 2. Read each page

### 2.1. Extract the title

From each page, we extract the title, like:

```
#main-content > d360-article-header > div.d-flex.justify-content-between.align-items-center.mb-3 > h1
```

### 2.2. Extract the content

From each page, we extract the content, like:

```css-selector
#main-content > d360-article-header > div.d-flex.justify-content-between.align-items-center.mb-3 > h1
```

```xpath
//*[@id="main-content"]/d360-article-header/div[1]/h1
```

```html
<h1 _ngcontent-serverapp-c2150518017="" class="article-title"><!----> Creating a sandbox project <d360-copy-article-link _ngcontent-serverapp-c2150518017="" _nghost-serverapp-c478378359="" ngh="11"><button _ngcontent-serverapp-c478378359="" aria-label="Copy article link" class="btn btn-secondary btn-icon copy-article"><i _ngcontent-serverapp-c478378359="" class="fa-regular fa-link-simple"></i></button><!----></d360-copy-article-link><!----></h1>
```

### 2.3. Extract the article

```css-selector
#articleContent
```

```xpath
//*[@id="articleContent"]
```

```html
<article _ngcontent-serverapp-c3082681425="" id="articleContent" appglossaryrenderer="" appimageviewer="" apphighlight="" appeditor360tabs="" class="block-article"><p data-block-id="8963fc1c-9933-4271-aeba-f2278090bd13"><strong>Plans supporting for creating a Sandbox project</strong></p><div contenteditable="false" translate="no" data-snippet="Ent plan supported" class="fr-deletable" id="blocksnippet"><table style="width: 100%;"><thead><tr>(...)</editor360-faq><p data-block-id="cb4876bb-f3e2-4b8d-9b43-86ae2794270c"></p></article>
```

## 3. Compile a complete document

### 3.1. HTML document

```html
<html>
    <body>
        <aside>
            <nav>
                <!-- original nav but with relative links -->
            </nav>
        </aside>
        <main>
            <div id="#<!-- the original filename without the .html -->">
                <h1...>
                    <!-- the title -->
                </h1>
                <article...>
                    <!-- the article -->
                </article>
            </div>
            ...
        </main>
    </body>
</html>
```

### 3.2. Markdown document

The document above but transformed with `html2text`. 

----
