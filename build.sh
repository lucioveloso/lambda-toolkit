#!/usr/bin/env bash

rm -rf build_env/
rm -rf build/
rm -rf dist/
virtualenv build_env
source build_env/bin/activate
python2.7 setup.py sdist
pip install -r requirements.txt
python2.7 setup.py bdist_wheel
