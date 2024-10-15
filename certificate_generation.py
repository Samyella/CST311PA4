# Samuel Caesar, Kate Liu, and Ichiro Miyasato (Team 7)
# 14 October 2024
# CST 311 Programming Assignment 4
# certificate_generation.py

import subprocess
import os

# Function to write common name to a text file
def write_common_name_to_file(common_name):
    with open("common_name.txt", "w") as f:
        f.write(common_name)

# Function to add IP addresses and common name to /etc/hosts
def add_to_hosts(ip_address, common_name):
    hosts_entry = f"{ip_address} {common_name}\n"
    try:
        with open("/etc/hosts", "a") as hosts_file:
            hosts_file.write(hosts_entry)
        print(f"Added {ip_address} {common_name} to /etc/hosts")
    except PermissionError:
        print("Error: Please run the script with sudo.")

# Function to generate a private key for the server using genrsa
def generate_private_key():
    private_key_file = "server_private_key.pem"
    try:
        subprocess.run(["openssl", "genrsa", "-out", private_key_file, "2048"], check=True)
        print(f"Private key generated: {private_key_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating private key: {e}")
        
# Function to generate a Certificate Signing Request (CSR)
def generate_csr(common_name, passphrase):
    csr_file = "server.csr"
    # We enter the inputs for the common name and the challenge password here in the private key
    try:
        subprocess.run([
            "openssl", "req", "-new", "-key", "server_private_key.pem", "-out", csr_file,
            "-subj", f"/CN={common_name}",
            "-passin", f"pass:{passphrase}"
        ], check=True)
        print(f"CSR generated: {csr_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating CSR: {e}")

# Function to generate a server certificate signed by the CA
def generate_server_cert():
    server_cert_file = "chatserver-cert.pem"
    ca_cert_file = "/etc/ssl/demoCA/cacert.pem"  # CA cert path of Lab 6A
    ca_key_file = "/etc/ssl/demoCA/private/cakey.pem"   # CA key path of Lab 6A

    # Here we try to use the root cacert certificate to create an X.509 CA certificate 
    # that is valid for 365 days. We call the generated file chatserver-cert.pem 
    try:
        subprocess.run([
            "openssl", "x509", "-req", "-in", "server.csr", "-CA", ca_cert_file, "-CAkey", ca_key_file,
            "-CAcreateserial", "-out", server_cert_file, "-days", "365", "-sha256"
        ], check=True)
        print(f"Server certificate generated: {server_cert_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating server certificate: {e}")

def main():
    # Prompt user for common name and challenge password (passphrase)
    common_name = input("Enter the common name for your chat server (tpa4.chat.test): ")
    challenge_password = input("Enter a challenge password for the server private key (CST311): ")

    # The server is on host h4 so we use this IP
    ip_address = '10.0.2.2'

    # Default values for testing:
    if not common_name:
        common_name = "tpa4.chat.test"
    write_common_name_to_file(common_name)

    # Modify /etc/hosts
    add_to_hosts(ip_address, common_name)

    # Generate private key
    generate_private_key()

    # Generate CSR
    generate_csr(common_name, challenge_password)

    # Generate server certificate
    generate_server_cert()

if __name__ == "__main__":
    main()
