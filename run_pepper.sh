#!/bin/bash
# Pepper Clinical V6 — launcher. © 2026 Lamya F. H. Ali
cd "$(dirname "$0")/frontend"
export PEPPER_SERVER="${PEPPER_SERVER:-http://127.0.0.1:8000}"
python pepper_app.py
