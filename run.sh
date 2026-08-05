#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    python3.11 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

export PYTHONPATH="$DIR"
./venv/bin/python main.py
