#!/bin/bash
# Pepper V6 — one-click code protection. © 2026 Lamya F. H. Ali
set -e
cd "$(dirname "$0")/.."
echo "Installing build tools..."
pip install cython setuptools >/dev/null 2>&1
echo "Compiling to native binaries..."
python cython_build/setup_cython.py build_ext --inplace
echo "Cleaning C intermediates..."
find . -name "*.c" -path "*/app/*" -delete 2>/dev/null || true
find frontend -name "*.c" -delete 2>/dev/null || true
echo ""
echo "✓ Done. Native .so files created."
echo "To hide source, delete the matching .py files (keep pepper_app.py + theme.py + main.py)."
echo "© 2026 Lamya F. H. Ali"
