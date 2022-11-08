#!/bin/bash
# This script will compile components into a wheel file
python setup.py bdist_wheel
rm -rf build
rm -rf *.egg-info