#!/bin/bash

./backend/build/main &

# Avvia uno script Python
python3 frontend/client.py &

wait