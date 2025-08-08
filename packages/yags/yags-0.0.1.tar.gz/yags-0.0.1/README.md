![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)
![100% Local](https://img.shields.io/badge/privacy-100%25%20local-brightgreen)
![Security Policy](https://img.shields.io/badge/security-policy-brightgreen)

# YAGS - Yet Another Git Squasher

Interactive tool for squashing Git commits with visual browsing and undo functionality.

<div align="center">
   <img src="assets/demo.gif" alt="demo" width="600">
</div>

## Installation

```bash
git clone https://github.com/duriantaco/yags.git
cd yags
pip install -e .
```

## Usage

```bash
yags
yags --commits 3        # squash last 3 commits  
yags --dry-run          # show what would happen
yags --undo             # undo last squash
yags --limit 50         # show up to 50 commits
```

## Options

1. **Squash since main branch** - Auto finds merge base
2. **Squash last N commits** - Enter number of commits
3. **Browse and pick visually** - Navigate with `n`/`p`, inspect with `i <num>`

## Quick start

You can run `yags` and select whichever options suit you the best. We will show you 

## Safety

- Auto backup branches before squashing
- `yags --undo`