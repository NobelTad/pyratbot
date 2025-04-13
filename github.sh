#!/bin/bash

# Ask for commit message
read -p "Enter commit message: " commit_msg

# Ask which file(s) to commit
read -p "Enter file(s) to commit (space-separated): " files

# Git commands
git add $files
git commit -m "$commit_msg"
git push origin main
