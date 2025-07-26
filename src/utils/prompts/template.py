"""
Prompt templates and schema for document image translation tasks.
"""

import os
from utils.utils import read_json

schema = read_json(os.path.join(os.path.dirname(__file__), "schema.json"))
"""
Loaded JSON schema for translation output.
"""

html_styles = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        /* Document Layout - A4 Size */
        @page {
            size: A4;
            margin: 2.54cm 2.54cm 2.54cm 2.54cm; /* 1 inch margins */
        }

        /* Base Document Styles */
        * {
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #333333;
            background-color: #ffffff;
            max-width: 21cm; /* A4 width */
            margin: 0 auto;
            padding: 2.54cm;
            min-height: 29.7cm; /* A4 height */
        }

        /* Color Palette Variables */
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --accent-color: #e74c3c;
            --text-color: #333333;
            --text-light: #666666;
            --background-color: #ffffff;
            --background-light: #f8f9fa;
            --border-color: #dee2e6;
            --code-background: #f4f4f4;
            --table-stripe: #f9f9f9;
        }

        /* Typography Hierarchy */
        h1, h2, h3, h4, h5, h6 {
            color: var(--primary-color);
            font-weight: bold;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            page-break-after: avoid;
        }

        h1 { font-size: 18pt; }
        h2 { font-size: 16pt; }
        h3 { font-size: 14pt; }
        h4 { font-size: 13pt; }
        h5 { font-size: 12pt; }
        h6 { font-size: 11pt; }

        p {
            margin: 0.5em 0;
            text-align: justify;
        }

        /* Lists */
        ul, ol {
            margin: 0.5em 0;
            padding-left: 2em;
        }

        li {
            margin-bottom: 0.25em;
        }

        /* Code Blocks and Inline Code */
        code {
            font-family: 'Courier New', monospace;
            background-color: var(--code-background);
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 11pt;
            color: var(--accent-color);
        }

        pre {
            background-color: var(--code-background);
            border: 1px solid var(--border-color);
            border-radius: 5px;
            padding: 1em;
            overflow-x: auto;
            margin: 1em 0;
            page-break-inside: avoid;
        }

        pre code {
            background: none;
            padding: 0;
            color: inherit;
        }

        /* Syntax Highlighting Classes */
        .hljs-keyword { color: #0066cc; font-weight: bold; }
        .hljs-string { color: #009900; }
        .hljs-comment { color: #808080; font-style: italic; }
        .hljs-number { color: #cc6600; }
        .hljs-function { color: #9932cc; }
        .hljs-variable { color: #cc0000; }

        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1em 0;
            page-break-inside: avoid;
            font-size: 11pt;
        }

        th, td {
            border: 1px solid var(--border-color);
            padding: 0.5em;
            text-align: left;
            vertical-align: top;
        }

        th {
            background-color: var(--primary-color);
            color: white;
            font-weight: bold;
        }

        tr:nth-child(even) {
            background-color: var(--table-stripe);
        }

        /* Responsive Tables */
        .table-container {
            overflow-x: auto;
            margin: 1em 0;
        }

        /* Images */
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em auto;
            border: 1px solid var(--border-color);
            border-radius: 5px;
        }

        .image-caption {
            text-align: center;
            font-style: italic;
            color: var(--text-light);
            font-size: 10pt;
            margin-top: 0.5em;
        }

        /* Blockquotes */
        blockquote {
            border-left: 4px solid var(--secondary-color);
            margin: 1em 0;
            padding-left: 1em;
            color: var(--text-light);
            font-style: italic;
        }

        /* Links */
        a {
            color: var(--secondary-color);
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        /* Special Elements */
        .highlight {
            background-color: #ffff99;
            padding: 0.1em 0.2em;
        }

        .note {
            background-color: var(--background-light);
            border: 1px solid var(--border-color);
            border-radius: 5px;
            padding: 1em;
            margin: 1em 0;
        }

        .warning {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
        }

        .error {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }

        /* Print Styles */
        @media print {
            body {
                margin: 0;
                padding: 1cm;
            }

            h1, h2, h3, h4, h5, h6 {
                page-break-after: avoid;
            }

            pre, table, img {
                page-break-inside: avoid;
            }

            a {
                color: inherit;
                text-decoration: none;
            }

            a:after {
                content: " (" attr(href) ")";
                font-size: 9pt;
                color: var(--text-light);
            }
        }

        /* Mobile Responsiveness */
        @media screen and (max-width: 768px) {
            body {
                padding: 1em;
                font-size: 14px;
            }

            table {
                font-size: 12px;
            }

            pre {
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <!-- Content will be inserted here -->
</body>
</html>
"""

system_translate_and_html_prompt = f"""
You are an expert document translator and layout designer. Your job is to translate the following markdown content to <target-language> and generate a complete HTML document using the default template.
Preserve all formatting, tables, code blocks, and images. For each image, use the provided image ID and dimensions (width x height in px) to set the appropriate attributes in the HTML <img> tags.

DEFAULT DOCUMENT TEMPLATE:
Generate HTML with the following default styling template. You may add additional styles specific to the content, but preserve these base styles:

```html
{html_styles}
```

STYLING INSTRUCTIONS:
- Use the default template above as your base
- You may add content-specific styles within <style> tags in the <head> section
- DO NOT remove or override the base document styles (body, typography, colors, etc.)
- For content-specific styling, use additional CSS classes or inline styles
- Maintain the A4 document format and professional appearance
- Ensure all tables, code blocks, and special elements work with the base template

When generating the HTML, pay special attention to:
- Code blocks: Render them with proper syntax highlighting using the provided classes and preserve formatting.
- Tables: Wrap in .table-container div for responsiveness, ensure they maintain structure and use the base table styling.
- Images: Use the provided dimensions, place contextually, and add .image-caption class for captions if needed.
- Layout: Maintain clean, readable, visually balanced layout using the document template structure.
- Special elements: Use .note, .warning, .error classes for callouts and special content blocks.

Here is the list of images and their dimensions (image_id: width x height in px):
<image-dimensions-list>

Generate complete HTML document using the template structure. Do not add any extra commentary or explanation—return only the HTML output in <target-language>.
"""

user_translate_and_html_prompt = """
Translate the following markdown string to <target-language> and convert it to HTML using the default document template. Ensure all formatting, tables, code blocks, and images are preserved and properly styled.
For each image, set the HTML <img> tag's id attribute to the image's id as provided in the image list.

<markdown-content>

Return only the complete HTML document in <target-language> without any additional explanations or comments.
"""
