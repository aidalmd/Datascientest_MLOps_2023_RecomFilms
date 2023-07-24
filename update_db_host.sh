#!/bin/bash

# Fetch the current server IP address
current_ip=$(hostname -I | awk '{print $1}')

# Save the current IP address to a new file (e.g., server_ip.txt)
echo "$current_ip" > server_ip.txt

# Fetch the SSH client IP address from the SSH_CONNECTION environment variable
ssh_client_ip=$(echo $SSH_CONNECTION | awk '{print $1}')

# Save the SSH client IP address to a new file (e.g., ssh_client_ip.txt)
echo "$ssh_client_ip" > ssh_client_ip.txt

# Update the .env file with the current IP address
sed -i "s/^DB_HOST=.*/DB_HOST=\"$current_ip\"/" .env

echo "DB_HOST updated in .env file to $current_ip"