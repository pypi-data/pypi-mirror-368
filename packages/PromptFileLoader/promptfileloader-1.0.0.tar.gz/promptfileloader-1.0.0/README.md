# PromptFileLoader

A simple and efficient Python package to load prompt files in YAML or TXT format with built-in caching.

---

## Overview

`PromptFileLoader` helps you easy to load prompt files for your applications, supporting both:

- YAML files (`.yaml`, `.yml`) parsed into Python dictionaries or lists, and  
- Plain text files (`.txt`) loaded as strings.

It caches loaded files internally for faster repeated access without redundant disk reads.

---

## Features

- Supports YAML and TXT prompt files  
- Caching to optimize file loading performance  
- Easy to initialize with a custom prompts directory or default folder  
- Minimal dependencies (only requires PyYAML)  
- Clear error handling for missing files or unsupported extensions

---

## Installation

Install via pip:

```bash
pip install promptfileloader
