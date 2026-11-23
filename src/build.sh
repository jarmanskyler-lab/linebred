#!/bin/sh
# Builds dist/app.js from src/app.src.js (readable source) with esbuild minify.
set -e
cd "$(dirname "$0")/.."
mkdir -p dist
npx esbuild src/app.src.js --minify --charset=utf8 --target=es2020 --outfile=dist/app.js --log-level=warning
node --check dist/app.js
wc -c dist/app.js
