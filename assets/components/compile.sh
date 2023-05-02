#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
# This script will compile components into a wheel file
echo "Compiling components..."
python setup.py bdist_wheel
#exit 0
rm -rf build
rm -rf *.egg-info
echo "Done compiling components."
echo "Installing components..."
. ../../.datahub/bin/activate
pip uninstall custom_components
pip install dist/*.whl 
deactivate
