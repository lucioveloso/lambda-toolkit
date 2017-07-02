#!/usr/bin/env bash

rm -rf env/
virtualenv env
rm -rf build/
rm -rf dist/
source env/activate
python2.7 setup.py sdist
pip install -r requirements.txt
python2.7 setup.py bdist_wheel
