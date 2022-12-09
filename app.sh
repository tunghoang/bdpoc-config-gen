#!/bin/bash
# This script will start the server
./.datahub/bin/streamlit run visualize/app.py --server.enableCORS=false --server.enableXsrfProtection=false
