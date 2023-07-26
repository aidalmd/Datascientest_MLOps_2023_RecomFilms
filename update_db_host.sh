#!/bin/bash

# Set the path to the SSH config file on Linux
ssh_config_file="$HOME/.ssh/config"

# Check if the SSH config file exists
if [ ! -f "$ssh_config_file" ]; then
  echo "SSH config file not found: $ssh_config_file"
  exit 1
fi

# Fetch host entries from the config file and store them in ssh_client_hostname.txt
target_host=$(grep -E '^Host ' "$ssh_config_file" | awk '{print $2}')

# Update the .env file with the current IP address
sed -i "s/^DB_HOST=.*/DB_HOST=\"$target_host\"/" .env

echo "DB_HOST updated in .env file to $target_host"