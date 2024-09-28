# Articles

This repository contains articles and blogs written on various topics

## TIPS

1. To convert markdown to html, use [markdown-to-html](https://it-tools.tech/markdown-to-html) converter by IT-Tools.tech.

1. To highlight syntax after converting markdown to html, use below three cdns:

    ```html
    <link
        rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism.min.css"
    />
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
    ```

    </br>

1. If the article contains `mermaid` graphs, to render it properly on html webpage, use below cdn:

    ```html
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    </script>
    ```
