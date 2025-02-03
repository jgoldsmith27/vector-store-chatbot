#!/bin/bash

# Function to start the backend and frontend
start_app() {
  # Start the backend in the background
  cd backend/src && python3 main.py &

  # Start the frontend in the background
  cd frontend && npm start &
}

# Function to stop the backend and frontend
# Had to target local ports due to ineffectiveness using grep/pgrep
stop_app() {
  # Stop backend (Python server)
  echo "Stopping backend..."

  # Get the PID of the process using port 8080
  backend_pid=$(lsof -ti :8080)

  if [ -n "$backend_pid" ]; then
    echo "Backend running (PID: $backend_pid). Terminating..."
    kill -9 $backend_pid
  else
    echo "Backend not running."
  fi

  # Stop frontend (npm on port 3000)
  echo "Stopping frontend..."

  # Get the PID of the process using port 3000
  frontend_pid=$(lsof -ti :3000)

  # Check the process command for each PID to determine if it's the frontend
  for pid in $frontend_pid; do
    process_cmd=$(ps -p $pid -o comm= | awk -F/ '{print $NF}')

    if [[ "$process_cmd" == "node" ]]; then
      echo "Frontend running (PID: $pid). Terminating..."
      kill $pid
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

  # Install all dependencies in the venv
  pip3 install -r requirements.txt

  # Get back to main project directory for convenience
  cd ../..
}

# Start or stop the app based on user input
if [ "$1" = "start" ]; then
  start_app
elif [ "$1" = "stop" ]; then
  stop_app
elif [ "$1" = "venv" ]; then
  venv
else
  echo "Usage: $0 {start|stop|venv}"
fi
