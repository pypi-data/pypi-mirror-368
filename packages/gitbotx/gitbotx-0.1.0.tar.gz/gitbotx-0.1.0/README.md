# gitbotx

[![PyPI Version](https://img.shields.io/pypi/v/gitbotx)](https://pypi.org/project/gitbotx)  

## Overview

**gitbotx** is a lightweight, context-aware CLI tool designed to analyze the current state of your Git repository and provide actionable suggestions for your next Git commands. It also helps automate common workflows such as syncing branches and generating commit messages, saving you time and reducing errors.

---

## Features

- Shows unstaged, staged, and untracked files count  
- Displays current branch and remote ahead/behind status  
- Suggests Git commands like `git add`, `git commit`, `git pull`, and `git push`  
- Generates simple commit message templates based on staged files  
- Automates `fetch`, `rebase`, and `push` operations with a single `sync` command  
- Interactive prompts for resolving rebase conflicts  

---

## Installation

Install from PyPI:

```bash
pip install gitbotx
````

Or install from source:

```bash
git clone https://github.com/parikshit-06/gitbotx.git
cd gitbotx
pip install -e .
```

---

## Usage

Run the tool inside a Git repository folder:

```bash
gitbotx --status
```

Get a suggested commit message based on staged changes:

```bash
gitbotx --commit-msg
```

Automatically fetch, rebase, and push your branch:

```bash
gitbotx --sync
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---