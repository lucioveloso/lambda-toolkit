#!/usr/bin/env bash

./build.sh
twine upload --config-file .pypirc dist/*
