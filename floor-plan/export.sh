#!/bin/sh
# Regenerate the SVGs and re-export PNGs at 2x with headless Chrome.
cd "$(dirname "$0")" || exit 1
python3 generate.py || exit 1
size=$(sed -n 's/.*<svg[^>]*width="\([0-9]*\)" height="\([0-9]*\)".*/\1,\2/p' existing.svg | head -1)
for v in existing proposed; do
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=2 --window-size="$size" --screenshot="$PWD/$v.png" "file://$PWD/$v.svg" 2>/dev/null
done
ls -la existing.png proposed.png
