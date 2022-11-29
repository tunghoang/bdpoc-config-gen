#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
. ../../.datahub/bin/activate
# This script will compile components into a wheel file
echo "Compiling components..."
python setup.py bdist_wheel
rm -rf build
rm -rf *.egg-info
echo "Done compiling components."
echo "Installing components..."
pip uninstall custom_components
pip install dist/*.whl 
deactivate
