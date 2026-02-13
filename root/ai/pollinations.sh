#!/bin/bash
# Copyright (C) 2026 Oleh Mamont
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org>.


apt update
apt install python3-pip python3-venv -y


#=================================================================
#----------------------- Pollinations API 4261 -------------------
#=================================================================

# Function for start Proxy Server
start_polligenapi_4261() {
    echo "=== Starting Polligen API 4261 ==="

    cd /root/ai/polligenapi4261
    # Creating or activating virtual environment
    if [ ! -d "/root/ai/polligenapi4261/polligen-venv" ]; then
        echo "Creating new virtual environment for Polligen API 4261..."
        /usr/bin/python3 -m venv /root/ai/polligenapi4261/polligen-venv
        source /root/ai/polligenapi4261/polligen-venv/bin/activate
        /root/ai/polligenapi4261/polligen-venv/bin/pip install --upgrade pip
        /root/ai/polligenapi4261/polligen-venv/bin/pip install fastapi uvicorn httpx sse-starlette pillow
    else
        echo "Activation present virtual environment for Polligen API 4261..."
        source /root/ai/polligenapi4261/polligen-venv/bin/activate
#        /root/ai/polligenapi4261/polligen-venv/bin/pip install --upgrade pip
#        /root/ai/polligenapi4261/polligen-venv/bin/pip install fastapi uvicorn httpx sse-starlette pillow
    fi

    echo "Starting Polligen API 4261 Server..."
    exec /root/ai/polligenapi4261/polligen-venv/bin/python3 /root/ai/polligenapi4261/polligen.py
}



#=================================================================
#--------------------- Pollinations API 4290 Free ----------------
#=================================================================

# Function for start Pollinations API Proxy Server
start_polligenapi_4290() {
    echo "=== Starting Polligen API 4290 Free ==="

    cd /root/ai/polligenapi4290-free
    # Creating or activating virtual environment
    if [ ! -d "/root/ai/polligenapi4290-free/polligen-venv" ]; then
        echo "Creating new virtual environment for Polligen API 4290 Free..."
        /usr/bin/python3 -m venv /root/ai/polligenapi4290-free/polligen-venv
        source /root/ai/polligenapi4290-free/polligen-venv/bin/activate
        /root/ai/polligenapi4290-free/polligen-venv/bin/pip install --upgrade pip
        /root/ai/polligenapi4290-free/polligen-venv/bin/pip install fastapi uvicorn httpx sse-starlette pillow
    else
        echo "Activation present virtual environment for Polligen API 4290 Free..."
        source /root/ai/polligenapi4290-free/polligen-venv/bin/activate
#        /root/ai/polligenapi4290-free/polligen-venv/bin/pip install --upgrade pip
#        /root/ai/polligenapi4290-free/polligen-venv/bin/pip install fastapi uvicorn httpx sse-starlette pillow
    fi

    echo "Starting Polligen API 4290 Free Server..."
    exec /root/ai/polligenapi4290-free/polligen-venv/bin/python3 /root/ai/polligenapi4290-free/polligen-free.py
}



#=================================================================
#-------------------------- main logic ---------------------------
#=================================================================

# Main start logic
if [ "$1" = "polligenapi-4261" ]; then
    start_polligenapi_4261
elif [ "$1" = "polligenapi-4290-free" ]; then
    start_polligenapi_4290

else
    echo "Usage: $0 {polligenapi-4261|polligenapi-4290-free}"
    echo "For automatic start use systemd services"
    exit 1
fi

