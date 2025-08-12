#!/bin/bash

REPO="kovidgoyal/calibre"
FOLDER="recipes"
LOCAL_DIR="$HOME/.local/share/calibre-recipe-runner/$FOLDER"
API_BASE="https://api.github.com/repos/$REPO"

mkdir -p "$LOCAL_DIR"

DEFAULT_BRANCH=$(curl -s "$API_BASE" | jq -r '.default_branch')
COMMIT_SHA=$(curl -s "$API_BASE/branches/$DEFAULT_BRANCH" | jq -r '.commit.sha')

TREE_URL="$API_BASE/git/trees/$COMMIT_SHA?recursive=1"
echo "🌳 Fetching full file tree from $DEFAULT_BRANCH ($COMMIT_SHA)..."

FILES=$(curl -s "$TREE_URL" | jq -r --arg folder "$FOLDER/" '
  .tree[]
  | select(.path | startswith($folder))
  | select(.type == "blob")
  | select(.path | endswith(".recipe") or endswith(".py"))
  | .path
')

echo "⬇️ Downloading recipe files..."
for FILE_PATH in $FILES; do
    RAW_URL="https://raw.githubusercontent.com/$REPO/$DEFAULT_BRANCH/$FILE_PATH"
    FILE_NAME=$(basename "$FILE_PATH")
    echo "Downloading $FILE_NAME..."
    curl -s -L "$RAW_URL" -o "$LOCAL_DIR/$FILE_NAME"
done

echo "✅ All non-PNG recipe files downloaded to $LOCAL_DIR."

