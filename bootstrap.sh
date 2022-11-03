#!/bin/sh
# Let's use Python 3.8 here, to make it easier to switch between Plone 5.2 and 6.0.
python3.8 -m venv .
./bin/pip install -r requirements.txt
./bin/buildout -c buildout.cfg
