#!/bin/bash

# Set the path to the SSH config file on Linux
ssh_config_file="$HOME/.ssh/config"

# Check if the SSH config file exists
if [ ! -f "$ssh_config_file" ]; then
  echo "SSH config file not found: $ssh_config_file"
  exit 1
fi

# Fetch host entries from the config file and store them in ssh_client_hostname.txt
ssh_host=$(grep -E '^Host ' "$ssh_config_file" | awk '{print $2}')

# Update the .env file with the current IP address
sed -i "s/^SSH_HOSTNAME=.*/SSH_HOSTNAME=\"$ssh_host\"/" .env

echo "SSH_HOSTNAME updated in .env file to $ssh_host"