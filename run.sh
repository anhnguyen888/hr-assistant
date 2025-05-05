#!/bin/bash
cd ~/hr-assistant
source venv/bin/activate
cd src
streamlit run app.py --server.port=8501
