# SNID SAGE Documentation

This directory contains the source files for the SNID SAGE documentation website.

## Structure

- `index.md` - Main landing page
- `installation/` - Installation guides
- `quickstart/` - Getting started tutorials
- `gui/` - GUI interface documentation
- `cli/` - Command-line interface documentation
- `ai/` - AI integration features
- `data/` - Data format specifications
- `tutorials/` - Step-by-step tutorials
- `reference/` - API reference and technical details
- `dev/` - Development and contribution guides

## Building Locally

To build the documentation locally:

```bash
# Install MkDocs and Material theme
pip install mkdocs-material

# Build the site
mkdocs build

# Serve locally (optional)
mkdocs serve
```

## Deployment

The documentation is automatically deployed to GitHub Pages via GitHub Actions when changes are pushed to the main branch.

The live site is available at: https://fiorenst.github.io/SNID-SAGE

## Configuration

The documentation is configured via `mkdocs.yml` in the project root. 