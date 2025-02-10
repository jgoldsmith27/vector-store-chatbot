#!/bin/bash

# This script allows for easier application management when using it locally
# See project README.md for more details on script usage

# Function to start the backend and frontend
start_app() {
  # Start the backend in the background
  cd backend/src && python3 main.py &

  if [ "$?" -ne 0 ]; then
    echo "Unable to start the backend. Exiting..."
    echo
    exit 1
  fi

  # Start the frontend in the background
  cd frontend && npm start &

  if [ "$?" -ne 0 ]; then
    echo "Unable to start the frontend. Exiting..."
    echo
    exit 1
  fi
}

# Function to stop the backend and frontend
# Had to target local ports due to ineffectiveness using grep/pgrep
stop_app() {
  # Stop backend (Python server)
  echo "Stopping backend..."

  # Get the PID of the process using port 8080
  backend_pid=$(lsof -ti :8080)

  if [ "$?" -ne 0 ]; then
    echo "Unable to get process on port 8080. Exiting..."
    echo
    exit 1
  fi

  if [ -n "$backend_pid" ]; then
    echo "Backend running (PID: $backend_pid). Terminating..."
    kill -9 $backend_pid

    if [ "$?" -ne 0 ]; then
      echo "Unable to kill process $backend_pid. Exiting..."
      echo
      exit 1
    fi
  
  else
    echo "Backend not running."
  fi

  # Stop frontend (npm on port 3000)
  echo "Stopping frontend..."

  # Get the PID of the process using port 3000
  frontend_pid=$(lsof -ti :3000)

  if [ "$?" -ne 0 ]; then
    echo "Unable to get process(es) on port 3000. Exiting..."
    echo
    exit 1
  fi

  # Check the process command for each PID to determine if it's the frontend
  for pid in $frontend_pid; do
    process_cmd=$(ps -p $pid -o comm= | awk -F/ '{print $NF}')

    if [[ "$process_cmd" == "node" ]]; then
      echo "Frontend running (PID: $pid). Terminating..."
      kill $pid

      if [ "$?" -ne 0 ]; then
        echo "Unable to kill process $pid. Exiting..."
        echo
        exit 1
      fi
    
    else
      echo "Process $pid is not the frontend."
    fi
  done
  echo "App terminated"
}

# Function to activate the virtual environment
venv() {
  # Go to the venv parent directory and activate it
  cd backend/src && source venv/bin/activate

  if [ "$?" -ne 0 ]; then
    echo "Unable to activate the venv. Exiting..."
    echo
    exit 1
  fi

  # Install the dependencies if necessary
  if [ "$1" = "podium" ]; then
    pip3 install --break-system-packages -r requirements.txt

    if [ "$?" -ne 0 ]; then
      echo "Unable to install requirements. Exiting..."
      echo
      exit 1
    fi

    echo "Running on podium computer, using --break-system-packages"
  else
    pip install -r requirements.txt

    if [ "$?" -ne 0 ]; then
      echo "Unable to install requirements. Exiting..."
      echo
      exit 1
    fi

    echo "Running on local machine, using normal pip install"
  fi

  # Get back to main project directory for convenience
  cd ../..

  if [ "$?" -ne 0 ]; then
    echo "Unable to return to main project directory. Exiting..."
    echo
  fi
}

# Check the number of parameters received
if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Incorrect usage of managae_app.sh"
  echo "Correct usage: ./manage_app.sh <action> <optional venv specification>"
  exit 1
fi

# Start or stop the app based on user input
if [ "$1" = "start" ]; then
  start_app
elif [ "$1" = "stop" ]; then
  stop_app
elif [ "$1" = "venv" ]; then
  venv "$2"
else
  echo "Usage: $0 {start|stop|venv} {|podium}"
fi
