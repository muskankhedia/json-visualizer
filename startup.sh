#!/bin/bash

# Install Graphviz
apt-get update
apt-get install -y graphviz

# Start your application
gunicorn --bind 0.0.0.0:$PORT your_flask_app:app
