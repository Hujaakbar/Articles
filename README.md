# Articles

This repository contains articles and blogs written on various topics

## Google Blogger Tips :bulb:

1. To convert markdown to html, use [markdown-to-html](https://it-tools.tech/markdown-to-html) converter by IT-Tools.tech. It is better compared to VS Code extension especially when it comes to handling mermaid.js graphs.
   Besides, it does not add any styles, so the output is a kind of agnostic and clean.

1. To highlight syntax after converting markdown to html, use either [hightlight.js](https://github.com/highlightjs/highlight.js) or [PrimsJS](https://github.com/PrismJS/prism):

    PrismJS:

    ```html
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>

    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>

    <link
        rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism.min.css"
    />
    ```

    </br>

    **Hightlight.js**

    hightlight.js has 3 advantages:

    - maintained more actively than PrismJS
    - more themes than PrismJS
    - Auto-detect language feature

    ```html
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-light.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>hljs.highlightAll();</script>
    ```

    The con is even though there are many themes to choose from, there is no really good one.
    Below are some of my current picks:
    - base16-windows-high-contrast-light
    - atom-one-light
    - stackoverflow-light
    - intellij-light
    - xcode
    - base16-humanoid-light
    - base16-summerfruit-light
    - vs
    - base16-humanoid-dark
    - atom-one-dark
    - night-owl
    - monokai-sublime
    - felipec

1. If the article contains `mermaid` graphs, to render it properly on html webpage, use below cdn:

    ```html
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    </script>
    ```

1. Write custom URL in the permalink section of the blogger editor. Otherwise blogger generates url from title, if the title contains non-ASCII characters, it discards those characters.

1. It is possible to schedule publication of the blog posts.

1. The theme used for the blog is "Notable Light", CSS styles used to customize the appearance and layout of the theme are stored here: [Notable_light_theme_styles.css](./Google_Blogger/Notable_light_theme_styles.css)
