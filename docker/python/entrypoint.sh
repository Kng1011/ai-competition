#!/bin/sh

# Check if DEBUG environment variable is set to "true"
if [ "$DEBUG" = "true" ]; then
    # If DEBUG is true, execute nodemon with additional arguments
    exec nodemon main.py "$@"
else
    # If DEBUG is not true, execute python with additional arguments
    exec python main.py "$@"
fi
