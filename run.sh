#!/bin/bash

# Kill any existing processes
pkill -f "backend.main"
pkill -f "streamlit run"

echo "Starting Backend..."
python3 -m backend.main &

echo "Waiting for backend to start..."
sleep 3

echo "Starting Frontend..."
streamlit run frontend/streamlit_app.py --server.port 8501
