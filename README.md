# Articles

This repository contains articles and blogs written on various topics

## Google Blogger Tips :bulb:

1. To convert markdown to html, use [markdown-to-html](https://it-tools.tech/markdown-to-html) converter by IT-Tools.tech. It is better compared to VS Code extension especially when it comes to handing mermaid.js graphs

1. To highlight syntax after converting markdown to html, use below three cdns:

    ```html
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>

    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>

    <link
        rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism.min.css"
    />
    ```

    </br>

1. If the article contains `mermaid` graphs, to render it properly on html webpage, use below cdn:

    ```html
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    </script>
    ```

1. Write custom URL in the permalink section of the blogger editor. Otherwise blogger generates url from title, if the title contains non-ASCII characters, it discards those characters.

1. It is possible to schedule publication of the blog posts.

1. The theme used for the blog is "Notable Light", CSS styles used to customize the appearance and layout of the theme are stored here: [Notable_light_theme_styles.css](./Google_Blogger/Notable_light_theme_styles.css)
