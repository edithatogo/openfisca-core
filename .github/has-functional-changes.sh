#! /usr/bin/env bash

IGNORE_DIFF_ON="README.md CONTRIBUTING.md Makefile .gitignore LICENSE* .github/* tests/* openfisca_tasks/*.mk tasks/*.mk publiccode.yml"

if last_tagged_commit=$(git describe --tags --abbrev=0 --first-parent 2>/dev/null)
then
  comparison_commit=$last_tagged_commit
elif [[ -n ${GITHUB_BASE_REF:-} ]] && git rev-parse --verify --quiet "origin/$GITHUB_BASE_REF" >/dev/null
then
  comparison_commit=$(git merge-base HEAD "origin/$GITHUB_BASE_REF")
else
  comparison_commit=$(git rev-parse HEAD^)
fi

if git diff-index --name-only --exit-code "$comparison_commit" -- . `echo " $IGNORE_DIFF_ON" | sed 's/ / :(exclude)/g'`  # Check if any functional file has changed since the comparison commit.
then
  echo "No functional changes detected."
  exit 1
else echo "The functional files above were changed."
fi
