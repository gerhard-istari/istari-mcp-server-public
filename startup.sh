#!/bin/bash
cd $(dirname $0)
source venv/bin/activate
poetry run python server.py
