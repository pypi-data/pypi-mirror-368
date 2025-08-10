# markitdown-cli

[![PyPI version](https://badge.fury.io/py/markitdown-cli.svg)](https://badge.fury.io/py/markitdown-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight CLI wrapper for Microsoft's `markitdown` library. Convert any webpage into a clean Markdown file directly from your terminal.

## Installation

The recommended way to install `markitdown-cli` is using `pipx`:

```bash
pipx install markitdown-cli
```

Alternatively, you can install it with `pip`:

```bash
pip install markitdown-cli
```

## Usage

The primary use case is to provide a URL to the tool. `markitdown-cli` will then download the page, convert it to Markdown, and save it as a file in your current directory.

### Basic Usage

```bash
markitdown-cli https://example.com/article
```

This will create a file named `article.md` in the current directory.

### Interactive Title Suggestion

The tool will suggest a title for the Markdown file based on the URL. You can either accept the suggestion by pressing Enter, or you can type a custom title.

```
$ markitdown-cli https://collabfund.com/blog/the-dumber-side-of-smart-people/
Suggested title [the-dumber-side-of-smart-people]:
Wrote: the-dumber-side-of-smart-people.md
```

### Specifying an Output Directory

You can use the `-o` or `--outdir` option to specify a different directory to save the Markdown file.

```bash
markitdown-cli https://example.com/article -o ./my-articles
```

This will create `article.md` inside the `my-articles` directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.