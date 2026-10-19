#!/usr/bin/env bash
# TFCI repository initialization. Run from inside this directory.
set -e
git init -b main
git add -A
git commit -m "TFCI Wave 0: instrument live - 23 events, 3 matured-cohort ratios, gate 14/14 green"
echo "Repository initialized. To publish to GitHub:"
echo "  A) gh repo create tfci --private --source=. --push   (requires gh CLI)"
echo "  B) git remote add origin <your-repo-url> && git push -u origin main"
