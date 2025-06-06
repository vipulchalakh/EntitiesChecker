#!/bin/bash

# This script is used by Vercel to install the spaCy model during build time

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Build completed successfully!"