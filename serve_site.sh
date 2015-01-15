#!/bin/sh
# Build site locally and run

echo "Starting server..."
jekyll serve -c _config.yml,_config-dev.yml


echo "Cleaning up..."
rm -Rf _site
