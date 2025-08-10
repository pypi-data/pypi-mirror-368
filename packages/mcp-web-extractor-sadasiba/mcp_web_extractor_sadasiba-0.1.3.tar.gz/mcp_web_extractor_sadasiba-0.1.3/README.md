# MCP Web Extractor (by sadasiba)

`mcp-web-extractor-sadasiba` is an MCP (Model Context Protocol) server that extracts clean text content from web pages for use by LLMs such as Claude.

It fetches HTML from a given URL, parses it with **BeautifulSoup**, and returns only the readable text.

---

## Features

- 🌐 Extracts readable text from any web page
- 🧹 Strips away HTML tags, scripts, and styling
- ⚡ Simple command-line interface
- 🤝 Works seamlessly with Claude's MCP integration

---

## Installation

You can install directly from [PyPI](https://pypi.org/project/mcp-web-extractor-sadasiba/):

```bash
pip install mcp-web-extractor-sadasiba
