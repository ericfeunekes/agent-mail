#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
skills_dir="$project_dir/.agents/skills/development-source"

if [ -d "$skills_dir/.git" ]; then
    git -C "$skills_dir" pull --ff-only origin main
else
    git clone --depth 1 --filter=blob:none --sparse --branch main \
        https://github.com/ericfeunekes/ai-marketplace.git "$skills_dir"
fi

git -C "$skills_dir" sparse-checkout set \
    plugins/software-development \
    plugins/collaboration \
    skills/testing
