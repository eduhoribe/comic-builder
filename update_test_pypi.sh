#!/usr/bin/env sh

rm -rf dist && python setup.py sdist bdist_wheel && python -m twine upload --repository testpypi dist/*
