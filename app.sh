#!/bin/bash
# This script will start the server
#INFLUX_CONFIG_FILE="/opt/home/jupyter-bdpoc/workspace/bdpoc-datahub/assets/files/config.ini" ./.datahub/bin/streamlit run visualize/main.py --server.enableCORS=false --server.enableXsrfProtection=false
./.datahub/bin/streamlit run visualize/main.py --server.enableCORS=false --server.enableXsrfProtection=false
